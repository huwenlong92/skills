#!/usr/bin/env python3
"""Offline, fail-closed migration planning; no database connections."""
import argparse
import hashlib
import json
from pathlib import Path

SHA = __import__("re").compile(r"^[0-9a-f]{64}$")
def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()
def history_map(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("migrations"), list):
        raise ValueError("invalid history")
    out = {}
    for m in doc["migrations"]:
        if not isinstance(m, dict) or not isinstance(m.get("migrationId"), str) or not isinstance(m.get("checksum"), str) or not SHA.fullmatch(m["checksum"]) or m.get("status") != "applied":
            raise ValueError("invalid migration record")
        if m["migrationId"] in out:
            raise ValueError("duplicate migration")
        out[m["migrationId"]] = m["checksum"]
    if any(not isinstance(a, dict) or a.get("status") != "applied" for a in doc.get("attempts", [])):
        raise ValueError("unresolved attempt")
    return out
def plan(source, target):
    for obj in (source, target):
        if not isinstance(obj, dict) or set(obj) != {"identity", "history", "snapshotFingerprint", "normalizerVersion", "evidence"}:
            raise ValueError("missing or unexpected evidence fields")
        ident = obj["identity"]
        if not isinstance(ident, dict) or set(ident) != {"environmentId", "databaseId", "dialect", "databaseVersion", "scope"}:
            raise ValueError("invalid database identity")
        if not isinstance(ident["scope"], list) or not ident["scope"] or any(not isinstance(x,str) or not x for x in ident["scope"]):
            raise ValueError("invalid scope")
        if not isinstance(obj["snapshotFingerprint"],str) or not SHA.fullmatch(obj["snapshotFingerprint"]):
            raise ValueError("invalid snapshot fingerprint")
        if not isinstance(obj["normalizerVersion"],str) or not obj["normalizerVersion"]:
            raise ValueError("invalid normalizer")
        if not isinstance(obj["evidence"],dict) or not all(k in obj["evidence"] for k in ("sourceCommit","collector","capturedAt")):
            raise ValueError("missing provenance")
    a,b=history_map(source["history"]),history_map(target["history"])
    if source["identity"]["dialect"] != target["identity"]["dialect"] or source["identity"]["scope"] != target["identity"]["scope"] or source["normalizerVersion"] != target["normalizerVersion"]:
        state="unknown"
    elif any(a[k]!=b[k] for k in a.keys()&b.keys()):
        state="checksum_mismatch"
    elif a==b:
        state="equal" if source["snapshotFingerprint"]==target["snapshotFingerprint"] else "schema_drift"
    elif set(b).issubset(a):
        state="local_ahead"
    elif set(a).issubset(b):
        state="remote_ahead"
    elif source["snapshotFingerprint"]==target["snapshotFingerprint"]:
        state="history_mismatch"
    else:
        state="diverged"
    decision="requires_approval" if state=="local_ahead" else ("candidate" if state=="equal" else "blocked")
    semantic={"apiVersion":"sdkit.dev/migration-plan/v1","sourceCommit":source["evidence"]["sourceCommit"],"target":target["identity"],"preconditions":{"historyFingerprint":digest(target["history"]),"schemaFingerprint":target["snapshotFingerprint"],"normalizerVersion":target["normalizerVersion"]},"state":state,"decision":decision,"steps":[{"migrationId":k,"checksum":a[k],"risk":"requires_review"} for k in sorted(a.keys()-b.keys())] if state=="local_ahead" else [],"executionAuthorized":False}
    return {**semantic,"planHash":digest(semantic)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("target")
    args=p.parse_args()
    try:
        a=json.loads(Path(args.source).read_text(encoding="utf-8"))
        b=json.loads(Path(args.target).read_text(encoding="utf-8"))
        print(canonical(plan(a,b)))
        return 0
    except (ValueError,TypeError,OSError) as exc:
        print(canonical({"status":"blocked","reason":str(exc)}))
        return 2
if __name__=="__main__":
    raise SystemExit(main())
