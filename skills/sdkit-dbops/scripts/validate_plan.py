#!/usr/bin/env python3
"""Offline plan integrity verification. Does not authorize execution."""
import argparse
import json
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("dbops_plan_for_validation", Path(__file__).with_name("plan_migrations.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
digest = module.digest
def validate(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get("planHash"),str):
        raise ValueError("invalid plan")
    expected={"apiVersion","sourceCommit","sourceHistoryFingerprint","sourceSchemaFingerprint","sourceIdentity","target","preconditions","state","decision","safetyGate","safetyEvidenceFingerprint","steps","executionAuthorized","planHash"}
    if set(doc) != expected or doc.get("apiVersion") != "sdkit.dev/migration-plan/v1":
        raise ValueError("invalid plan structure")
    if doc.get("decision") not in ("candidate", "requires_approval", "blocked") or not isinstance(doc.get("steps"), list):
        raise ValueError("invalid plan decision")
    body={k:v for k,v in doc.items() if k!="planHash"}
    if doc["planHash"]!=digest(body):
        raise ValueError("plan hash mismatch")
    if not isinstance(doc.get("safetyGate"), dict) or doc["safetyGate"].get("status") != "blocked" or doc.get("decision") != "blocked":
        raise ValueError("untrusted safety decision")
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
