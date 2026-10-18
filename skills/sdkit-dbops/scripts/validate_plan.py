#!/usr/bin/env python3
"""Offline plan integrity verification. Does not authorize execution."""
import argparse
import json
import re
from datetime import datetime
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("dbops_plan_for_validation", Path(__file__).with_name("plan_migrations.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
digest = module.digest
def validate(doc):
    if not isinstance(doc,dict) or not isinstance(doc.get("planHash"),str):
        raise ValueError("invalid plan")
    expected={"apiVersion","sourceCommit","sourceEvidenceFingerprint","targetEvidenceFingerprint","sourceHistoryFingerprint","sourceSchemaFingerprint","sourceNormalizerVersion","sourceIdentity","target","preconditions","state","decision","safetyGate","safetyEvidenceFingerprint","steps","executionAuthorized","planHash"}
    if set(doc) != expected or doc.get("apiVersion") != "sdkit.dev/migration-plan/v1":
        raise ValueError("invalid plan structure")
    if doc.get("decision") not in ("candidate", "requires_approval", "blocked") or not isinstance(doc.get("steps"), list):
        raise ValueError("invalid plan decision")
    sha = re.compile(r"^[a-f0-9]{64}$")
    commit = re.compile(r"^[a-f0-9]{40}$")
    for k in ("planHash", "sourceEvidenceFingerprint", "targetEvidenceFingerprint",
              "sourceHistoryFingerprint", "sourceSchemaFingerprint"):
        if not isinstance(doc.get(k), str) or not sha.fullmatch(doc[k]):
            raise ValueError("invalid fingerprint")
    if doc.get("safetyEvidenceFingerprint") is not None and (
        not isinstance(doc["safetyEvidenceFingerprint"], str)
        or not sha.fullmatch(doc["safetyEvidenceFingerprint"])
    ):
        raise ValueError("invalid safety fingerprint")
    if not isinstance(doc.get("sourceCommit"), str) or not commit.fullmatch(doc["sourceCommit"]):
        raise ValueError("invalid source commit")
    if not isinstance(doc.get("sourceNormalizerVersion"), str) or not doc["sourceNormalizerVersion"]:
        raise ValueError("invalid source normalizer")
    for k in ("sourceIdentity", "target"):
        ident = doc.get(k)
        if not isinstance(ident, dict) or set(ident) != {"environmentId", "databaseId", "dialect", "databaseVersion", "scope"}:
            raise ValueError("invalid identity")
        if ident["dialect"] not in module.DIALECTS or any(not isinstance(ident[x], str) or not ident[x] for x in ("environmentId", "databaseId", "databaseVersion")):
            raise ValueError("invalid identity values")
        if not isinstance(ident["scope"], list) or not ident["scope"] or any(not isinstance(x, str) or not x for x in ident["scope"]) or len(set(ident["scope"])) != len(ident["scope"]):
            raise ValueError("invalid scope")
    pre = doc.get("preconditions")
    if not isinstance(pre, dict) or set(pre) != {"historyFingerprint", "schemaFingerprint", "normalizerVersion"}:
        raise ValueError("invalid preconditions")
    if any(not isinstance(pre[k], str) for k in pre) or not sha.fullmatch(pre["historyFingerprint"]) or not sha.fullmatch(pre["schemaFingerprint"]) or not pre["normalizerVersion"]:
        raise ValueError("invalid precondition values")
    if doc.get("state") not in {"equal", "local_ahead", "remote_ahead", "diverged", "schema_drift", "history_mismatch", "checksum_mismatch", "unknown"}:
        raise ValueError("invalid state")
    gate = doc.get("safetyGate")
    if not isinstance(gate, dict) or gate.get("status") != "blocked" or gate.get("executionAuthorized") is not False or gate.get("evidenceVerified") is not False:
        raise ValueError("invalid nested safety flags")
    optional_gate = {
        "reason": lambda v: isinstance(v, str),
        "dataRisk": lambda v: v in ("unknown", "destructive") if isinstance(v, str) else False,
        "dataSafetyStatus": lambda v: v in ("unknown", "blocked") if isinstance(v, str) else False,
        "backupStatus": lambda v: v in ("evidence_required", "not_required") if isinstance(v, str) else False,
        "recommendedBackup": lambda v: v is None or isinstance(v, str),
    }
    for field, predicate in optional_gate.items():
        if field in gate and not predicate(gate[field]):
            raise ValueError("invalid safety gate field: " + field)
    if not isinstance(doc["steps"], list) or any(not isinstance(x, dict) or set(x) != {"migrationId", "checksum", "risk"} or not isinstance(x["migrationId"], str) or not module._load_sibling("validate_history").MID.fullmatch(x["migrationId"]) or not isinstance(x["checksum"], str) or not sha.fullmatch(x["checksum"]) or x["risk"] != "requires_review" for x in doc["steps"]):
        raise ValueError("invalid steps")
    for step in doc["steps"]:
        try:
            datetime.strptime(step["migrationId"][:16], "%Y%m%dT%H%M%SZ")
        except ValueError as exc:
            raise ValueError("invalid migration step date") from exc
    if set(gate) - {"status", "reason", "dataRisk", "dataSafetyStatus", "backupStatus", "recommendedBackup", "evidenceVerified", "executionAuthorized"}:
        raise ValueError("unknown safety gate fields")
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
        print(json.dumps(validate(json.loads(Path(a.path).read_text(encoding="utf-8"), parse_constant=lambda x: (_ for _ in ()).throw(ValueError("invalid JSON constant")))),sort_keys=True))
        return 0
    except (OSError,ValueError,TypeError) as e:
        print(json.dumps({"status":"blocked","reason":str(e)},sort_keys=True))
        return 2
if __name__=="__main__":
    raise SystemExit(main())
