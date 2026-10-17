#!/usr/bin/env python3
"""Foundry Workspace configuration and local-first repository resolver (stdlib only)."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = Path.home() / ".config" / "sdkit" / "skills" / "foundry" / "config.json"
DEFAULTS_FILE = ROOT / "config" / "defaults.yaml"

def canonical(url):
    if not isinstance(url, str):
        raise ValueError("Invalid Git URL")
    if "://" in url:
        parsed = urlparse(url)
        if parsed.scheme not in ("ssh", "https") or parsed.password:
            raise ValueError("Unsupported or unsafe Git URL")
        host, path = parsed.hostname, parsed.path
    else:
        match = re.fullmatch(r"git@([^:/\s]+):([^\s]+)", url)
        if not match:
            raise ValueError("Expected SSH or HTTPS Git URL")
        host, path = match.groups()
    path = (path or "").strip("/").removesuffix(".git")
    if not host or not path or ".." in path.split("/"):
        raise ValueError("Invalid Git URL")
    return host.lower(), path.lower()

def validate(data):
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Unsupported configuration version")
    spaces = data.get("workspaces")
    if not isinstance(spaces, dict):
        raise ValueError("Invalid workspaces")
    primary = data.get("primary_workspace")
    if primary is not None and primary not in spaces:
        raise ValueError("Primary workspace does not exist")
    for name, workspace in spaces.items():
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
            raise ValueError("Invalid workspace name")
        if not isinstance(workspace, dict) or not isinstance(workspace.get("repository"), dict):
            raise ValueError("Invalid repository")
        repo = workspace["repository"]
        if repo.get("provider") not in ("github", "gitlab", "gitee", "git"):
            raise ValueError("Invalid provider")
        canonical(repo.get("url"))
        if repo.get("local_path") is not None and (not isinstance(repo["local_path"], str) or not repo["local_path"].strip()):
            raise ValueError("Invalid local_path")
    return data

def read_defaults():
    """Parse the narrow Foundry defaults.yaml mapping using stdlib."""
    content = DEFAULTS_FILE.read_text(encoding="utf-8")
    def field(name):
        match = re.search(r"^\s*" + re.escape(name) + r":\s*(.+?)\s*$", content, re.M)
        if not match:
            raise ValueError("Missing defaults field: " + name)
        return match.group(1).strip().strip(chr(34)).strip(chr(39))
    primary = field("primary_workspace")
    workspace_match = re.search(r"^  ([A-Za-z0-9_-]+):\s*$", content, re.M)
    if not workspace_match or workspace_match.group(1) != primary:
        raise ValueError("Invalid defaults workspace")
    return validate({"version": int(field("version")), "primary_workspace": primary,
        "workspaces": {primary: {"repository": {"provider": field("provider"), "url": field("url"),
        "local_path": None if field("local_path") == "null" else field("local_path")}}}})

def load(path):
    if not path.exists():
        return read_defaults(), "skill-default"
    try:
        return validate(json.loads(path.read_text(encoding="utf-8"))), "user"
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("Invalid JSON configuration") from exc

def save(path, data):
    validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            os.chmod(tmp, 0o600)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()

def git(cwd, *args):
    result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git operation failed")
    return result.stdout.strip()

def resolve(data, name, cwd):
    name = name or data["primary_workspace"]
    if not name or name not in data["workspaces"]:
        raise ValueError("Workspace not bound")
    repo = data["workspaces"][name]["repository"]
    expected = canonical(repo["url"])
    candidates = [Path(cwd)]
    configured = Path(repo["local_path"]).expanduser().resolve() if repo.get("local_path") else None
    if configured and configured not in candidates:
        candidates.append(configured)
    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            root = Path(git(candidate, "rev-parse", "--show-toplevel")).resolve()
            remote = git(root, "remote", "get-url", "origin")
            if canonical(remote) != expected:
                if configured and candidate == configured:
                    raise ValueError("Configured local repository identity mismatch")
                continue
            try:
                branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
            except ValueError:
                branch = None
        except ValueError as exc:
            if configured and candidate == configured:
                raise ValueError("Configured local repository invalid or mismatched") from exc
            continue
        dirty = bool(git(root, "status", "--porcelain"))
        result = {"workspace": name, "mode": "local", "path": str(root), "branch": branch, "dirty": dirty, "provider": repo["provider"], "url": repo["url"], "identity_verified": True}
        try:
            upstream = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
            counts = git(root, "rev-list", "--left-right", "--count", f"{upstream}...HEAD").split()
            result["upstream"] = upstream
            result["behind"], result["ahead"] = map(int, counts)
        except ValueError:
            result["upstream"] = None
            result["ahead"] = None
            result["behind"] = None
        return result
    if configured and configured.exists():
        raise ValueError("Configured local repository cannot be used")
    return {"workspace": name, "mode": "remote", "provider": repo["provider"], "url": repo["url"], "authorized": False, "identity_verified": False}

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_PATH)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("list")
    add = sub.add_parser("add")
    add.add_argument("name")
    add.add_argument("url")
    add.add_argument("--provider", required=True, choices=["github", "gitlab", "gitee", "git"])
    add.add_argument("--path")
    add.add_argument("--primary", action="store_true")
    primary = sub.add_parser("set-primary")
    primary.add_argument("name")
    local = sub.add_parser("set-path")
    local.add_argument("name")
    local.add_argument("path")
    remove = sub.add_parser("remove")
    remove.add_argument("name")
    check = sub.add_parser("resolve")
    check.add_argument("name", nargs="?")
    check.add_argument("--active")
    args = parser.parse_args(argv)
    path = args.config.expanduser()
    if args.command == "init":
        if path.exists():
            print("Existing configuration preserved")
            return
        save(path, {"version": 1, "primary_workspace": None, "workspaces": {}})
        print(f"Initialized {path}")
        return
    data, source = load(path)
    if args.command == "list":
        print(json.dumps({"source": source, **data}, ensure_ascii=False))
        return
    if args.command == "resolve":
        result = resolve(data, args.name or args.active, Path.cwd())
        result["config_source"] = source
        print(json.dumps(result, ensure_ascii=False))
        return
    if source == "skill-default":
        raise ValueError("Initialize user configuration before changing workspaces")
    if args.command == "add":
        if args.name in data["workspaces"]:
            raise ValueError("Workspace already exists")
        data["workspaces"][args.name] = {"repository": {"provider": args.provider, "url": args.url, "local_path": str(Path(args.path).expanduser().resolve()) if args.path else None}}
        if args.primary or data["primary_workspace"] is None:
            data["primary_workspace"] = args.name
    elif args.command == "set-primary":
        if args.name not in data["workspaces"]:
            raise ValueError("Unknown workspace")
        data["primary_workspace"] = args.name
    elif args.command == "set-path":
        if args.name not in data["workspaces"]:
            raise ValueError("Unknown workspace")
        data["workspaces"][args.name]["repository"]["local_path"] = str(Path(args.path).expanduser().resolve())
    elif args.command == "remove":
        if args.name not in data["workspaces"]:
            raise ValueError("Unknown workspace")
        del data["workspaces"][args.name]
        if data["primary_workspace"] == args.name:
            data["primary_workspace"] = None
    save(path, data)
    print(json.dumps({"primary_workspace": data["primary_workspace"], "workspaces": list(data["workspaces"])}, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
