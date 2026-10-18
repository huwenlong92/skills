#!/usr/bin/env python3
"""Offline backup recommendation. Never performs backups or verifies restore."""
import json

def decide(request):
    if not isinstance(request, dict) or set(request) != {"operationRisk", "databaseSizeBytes", "affectedSizeBytes", "rpoSeconds", "rtoSeconds", "recoveryOptions"}:
        raise ValueError("invalid backup request")
    for key in ("databaseSizeBytes", "affectedSizeBytes", "rpoSeconds", "rtoSeconds"):
        if type(request[key]) is not int or request[key] < 0:
            raise ValueError("invalid numeric input")
    if request["affectedSizeBytes"] > request["databaseSizeBytes"]:
        raise ValueError("affected size exceeds database")
    risk = request["operationRisk"]
    if risk not in {"read_only", "additive", "structural", "destructive", "unknown"}:
        raise ValueError("invalid operation risk")
    options = request["recoveryOptions"]
    if not isinstance(options, list):
        raise ValueError("invalid recovery options")
    candidates = []
    for option in options:
        if not isinstance(option, dict) or set(option) != {"strategy", "coversAffectedObjects", "rpoSeconds", "rtoSeconds", "restoreVerified"}:
            raise ValueError("invalid recovery option")
        if option["strategy"] not in {"existing-pitr", "verified-snapshot", "targeted-backup", "full-backup"} or type(option["coversAffectedObjects"]) is not bool or type(option["restoreVerified"]) is not bool:
            raise ValueError("invalid option")
        if any(type(option[k]) is not int or option[k] < 0 for k in ("rpoSeconds", "rtoSeconds")):
            raise ValueError("invalid recovery objective")
        if option["coversAffectedObjects"] and option["restoreVerified"] and option["rpoSeconds"] <= request["rpoSeconds"] and option["rtoSeconds"] <= request["rtoSeconds"]:
            candidates.append(option["strategy"])
    preference = ("existing-pitr", "verified-snapshot", "targeted-backup", "full-backup") if request["databaseSizeBytes"] > 10**10 else ("targeted-backup", "existing-pitr", "verified-snapshot", "full-backup")
    selected = next((x for x in preference if x in candidates), None)
    return {"backupRequired": risk != "read_only", "recommendedStrategy": selected if selected else ("none-for-read-only" if risk == "read_only" else None), "status": "not_required" if risk == "read_only" else "evidence_required", "executionAuthorized": False, "evidenceVerifiedByTool": False, "eligibleClaimedOptions": sorted(set(candidates))}
