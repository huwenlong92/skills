import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1] / "scripts"
def load(name):
    spec = importlib.util.spec_from_file_location("test_" + name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
plan = load("plan_migrations")
recovery = load("recovery_report")

def sample(environment):
    return {"identity": {"environmentId": environment, "databaseId": "db", "dialect": "postgres",
                         "databaseVersion": "18", "scope": ["public"]},
            "history": {"migrations": []}, "snapshotFingerprint": "a" * 64,
            "normalizerVersion": "1", "evidence": {"sourceCommit": "0" * 40,
            "collector": "offline", "capturedAt": "2026-10-18T00:00:00Z"}}

def safety(operations=None):
    return {"operations": operations if operations is not None else [{"kind": "sql", "text": "TRUNCATE TABLE public.users"}],
            "backupRequest": {"operationRisk": "destructive", "databaseSizeBytes": 200000000000,
                              "affectedSizeBytes": 80000000000, "rpoSeconds": 300,
                              "rtoSeconds": 3600, "recoveryOptions": []},
            "evidence": {"recoveryEvidenceId": "claim-only", "capturedAt": "2026-10-18T00:00:00Z",
                         "source": "unverified"}}

class SafetyIntegrationTests(unittest.TestCase):
    def test_missing_safety_blocks(self):
        p = plan.plan(sample("local"), sample("remote"))
        self.assertEqual(p["decision"], "blocked")
        self.assertFalse(p["executionAuthorized"])
    def test_destructive_sql_blocks(self):
        p = plan.plan(sample("local"), sample("remote"), safety())
        self.assertEqual(p["safetyGate"]["dataRisk"], "destructive")
        self.assertEqual(p["decision"], "blocked")
    def test_backup_claim_does_not_authorize(self):
        x = safety()
        x["backupRequest"]["recoveryOptions"] = [{"strategy": "existing-pitr", "coversAffectedObjects": True,
            "rpoSeconds": 60, "rtoSeconds": 600, "restoreVerified": True}]
        p = plan.plan(sample("local"), sample("remote"), x)
        self.assertFalse(p["safetyGate"]["evidenceVerified"])
        self.assertEqual(p["decision"], "blocked")
    def test_evidence_changes_plan_hash(self):
        x = safety()
        first = plan.plan(sample("local"), sample("remote"), x)
        x["evidence"]["recoveryEvidenceId"] = "another"
        second = plan.plan(sample("local"), sample("remote"), x)
        self.assertNotEqual(first["planHash"], second["planHash"])
    def test_target_change_invalidates_hash(self):
        a = plan.plan(sample("local"), sample("remote"), safety())
        b = sample("remote")
        b["snapshotFingerprint"] = "b" * 64
        self.assertNotEqual(a["planHash"], plan.plan(sample("local"), b, safety())["planHash"])
    def test_orm_seed_blocked(self):
        x = safety([{"kind": "seed", "text": "reset demo accounts"}])
        self.assertEqual(plan.plan(sample("local"), sample("remote"), x)["decision"], "blocked")
    def test_recovery_never_authorizes(self):
        doc = {"operationId": "op1", "targetIdentity": {"databaseId": "db"},
               "lastKnownStep": "step1", "failureState": "partially_committed", "observations": []}
        r = recovery.report(doc)
        self.assertEqual(r["status"], "investigation_required")
        self.assertFalse(r["executionAuthorized"])
    def test_bad_recovery_state_rejected(self):
        with self.assertRaises(ValueError):
            recovery.report({"operationId": "op1", "targetIdentity": {"databaseId": "db"},
                "lastKnownStep": None, "failureState": "succeeded", "observations": []})
