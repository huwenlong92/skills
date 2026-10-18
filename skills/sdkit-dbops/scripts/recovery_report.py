#!/usr/bin/env python3
"""Offline recovery triage; never executes rollback or validates backups."""
import argparse
import json
from pathlib import Path

STATES = {"failed", "interrupted", "unknown", "partially_committed"}

def report(evidence):
    if not isinstance(evidence, dict) or set(evidence) != {"operationId", "targetIdentity", "lastKnownStep", "failureState", "observations"}:
        raise ValueError("invalid recovery evidence")
    if not isinstance(evidence["operationId"], str) or not evidence["operationId"]:
        raise ValueError("invalid operation identity")
    if not isinstance(evidence["targetIdentity"], dict) or not evidence["targetIdentity"]:
        raise ValueError("invalid target identity")
    if evidence["failureState"] not in STATES:
        raise ValueError("invalid failure state")
    if not isinstance(evidence["observations"], list):
        raise ValueError("invalid observations")
    return {"status": "investigation_required",
            "reason": "execution state cannot be established from offline evidence",
            "operationId": evidence["operationId"],
            "targetIdentity": evidence["targetIdentity"],
            "lastKnownStep": evidence["lastKnownStep"],
            "failureState": evidence["failureState"],
            "recoveryRequirements": ["recollect actual schema and affected data evidence",
                                     "verify recoverability using an independent trusted source",
                                     "prepare a new plan and obtain new approval"],
            "executionAuthorized": False}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence")
    args = p.parse_args()
    try:
        evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
        print(json.dumps(report(evidence), ensure_ascii=False, sort_keys=True, allow_nan=False))
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "executionAuthorized": False}))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
