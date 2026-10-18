#!/usr/bin/env python3
"""Offline plan integrity verification. Does not authorize execution."""
import argparse
import json
from pathlib import Path
from plan_migrations import digest
def validate(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get("planHash"),str):
        raise ValueError("invalid plan")
    body={k:v for k,v in doc.items() if k!="planHash"}
    if doc["planHash"]!=digest(body):
        raise ValueError("plan hash mismatch")
    if doc.get("executionAuthorized") is not False:
        raise ValueError("execution must not be authorized")
    return {"status":"valid","executionAuthorized":False}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("path")
    a=p.parse_args()
    try:
        print(json.dumps(validate(json.loads(Path(a.path).read_text(encoding="utf-8"))),sort_keys=True))
        return 0
    except (OSError,ValueError,TypeError) as e:
        print(json.dumps({"status":"blocked","reason":str(e)},sort_keys=True))
        return 2
if __name__=="__main__":
    raise SystemExit(main())
