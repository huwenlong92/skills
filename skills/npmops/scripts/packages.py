#!/usr/bin/env python3
"""Create and find package directories under the user's configured packages_root."""
import argparse
import json
from pathlib import Path
import re
import sys


def configured_root(config):
    data = json.loads(config.read_text(encoding="utf-8"))
    value = data.get("packages_root") if isinstance(data, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Configuration requires a nonempty packages_root")
    root = Path(value).expanduser()
    root = (root if root.is_absolute() else config.parent / root).resolve()
    if not root.is_dir():
        raise ValueError("Configured packages_root is not an accessible directory")
    return root


def create(root, directory):
    if directory == "node_modules" or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", directory):
        raise ValueError("Use a single lowercase directory name, without a scope or path separators")
    target = root / directory
    # mkdir without exist_ok protects existing directories, files and dangling symlinks.
    target.mkdir()
    return {"directory": directory, "path": str(target), "created": True,
            "package_initialized": False}


def catalogue(root, query=""):
    entries, issues = [], []
    for path in sorted(root.iterdir()):
        # A discovery command must not wander into other repositories through links.
        if path.is_symlink() or not path.is_dir() or path.name.startswith(".") or path.name == "node_modules":
            continue
        entry = {"directory": path.name, "path": str(path), "package_name": None,
                 "package_initialized": False}
        manifest = path / "package.json"
        if manifest.is_symlink():
            issues.append({"directory": path.name, "error": "package.json symlink is not read"})
        elif manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not data["name"].strip():
                    raise ValueError("package.json must declare a package name")
                entry["package_name"] = data["name"]
                entry["package_initialized"] = True
            except (OSError, ValueError) as error:
                issues.append({"directory": path.name, "error": str(error)})
        haystack = path.name + " " + (entry["package_name"] or "")
        if query.casefold() in haystack.casefold():
            entries.append(entry)
    return entries, issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path,
                        default=Path.home() / ".config/sdkit/skills/npmops/config.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("root", help="show the configured parent directory")
    commands.add_parser("list", help="list direct package directories")
    find = commands.add_parser("find", help="find directories by directory or package name")
    find.add_argument("query")
    new = commands.add_parser("create", help="create an empty package directory; does not initialize or publish a package")
    new.add_argument("directory")
    args = parser.parse_args()
    try:
        root = configured_root(args.config.expanduser().resolve())
        result = {"packages_root": str(root)}
        if args.command == "create":
            result.update(create(root, args.directory))
        elif args.command in ("list", "find"):
            if args.command == "find" and not args.query.strip():
                raise ValueError("Find query must not be empty")
            result["packages"], result["issues"] = catalogue(root, args.query if args.command == "find" else "")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
