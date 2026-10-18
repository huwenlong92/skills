#!/usr/bin/env python3
"""Offline, fail-closed migration planning; no database connections."""
import argparse
import hashlib
import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
DIALECTS = {"postgres", "mysql", "oracle", "sqlite"}
def _load_sibling(name):
    spec = importlib.util.spec_from_file_location("dbops_" + name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
def digest(obj):
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()
def history_map(doc):
    if not isinstance(doc, dict) or not isinstance(doc.get("migrations"), list):
        raise ValueError("invalid history")
    _load_sibling("validate_history").validate(doc)
    out = {}
    for m in doc["migrations"]:
        if not isinstance(m, dict) or not isinstance(m.get("migrationId"), str) or not isinstance(m.get("checksum"), str) or not SHA.fullmatch(m["checksum"]) or m.get("status") != "applied":
            raise ValueError("invalid migration record")
        if set(m) != {"migrationId", "checksum", "status"}:
            raise ValueError("invalid migration fields")
        if m["migrationId"] in out:
            raise ValueError("duplicate migration")
        out[m["migrationId"]] = m["checksum"]
    if set(doc) - {"migrations", "attempts"} or not isinstance(doc.get("attempts", []), list):
        raise ValueError("invalid history fields")
    if any(not isinstance(a, dict) or set(a) != {"status"} or a.get("status") != "applied" for a in doc.get("attempts", [])):
        raise ValueError("unresolved attempt")
    return out
def safety_gate(safety):
    """Untrusted offline evidence never authorizes writes or proves recovery."""
    if not isinstance(safety, dict) or set(safety) != {"operations", "backupRequest", "evidence"}:
        return {"status": "blocked", "reason": "missing or invalid safety evidence",
                "dataRisk": "unknown", "backupStatus": "evidence_required",
                "evidenceVerified": False, "executionAuthorized": False}
    risk = _load_sibling("data_safety").assess(safety["operations"])
    backup = _load_sibling("backup_decision").decide(safety["backupRequest"])
    evidence = safety["evidence"]
    if not isinstance(evidence, dict) or set(evidence) != {"recoveryEvidenceId", "capturedAt", "source"}:
        raise ValueError("invalid recovery evidence identity")
    if not all(isinstance(v, str) and v for v in evidence.values()):
        raise ValueError("empty recovery evidence identity")
    return {"status": "blocked", "reason": "offline evidence cannot prove recovery or authorize execution",
            "dataRisk": risk["risk"], "dataSafetyStatus": risk["status"],
            "backupStatus": backup["status"], "recommendedBackup": backup["recommendedStrategy"],
            "evidenceVerified": False, "executionAuthorized": False}

def plan(source, target, safety=None):
    for obj in (source, target):
        if not isinstance(obj, dict) or set(obj) != {"identity", "history", "snapshotFingerprint", "normalizerVersion", "evidence"}:
            raise ValueError("missing or unexpected evidence fields")
        ident = obj["identity"]
        if not isinstance(ident, dict) or set(ident) != {"environmentId", "databaseId", "dialect", "databaseVersion", "scope"}:
            raise ValueError("invalid database identity")
        if ident["dialect"] not in DIALECTS or any(not isinstance(ident[k], str) or not ident[k] for k in ("environmentId", "databaseId", "databaseVersion")):
            raise ValueError("invalid target identity")
        if not isinstance(ident["scope"], list) or not ident["scope"] or len(set(ident["scope"])) != len(ident["scope"]) or any(not isinstance(x,str) or not x for x in ident["scope"]):
            raise ValueError("invalid scope")
        if not isinstance(obj["snapshotFingerprint"],str) or not SHA.fullmatch(obj["snapshotFingerprint"]):
            raise ValueError("invalid snapshot fingerprint")
        if not isinstance(obj["normalizerVersion"],str) or not obj["normalizerVersion"]:
            raise ValueError("invalid normalizer")
        if not isinstance(obj["evidence"],dict) or set(obj["evidence"]) != {"sourceCommit","collector","capturedAt"}:
            raise ValueError("missing provenance")
        ev = obj["evidence"]
        if not isinstance(ev["sourceCommit"], str) or not COMMIT.fullmatch(ev["sourceCommit"]) or not isinstance(ev["collector"], str) or not ev["collector"] or not isinstance(ev["capturedAt"], str):
            raise ValueError("invalid provenance")
        try:
            datetime.fromisoformat(ev["capturedAt"].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("invalid capturedAt") from exc
    a,b=history_map(source["history"]),history_map(target["history"])
    if source["identity"]["environmentId"] == target["identity"]["environmentId"] and source["identity"]["databaseId"] == target["identity"]["databaseId"]:
        raise ValueError("source and target must be distinct environments")
    if source["identity"]["dialect"] != target["identity"]["dialect"] or source["identity"]["databaseVersion"] != target["identity"]["databaseVersion"] or sorted(source["identity"]["scope"]) != sorted(target["identity"]["scope"]) or source["normalizerVersion"] != target["normalizerVersion"]:
        state="unknown"
    elif any(a[k]!=b[k] for k in a.keys()&b.keys()):
        state="checksum_mismatch"
    elif a==b:
        state="equal" if source["snapshotFingerprint"]==target["snapshotFingerprint"] else "schema_drift"
    elif list(b.items()) == list(a.items())[:len(b)]:
        state="local_ahead"
    elif list(a.items()) == list(b.items())[:len(a)]:
        state="remote_ahead"
    elif source["snapshotFingerprint"]==target["snapshotFingerprint"]:
        state="history_mismatch"
    else:
        state="diverged"
    gate = safety_gate(safety)
    safety_hash = digest(safety) if safety is not None else None
    decision = "blocked"  # Offline plans never satisfy the execution safety gate.
    semantic={"apiVersion":"sdkit.dev/migration-plan/v1","sourceCommit":source["evidence"]["sourceCommit"],"sourceEvidenceFingerprint":digest(source["evidence"]),"targetEvidenceFingerprint":digest(target["evidence"]),"sourceHistoryFingerprint":digest(source["history"]),"sourceSchemaFingerprint":source["snapshotFingerprint"],"sourceNormalizerVersion":source["normalizerVersion"],"sourceIdentity":dict(source["identity"],scope=sorted(source["identity"]["scope"])),"target":dict(target["identity"],scope=sorted(target["identity"]["scope"])),"preconditions":{"historyFingerprint":digest(target["history"]),"schemaFingerprint":target["snapshotFingerprint"],"normalizerVersion":target["normalizerVersion"]},"state":state,"decision":decision,"safetyGate":gate,"safetyEvidenceFingerprint":safety_hash,"steps":[{"migrationId":k,"checksum":a[k],"risk":"requires_review"} for k in sorted(a.keys()-b.keys())] if state=="local_ahead" else [],"executionAuthorized":False}
    return {**semantic,"planHash":digest(semantic)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--safety", help="local offline safety evidence JSON")
    args=p.parse_args()
    try:
        a=json.loads(Path(args.source).read_text(encoding="utf-8"))
        b=json.loads(Path(args.target).read_text(encoding="utf-8"))
        safety = json.loads(Path(args.safety).read_text(encoding="utf-8")) if args.safety else None
        print(canonical(plan(a,b,safety)))
        return 0
    except (ValueError,TypeError,OSError) as exc:
        print(canonical({"status":"blocked","reason":str(exc)}))
        return 2
if __name__=="__main__":
    raise SystemExit(main())
