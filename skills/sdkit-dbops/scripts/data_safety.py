#!/usr/bin/env python3
"""Conservative offline data-loss risk classification; not a SQL parser."""
import re

DESTRUCTIVE = re.compile(r"\b(?:TRUNCATE|DROP\s+(?:TABLE|SCHEMA|DATABASE)|DELETE\s+FROM)\b", re.I)
WRITE = re.compile(r"\b(?:UPDATE|REPLACE\s+INTO|INSERT\s+OVERWRITE|MERGE\s+INTO)\b", re.I)
INDIRECT = re.compile(r"\b(?:EXEC(?:UTE)?|CALL|DO|SEED|AUTOMIGRATE|REBUILD|RECREATE)\b", re.I)
PROTECTED = re.compile(r"\b(?:system|system_data)\b", re.I)

def assess(operations):
    if not isinstance(operations, list):
        raise ValueError("operations must be an array")
    if not operations:
        return {"status": "unknown", "risk": "unknown", "reasons": ["no operation evidence"], "executionAuthorized": False}
    reasons = []
    for op in operations:
        if not isinstance(op, dict) or set(op) != {"kind", "text"} or not all(isinstance(op[k], str) and op[k] for k in ("kind", "text")):
            raise ValueError("invalid operation evidence")
        kind, sql = op["kind"].lower(), op["text"]
        if kind not in {"sql", "seed", "orm", "script"}:
            raise ValueError("unknown operation kind")
        if kind != "sql" or INDIRECT.search(sql):
            reasons.append("indirect or dynamic operation requires review")
        if PROTECTED.search(sql):
            reasons.append("protected schema reference")
        if DESTRUCTIVE.search(sql):
            reasons.append("destructive SQL candidate")
        if WRITE.search(sql):
            reasons.append("data mutation candidate")
        if not (DESTRUCTIVE.search(sql) or WRITE.search(sql) or INDIRECT.search(sql)) and kind == "sql":
            reasons.append("unparsed SQL cannot prove read-only")
    return {"status": "blocked", "risk": "destructive" if any("destructive" in r or "protected" in r for r in reasons) else "unknown", "reasons": sorted(set(reasons)), "executionAuthorized": False}
