import importlib.util
import pathlib
import unittest
path = pathlib.Path(__file__).resolve().parents[1] / "scripts/check_operation_intent.py"
spec = importlib.util.spec_from_file_location("dbops_intent", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def sample():
    return {"environment": "production", "target": {"instanceId": "example", "databaseId": "db", "scope": ["public"]},
            "operations": [{"type": "alter", "risk": "additive", "objects": ["public.users"]}],
            "planHash": "a"*64, "approval": {"approved": True}, "backup": {"restoreVerified": True}}
class IntentTests(unittest.TestCase):
    def test_production_remains_blocked(self):
        self.assertFalse(mod.validate(sample())["executionAuthorized"])
    def test_claimed_approval_cannot_unlock(self):
        self.assertEqual(mod.validate(sample())["status"], "blocked")
    def test_truncate_requires_special_approval(self):
        x=sample();x["operations"]=[{"type":"truncate","risk":"destructive","objects":["public.users"]}]
        self.assertTrue(any("high-risk" in v for v in mod.validate(x)["reasons"]))
    def test_protected_schema(self):
        x=sample();x["operations"][0]["objects"]=["system_data.accounts"]
        self.assertIn("protected infrastructure object",mod.validate(x)["reasons"])
    def test_unknown_environment(self):
        x=sample();x["environment"]="mystery"
        with self.assertRaises(ValueError):mod.validate(x)
    def test_invalid_hash(self):
        x=sample();x["planHash"]="bad"
        with self.assertRaises(ValueError):mod.validate(x)
    def test_empty_operations(self):
        x=sample();x["operations"]=[]
        with self.assertRaises(ValueError):mod.validate(x)
    def test_unknown_fields(self):
        x=sample();x["unexpected"]="yes"
        with self.assertRaises(ValueError):mod.validate(x)
