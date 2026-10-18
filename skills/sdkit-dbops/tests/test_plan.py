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
        p=m.plan(sample(),sample())
        self.assertEqual(p["state"],"equal")
        self.assertFalse(p["executionAuthorized"])
        self.assertEqual(p["planHash"],m.digest({k:v for k,v in p.items() if k!="planHash"}))
    def test_local_ahead(self):
        x=sample([{"migrationId":"a","checksum":"b"*64,"status":"applied"}])
        self.assertEqual(m.plan(x,sample())["state"],"local_ahead")
    def test_checksum_conflict(self):
        x=sample([{"migrationId":"a","checksum":"b"*64,"status":"applied"}])
        y=sample([{"migrationId":"a","checksum":"c"*64,"status":"applied"}])
        self.assertEqual(m.plan(x,y)["state"],"checksum_mismatch")
    def test_failed_attempt_blocked(self):
        x=sample();x["history"]["attempts"]=[{"status":"failed"}]
        with self.assertRaises(ValueError):m.plan(x,sample())
