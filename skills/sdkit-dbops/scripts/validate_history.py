#!/usr/bin/env python3
"""Validate offline Migration History JSON."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

MID = re.compile(r"^\d{8}T\d{6}Z_[a-f0-9]{6,16}_[a-z][a-z0-9_]*$")
SHA = re.compile(r"^[a-f0-9]{64}$")

def validate(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("migrations"), list):
        raise ValueError("invalid history")
    if set(doc) - {"migrations", "attempts"}:
        raise ValueError("unknown history fields")
    seen = set()
    for m in doc["migrations"]:
        if not isinstance(m, dict) or not MID.fullmatch(str(m.get("migrationId", ""))) or not SHA.fullmatch(str(m.get("checksum", ""))):
            raise ValueError("invalid migration")
        try:
            datetime.strptime(m["migrationId"][:16], "%Y%m%dT%H%M%SZ")
        except ValueError as exc:
            raise ValueError("invalid timestamp") from exc
        if set(m) - {"migrationId", "checksum", "status"}:
            raise ValueError("unknown migration fields")
        if m.get("status") != "applied" or m["migrationId"] in seen:
            raise ValueError("unresolved or duplicate migration")
        seen.add(m["migrationId"])
    attempts = doc.get("attempts", [])
    if not isinstance(attempts, list) or any(not isinstance(a, dict) or a.get("status") != "applied" for a in attempts):
        raise ValueError("unresolved attempts")
    if any(set(a) - {"status"} for a in attempts):
        raise ValueError("unknown attempt fields")
    return {"status": "valid", "count": len(seen)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    args = p.parse_args()
    try:
        print(json.dumps(validate(json.loads(Path(args.path).read_text(encoding="utf-8"))), sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, sort_keys=True))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
