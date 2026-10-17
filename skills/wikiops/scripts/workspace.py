#!/usr/bin/env python3
"""WikiOps Workspace V1 local configuration helper (stdlib only)."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

DEFAULT_PATH = Path.home() / ".config" / "sdkit" / "skills" / "wikiops" / "config.json"

def git(*args, cwd):
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git operation failed")
    return result.stdout.strip()

def canonical(url):
    url = url.strip()
    if "://" in url:
        parsed = urlparse(url)
        host, path = parsed.hostname, parsed.path
    elif "@" in url and ":" in url.split("@", 1)[1]:
        host, path = url.split("@", 1)[1].split(":", 1)
    else:
        raise ValueError("Repository URL must be a full SSH or HTTPS Git URL")
    if not host or not path.strip("/"):
        raise ValueError("Invalid Git remote URL")
    if "://" in url and parsed.scheme not in ("ssh", "https"):
        raise ValueError("Invalid Git remote URL")
    return host.lower(), path.strip("/").removesuffix(".git").lower()

def load(path):
    if not path.exists():
        raise ValueError("No user config; run init first")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("Invalid user configuration") from exc
    if data.get("version") != 1 or not isinstance(data.get("workspaces"), dict):
        raise ValueError("Unsupported configuration")
    return data

def main():
    parser = argparse.ArgumentParser(description="WikiOps local workspace helper")
    parser.add_argument("--config", type=Path, default=DEFAULT_PATH)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    add = sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("url")
    add.add_argument("--provider", choices=["github", "gitlab", "gitee", "git"], required=True)
    add.add_argument("--path", type=Path)
    add.add_argument("--primary", action="store_true")
    sub.add_parser("list")
    check = sub.add_parser("resolve")
    check.add_argument("name", nargs="?")
    args = parser.parse_args()
    path = args.config.expanduser()
    if args.command == "init":
        if path.exists():
            print(f"Existing config preserved: {path}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": 1, "primary_workspace": None, "workspaces": {}}, indent=2) + "\n", encoding="utf-8")
        os.chmod(path, 0o600)
        print(f"Initialized: {path}")
        return
    data = load(path)
    if args.command == "add":
        canonical(args.url)
        if not args.name.strip() or "/" in args.name or "\\" in args.name:
            raise ValueError("Invalid workspace name")
        if args.name in data["workspaces"]:
            raise ValueError("Workspace already exists; no implicit overwrite")
        repo = {"provider": args.provider, "url": args.url, "local_path": str(args.path.expanduser().resolve()) if args.path else None}
        data["workspaces"][args.name] = {"repository": repo}
        if args.primary or data["primary_workspace"] is None:
            data["primary_workspace"] = args.name
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.chmod(path, 0o600)
        print(f"Added workspace: {args.name}")
        return
    if args.command == "list":
        print(json.dumps({"primary_workspace": data["primary_workspace"], "workspaces": list(data["workspaces"])}, ensure_ascii=False, indent=2))
        return
    name = args.name or data["primary_workspace"]
    if not name or name not in data["workspaces"]:
        raise ValueError("Workspace not found; bind a workspace first")
    repo = data["workspaces"][name]["repository"]
    candidates = [Path.cwd()]
    if repo.get("local_path"):
        candidates.append(Path(repo["local_path"]).expanduser())
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            root = Path(git("rev-parse", "--show-toplevel", cwd=candidate))
            remotes = git("remote", "-v", cwd=root).splitlines()
            urls = [parts[1] for line in remotes if (parts := line.split()) and len(parts) >= 3 and parts[0] == "origin" and parts[2] == "(fetch)"]
            if any(canonical(u) == canonical(repo["url"]) for u in urls):
                print(json.dumps({"workspace": name, "mode": "local", "path": str(root), "branch": git("branch", "--show-current", cwd=root), "dirty": bool(git("status", "--porcelain", cwd=root))}))
                return
            if repo.get("local_path") and candidate == Path(repo["local_path"]).expanduser():
                raise ValueError("Configured local repository remote does not match workspace")
        except (ValueError, OSError) as exc:
            if repo.get("local_path") and candidate == Path(repo["local_path"]).expanduser() and candidate.exists():
                raise ValueError("Configured local repository invalid or mismatched") from exc
            continue
    print(json.dumps({"workspace": name, "mode": "remote", "provider": repo["provider"], "url": repo["url"], "authorized": False}))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
