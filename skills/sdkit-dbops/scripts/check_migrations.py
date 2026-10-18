#!/usr/bin/env python3
"""Offline, read-only SQL migration checker. Python standard library only."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
from datetime import datetime

NAME = re.compile(r"^\d{8}T\d{6}Z_[a-f0-9]{6,16}_[a-z][a-z0-9_]*\.sql$")
RISK = re.compile(r"\b(DROP|TRUNCATE|ALTER|DELETE|UPDATE|INSERT|GRANT|REVOKE|EXEC|EXECUTE|CALL|CREATE)\b", re.I)
DIALECTS = {"postgres", "mysql", "oracle", "sqlite"}

def inspect(root, dialect, layout):
    if dialect not in DIALECTS or layout not in ("single", "multi"):
        raise ValueError("unsupported dialect or layout")
    base = root / "database"
    folder = base / "migrations" if layout == "single" else base / dialect / "migrations"
    if base.is_symlink() or (layout == "multi" and (base / dialect).is_symlink()):
        raise ValueError("symlink in migration path")
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError("migration directory missing or symlink")
    entries = []
    names = set()
    for p in sorted(folder.iterdir()):
        if p.is_symlink() or not p.is_file() or p.suffix != ".sql":
            raise ValueError("unexpected entry in migration directory")
        if not NAME.fullmatch(p.name):
            raise ValueError("invalid migration filename: " + p.name)
        mid = p.stem
        try:
            datetime.strptime(mid[:16], "%Y%m%dT%H%M%SZ")
        except ValueError as exc:
            raise ValueError("invalid UTC migration timestamp: " + p.name) from exc
        if mid in names:
            raise ValueError("duplicate migration id: " + mid)
        names.add(mid)
        data = p.read_bytes()
        try:
            sql = data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("migration must be UTF-8: " + p.name)
        flags = sorted(set(x.upper() for x in RISK.findall(sql)))
        entries.append({"id": mid, "dialect": dialect, "path": p.relative_to(root).as_posix(),
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "reviewRequired": True, "riskTokens": flags})
    if layout == "multi":
        for other in sorted(DIALECTS - {dialect}):
            other_root = base / other
            sibling = other_root / "migrations"
            if other_root.is_symlink() or sibling.is_symlink():
                raise ValueError("symlink in sibling migration path")
            if sibling.is_dir():
                for candidate in sibling.iterdir():
                    if candidate.is_symlink():
                        raise ValueError("symlink in sibling migration file: " + candidate.name)
                    if candidate.is_file() and candidate.suffix == ".sql" and candidate.stem in names:
                        raise ValueError("cross-dialect migration id collision: " + candidate.stem)
    return {"status": "review_required" if entries else "empty", "dialect": dialect,
            "migrations": entries, "databaseConnected": False}

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dialect", required=True, choices=sorted(DIALECTS))
    ap.add_argument("--layout", default="single", choices=["single", "multi"])
    args = ap.parse_args(argv)
    try:
        result = inspect(pathlib.Path(args.root).resolve(), args.dialect, args.layout)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "databaseConnected": False}, ensure_ascii=False))
        return 2

if __name__ == "__main__":
    sys.exit(main())
