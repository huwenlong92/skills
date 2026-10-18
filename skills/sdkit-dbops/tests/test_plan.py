import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/plan_migrations.py"
s=importlib.util.spec_from_file_location("dbops_plan",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def sample(records=None):
    return {"identity":{"environmentId":"dev","databaseId":"db","dialect":"postgres","databaseVersion":"18","scope":["public"]},"history":{"migrations":records or []},"snapshotFingerprint":"a"*64,"normalizerVersion":"1","evidence":{"sourceCommit":"0"*40,"collector":"offline","capturedAt":"2026-10-18T00:00:00Z"}}
class PlanTests(unittest.TestCase):
    def test_equal_candidate_not_authorized(self):
        source=sample();target=sample();target["identity"]["environmentId"]="remote-dev"
        p=m.plan(source,target)
        self.assertEqual(p["state"],"equal")
        self.assertEqual(p["decision"],"blocked")
        self.assertFalse(p["executionAuthorized"])
        self.assertEqual(p["planHash"],m.digest({k:v for k,v in p.items() if k!="planHash"}))
    def test_local_ahead(self):
        x=sample([{"migrationId":"20261018T053000Z_a83f2c_add_avatar","checksum":"b"*64,"status":"applied"}])
        self.assertEqual(m.plan(x,dict(sample(),identity=dict(sample()["identity"],environmentId="remote-dev")))["state"],"local_ahead")
    def test_checksum_conflict(self):
        x=sample([{"migrationId":"a","checksum":"b"*64,"status":"applied"}])
        y=sample([{"migrationId":"a","checksum":"c"*64,"status":"applied"}])
        self.assertEqual(m.plan(x,dict(y,identity=dict(y["identity"],environmentId="remote-dev")))["state"],"checksum_mismatch")
    def test_failed_attempt_blocked(self):
        x=sample();x["history"]["attempts"]=[{"status":"failed"}]
        with self.assertRaises(ValueError):m.plan(x,dict(sample(),identity=dict(sample()["identity"],environmentId="remote-dev")))

    def test_self_target_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            m.plan(sample(),sample())

    def test_unknown_provenance_rejected(self):
        source=sample();source["evidence"]["extra"]="untrusted"
        target=sample();target["identity"]["environmentId"]="remote-dev"
        with self.assertRaises(ValueError):
            m.plan(source,target)

    def test_unresolved_attempt_rejected(self):
        source=sample();source["history"]["attempts"]=[{"status":"unknown"}]
        target=sample();target["identity"]["environmentId"]="remote-dev"
        with self.assertRaises(ValueError):
            m.plan(source,target)
