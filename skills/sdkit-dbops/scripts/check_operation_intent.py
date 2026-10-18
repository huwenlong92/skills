#!/usr/bin/env python3
"""Offline intent gate. No database, network, signing, or execution."""
import argparse
import json
import re
from pathlib import Path

SHA = re.compile(r"^[a-f0-9]{64}\Z")
RISKS = {"read_only", "additive", "structural", "destructive", "unknown"}
ENVIRONMENTS = {"local", "shared_dev", "staging", "production"}
DANGEROUS = {"drop", "truncate", "delete", "overwrite", "reset", "rebuild"}
OPERATIONS = {"select", "inspect", "create", "alter", "add_column", "create_index", "drop", "truncate", "delete", "update", "insert", "merge", "overwrite", "reset", "rebuild", "migrate", "seed", "backfill", "restore", "bootstrap"}

def validate(value):
    if not isinstance(value, dict) or set(value) != {"environment", "target", "operations", "planHash", "approval", "backup"}:
        raise ValueError("invalid intent fields")
    if not isinstance(value["environment"], str) or value["environment"] not in ENVIRONMENTS:
        raise ValueError("unknown environment")
    target = value["target"]
    if not isinstance(target, dict) or set(target) != {"instanceId", "databaseId", "scope"}:
        raise ValueError("invalid target")
    if any(not isinstance(target[k], str) or not target[k] for k in ("instanceId", "databaseId")):
        raise ValueError("invalid target identity")
    if not isinstance(target["scope"], list) or not target["scope"] or any(not isinstance(x, str) or not x for x in target["scope"]) or len(set(target["scope"])) != len(target["scope"]):
        raise ValueError("invalid target scope")
    if not isinstance(value["planHash"], str) or not SHA.fullmatch(value["planHash"]):
        raise ValueError("invalid plan hash")
    ops = value["operations"]
    if not isinstance(ops, list) or not ops:
        raise ValueError("missing operations")
    for op in ops:
        if not isinstance(op, dict) or set(op) != {"type", "risk", "objects"}:
            raise ValueError("invalid operation")
        if not isinstance(op["type"], str) or op["type"].lower() not in OPERATIONS or not isinstance(op["risk"], str) or op["risk"] not in RISKS:
            raise ValueError("invalid operation classification")
        if not isinstance(op["objects"], list) or not op["objects"] or any(not isinstance(x, str) or not x for x in op["objects"]):
            raise ValueError("invalid affected objects")
        if any(obj.count(".") != 1 or not all(obj.split(".")) or obj.split(".", 1)[0] not in target["scope"] for obj in op["objects"]):
            raise ValueError("operation object outside declared scope")
    for key in ("approval", "backup"):
        if not isinstance(value[key], dict):
            raise ValueError("invalid evidence")
    reasons = ["offline evidence cannot authorize execution"]
    if value["environment"] == "production":
        reasons.append("production execution remains prohibited by current skill rules")
    if any(op["type"].lower() in DANGEROUS or op["risk"] in {"destructive", "unknown"} for op in ops):
        reasons.append("destructive or unknown operation requires independent high-risk approval")
    if any(x.split(".", 1)[0] in {"system", "system_data"} for op in ops for x in op["objects"]):
        reasons.append("protected infrastructure object")
    return {"status": "blocked", "executionAuthorized": False, "reasons": reasons}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("intent")
    args = p.parse_args()
    try:
        def reject_constant(value):
            raise ValueError("nonfinite JSON: " + value)
        data = json.loads(Path(args.intent).read_text(encoding="utf-8"), parse_constant=reject_constant)
        print(json.dumps(validate(data), ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"status": "blocked", "executionAuthorized": False, "reason": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
