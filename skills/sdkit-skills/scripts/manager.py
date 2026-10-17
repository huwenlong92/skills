#!/usr/bin/env python3
"""Local, stdlib-only SDKit Skills catalog and safe lifecycle commands."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
MANAGER = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
LINK = re.compile(r"\]\(([^)]+)\)")
RECORD = ".sdkit-skill-install.json"


def catalog():
    return json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))


def valid_name(name):
    if not NAME.fullmatch(name):
        raise ValueError("invalid skill name")


def source(name):
    valid_name(name)
    return ROOT / "skills" / name


def check_skill(path, name):
    if not path.is_dir() or path.is_symlink():
        raise ValueError(f"missing or linked skill: {name}")
    files = list(path.rglob("*"))
    if any(p.is_symlink() for p in files):
        raise ValueError(f"symlink in skill: {name}")
    entry = path / "SKILL.md"
    if not entry.is_file():
        raise ValueError(f"missing SKILL.md: {name}")
    body = entry.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", body, re.S)
    if not match:
        raise ValueError(f"invalid frontmatter: {name}")
    fields = match.group(1).splitlines()
    if len(fields) != 2 or not fields[0].startswith("name: ") or not fields[1].startswith("description: "):
        raise ValueError(f"frontmatter must contain name and description only: {name}")
    if fields[0][6:].strip() != name or not fields[1][13:].strip():
        raise ValueError(f"frontmatter identity mismatch: {name}")
    for md in [p for p in files if p.is_file() and p.suffix == ".md"]:
        content = md.read_text(encoding="utf-8")
        for target in LINK.findall(content):
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target or re.match(r"^(https?://|mailto:|/)", target):
                continue
            resolved = (md.parent / target).resolve()
            # Source-repository documentation may link to shared root docs;
            # never accept paths outside the source repository.
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                raise ValueError(f"broken link: {md.relative_to(path)} -> {target}")
    return True


def validate(all_skills=False, name=None):
    data = catalog()
    entries = data["skills"]
    categories = set(data["categories"])
    seen = set()
    for item in entries:
        n = item["name"]
        valid_name(n)
        if n in seen or item["category"] not in categories or item["path"] != f"skills/{n}":
            raise ValueError(f"invalid catalog entry: {n}")
        seen.add(n)
    disk = {p.name for p in (ROOT / "skills").iterdir() if p.is_dir() and not p.name.startswith(".")}
    if disk != seen:
        raise ValueError(f"catalog mismatch: missing={sorted(disk-seen)} stale={sorted(seen-disk)}")
    selected = sorted(seen) if all_skills else [name]
    for n in selected:
        if n not in seen:
            raise ValueError(f"unknown skill: {n}")
        check_skill(source(n), n)
    return len(selected)


def create(name, category):
    valid_name(name)
    data = catalog()
    if category not in data["categories"]:
        raise ValueError("unknown category")
    path = source(name)
    if path.exists() or path.is_symlink() or any(s["name"] == name for s in data["skills"]):
        raise ValueError("skill already exists")
    path.mkdir()
    original_catalog = (ROOT / "catalog.json").read_bytes()
    try:
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: 待补充该 Skill 的明确任务触发条件。\n---\n\n# {name}\n\n## 执行流程\n\n待补充。\n\n## 验收\n\n待补充。\n", encoding="utf-8")
        data["skills"].append({"name": name, "category": category, "path": f"skills/{name}"})
        new_catalog = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        fd, temp_path = tempfile.mkstemp(prefix=".catalog-", dir=ROOT)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(new_catalog)
            os.replace(temp_path, ROOT / "catalog.json")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    except Exception:
        shutil.rmtree(path)
        if (ROOT / "catalog.json").read_bytes() != original_catalog:
            (ROOT / "catalog.json").write_bytes(original_catalog)
        raise


def manifest(path):
    result = {}
    for p in sorted(path.rglob("*")):
        if p.is_symlink():
            raise ValueError("symlink not allowed")
        if p.is_file():
            rel = p.relative_to(path).as_posix()
            if rel != RECORD:
                result[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def install(name, target, update=False):
    src = source(name)
    check_skill(src, name)
    target = Path(target).expanduser().absolute()
    if any(p.is_symlink() for p in (target, *target.parents)) or not target.is_dir():
        raise ValueError("target parent must exist and not be a symlink")
    dest = target / name
    if src.resolve() == dest.resolve() or src.resolve().is_relative_to(dest.resolve()) or dest.resolve().is_relative_to(src.resolve()):
        raise ValueError("source and destination overlap")
    old = None
    if dest.exists() or dest.is_symlink():
        if not update or dest.is_symlink() or not dest.is_dir():
            raise ValueError("destination exists; explicit safe update required")
        record = dest / RECORD
        if not record.is_file() or record.is_symlink():
            raise ValueError("unmanaged destination")
        old = json.loads(record.read_text(encoding="utf-8"))
        if old.get("name") != name or old.get("files") != manifest(dest):
            raise ValueError("installed skill modified")
    elif update:
        raise ValueError("cannot update missing installation")
    stage = Path(tempfile.mkdtemp(prefix=".sdkit-stage-", dir=target))
    backup = None
    try:
        shutil.rmtree(stage)
        shutil.copytree(src, stage, symlinks=True)
        hashes = manifest(stage)
        (stage / RECORD).write_text(json.dumps({"name": name, "files": hashes}, sort_keys=True) + "\n", encoding="utf-8")
        if old is not None:
            backup = Path(tempfile.mkdtemp(prefix=".sdkit-backup-", dir=target))
            backup.rmdir()
            dest.rename(backup)
        try:
            stage.rename(dest)
        except Exception:
            if backup is not None:
                backup.rename(dest)
                backup = None
            raise
    finally:
        if stage.exists():
            shutil.rmtree(stage)
        if backup is not None and backup.exists():
            shutil.rmtree(backup)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("list")
    c = sub.add_parser("create")
    c.add_argument("name")
    c.add_argument("--category", required=True)
    v = sub.add_parser("validate")
    v.add_argument("name", nargs="?")
    v.add_argument("--all", action="store_true")
    for action in ("install", "update"):
        p = sub.add_parser(action)
        p.add_argument("name")
        p.add_argument("--target", required=True)
    args = parser.parse_args()
    if args.action == "list":
        print(json.dumps(catalog()["skills"], ensure_ascii=False, indent=2))
    elif args.action == "create":
        create(args.name, args.category)
        print(f"created {args.name}")
    elif args.action == "validate":
        if not args.all and not args.name:
            parser.error("provide name or --all")
        print(f"validated {validate(args.all, args.name)} skills")
    else:
        install(args.name, args.target, update=args.action == "update")
        print(f"{args.action} completed: {args.name}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
