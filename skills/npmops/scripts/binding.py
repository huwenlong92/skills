#!/usr/bin/env python3
"""Read a private local-directory/Git-URL binding and verify it without writing Git state."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

SKILL_NAME = "npmops"


def canonical(url):
    if not isinstance(url, str) or not url or any(c.isspace() for c in url):
        raise ValueError("Invalid repository URL")
    port = None
    if "://" in url:
        parsed = urlsplit(url)
        if (parsed.scheme not in ("https", "ssh") or parsed.password is not None
                or parsed.query or parsed.fragment or (parsed.scheme == "https" and parsed.username)):
            raise ValueError("Expected a credential-free SSH or HTTPS repository URL")
        host, path = parsed.hostname, parsed.path
        port = parsed.port
        if port == {"https": 443, "ssh": 22}[parsed.scheme]:
            port = None
    else:
        match = re.fullmatch(r"git@([^:/\s]+):([^\s]+)", url)
        if not match:
            raise ValueError("Expected an SSH or HTTPS repository URL")
        host, path = match.groups()
    path = path.strip("/").removesuffix(".git")
    if not host or not path or any(p in ("", ".", "..") for p in path.split("/")):
        raise ValueError("Invalid repository identity")
    # GitHub paths are case-insensitive; generic Git servers may distinguish case.
    return host.lower(), port, path.lower() if host.lower() == "github.com" else path


def load(config):
    data = json.loads(config.read_text(encoding="utf-8"))
    repo = data.get("repository") if isinstance(data, dict) else None
    if not isinstance(repo, dict):
        raise ValueError("Configuration requires repository.url and repository.local_path")
    canonical(repo.get("url"))
    value = repo.get("local_path")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Configuration requires a nonempty repository.local_path")
    path = Path(value).expanduser()
    return repo["url"], (path if path.is_absolute() else config.parent / path).resolve()


def git(path, *args):
    result = subprocess.run(["git", "-C", str(path), *args], text=True, capture_output=True)
    if result.returncode:
        raise ValueError("Git check failed: " + args[0])
    return result.stdout.strip()


def verify(path, url):
    expected = canonical(url)
    path = Path(path).expanduser().resolve()
    if not path.is_dir():
        raise ValueError("Bound local directory is not accessible")
    root = Path(git(path, "rev-parse", "--show-toplevel")).resolve()
    fetch = git(root, "remote", "get-url", "--all", "origin").splitlines()
    push = git(root, "remote", "get-url", "--push", "--all", "origin").splitlines()
    if not fetch or not push or any(canonical(u) != expected for u in fetch + push):
        raise ValueError("origin Fetch/Push identity does not match the configured repository")
    try:
        branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    except ValueError:
        branch = None
    try:
        upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        behind, ahead = map(int, git(root, "rev-list", "--left-right", "--count", f"{upstream}...HEAD").split())
    except ValueError:
        upstream, behind, ahead = None, None, None
    return {"local_path": str(path), "git_root": str(root), "url": url,
            "identity_verified": True, "fetch_push_verified": True, "branch": branch,
            "dirty": bool(git(root, "status", "--porcelain")), "upstream": upstream,
            "ahead": ahead, "behind": behind, "fresh_remote_check": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path,
                        default=Path.home() / ".config" / "sdkit" / "skills" / SKILL_NAME / "config.json")
    parser.add_argument("--path", type=Path, help="explicit package source directory; requires --url")
    parser.add_argument("--url", help="expected remote URL for this package; requires --path")
    args = parser.parse_args()
    try:
        if (args.path is None) != (args.url is None):
            raise ValueError("Supply --path and --url together")
        if args.path is not None:
            url, path = args.url, args.path
        else:
            url, path = load(args.config.expanduser().resolve())
        print(json.dumps(verify(path, url), ensure_ascii=False))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "identity_verified": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
