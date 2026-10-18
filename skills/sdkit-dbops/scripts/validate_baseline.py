#!/usr/bin/env python3
"""Validate a sanitized baseline descriptor without database access."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[a-f0-9]{64}$")
DIALECTS = {"postgres", "mysql", "oracle", "sqlite"}
FIELDS = {"baselineId", "dialect", "scope", "schemaFingerprint", "normalizerVersion", "checksum"}

def validate(doc):
    if not isinstance(doc, dict) or set(doc) != FIELDS:
        raise ValueError("invalid baseline fields")
    if not isinstance(doc["baselineId"], str) or not doc["baselineId"]:
        raise ValueError("invalid baseline id")
    if doc["dialect"] not in DIALECTS:
        raise ValueError("invalid dialect")
    scope = doc["scope"]
    if not isinstance(scope, list) or not scope or not all(isinstance(x, str) and x for x in scope) or len(set(scope)) != len(scope):
        raise ValueError("invalid scope")
    if not isinstance(doc["normalizerVersion"], str) or not doc["normalizerVersion"]:
        raise ValueError("invalid normalizer version")
    if not SHA.fullmatch(str(doc["schemaFingerprint"])) or not SHA.fullmatch(str(doc["checksum"])):
        raise ValueError("invalid checksum or fingerprint")
    return {"status": "valid", "baselineId": doc["baselineId"], "adopted": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    try:
        result = validate(json.loads(Path(args.path).read_text(encoding="utf-8")))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, sort_keys=True))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
