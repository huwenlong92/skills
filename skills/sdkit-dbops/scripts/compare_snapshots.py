#!/usr/bin/env python3
"""Compare sanitized JSON snapshots without database access."""
import argparse
import hashlib
import json
from pathlib import Path

KEYS = ("dialect", "databaseVersion", "normalizerVersion", "scope", "coverage")
KINDS = {"table", "column", "index", "constraint", "sequence", "view"}
DIALECTS = {"postgres", "mysql", "oracle", "sqlite"}

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def normalize(doc):
    if not isinstance(doc, dict) or any(k not in doc for k in (*KEYS, "objects")):
        raise ValueError("missing snapshot fields")
    if set(doc) != set((*KEYS, "objects")):
        raise ValueError("unknown snapshot fields")
    if doc["dialect"] not in DIALECTS or not isinstance(doc["objects"], list):
        raise ValueError("invalid dialect or objects")
    if not all(isinstance(doc[k], str) and doc[k] for k in ("databaseVersion", "normalizerVersion")):
        raise ValueError("invalid version")
    scope = doc["scope"]
    if not isinstance(scope, list) or not scope or not all(isinstance(s, str) and s for s in scope) or len(scope) != len(set(scope)):
        raise ValueError("invalid scope")
    cov = doc["coverage"]
    if not isinstance(cov, dict) or cov.get("complete") is not True or not isinstance(cov.get("kinds"), list) or not cov["kinds"]:
        raise ValueError("incomplete coverage")
    if set(cov) != {"complete", "kinds"}:
        raise ValueError("unknown coverage fields")
    if not set(cov["kinds"]).issubset(KINDS) or len(cov["kinds"]) != len(set(cov["kinds"])):
        raise ValueError("invalid coverage")
    seen = set()
    objects = []
    for obj in doc["objects"]:
        if not isinstance(obj, dict) or not all(isinstance(obj.get(k), str) for k in ("kind", "schema", "name")):
            raise ValueError("invalid object")
        if set(obj) - {"kind", "schema", "name", "attributes"}:
            raise ValueError("unknown object fields")
        if "attributes" in obj and (not isinstance(obj["attributes"], dict) or not all(isinstance(k, str) for k in obj["attributes"])):
            raise ValueError("invalid attributes")
        if not obj["name"] or obj["kind"] not in cov["kinds"] or obj["schema"] not in scope:
            raise ValueError("object outside coverage")
        ident = (obj["kind"], obj["schema"], obj["name"])
        if ident in seen:
            raise ValueError("duplicate object")
        seen.add(ident)
        objects.append(obj)
    try:
        canonical(objects)
    except (ValueError, TypeError) as exc:
        raise ValueError("non-finite or invalid object attributes") from exc
    result = {k: doc[k] for k in KEYS}
    result["scope"] = sorted(scope)
    result["coverage"] = {"complete": True, "kinds": sorted(cov["kinds"])}
    result["objects"] = sorted(objects, key=lambda x: (x["kind"], x["schema"], x["name"]))
    return result

def fingerprint(doc):
    return hashlib.sha256(canonical(normalize(doc)).encode("utf-8")).hexdigest()

def compare(left, right):
    try:
        a, b = normalize(left), normalize(right)
        for key in KEYS:
            if a[key] != b[key]:
                return {"status": "unknown", "reason": "incompatible " + key}
        l = {(o["kind"], o["schema"], o["name"]): o for o in a["objects"]}
        r = {(o["kind"], o["schema"], o["name"]): o for o in b["objects"]}
        added, removed = sorted(r.keys()-l.keys()), sorted(l.keys()-r.keys())
        changed = sorted(k for k in l.keys() & r.keys() if canonical(l[k]) != canonical(r[k]))
        return {"status": "drift" if added or removed or changed else "equal",
                "leftFingerprint": fingerprint(left), "rightFingerprint": fingerprint(right),
                "added": [list(x) for x in added], "removed": [list(x) for x in removed], "changed": [list(x) for x in changed]}
    except (ValueError, TypeError) as exc:
        return {"status": "unknown", "reason": str(exc)}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("left")
    p.add_argument("right")
    args = p.parse_args()
    try:
        result = compare(json.loads(Path(args.left).read_text(encoding="utf-8")), json.loads(Path(args.right).read_text(encoding="utf-8")))
        print(canonical(result))
        return {"equal": 0, "drift": 1, "unknown": 2}[result["status"]]
    except (OSError, ValueError) as exc:
        print(canonical({"status": "unknown", "reason": str(exc)}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
