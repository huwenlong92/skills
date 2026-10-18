import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/compare_snapshots.py"
spec=importlib.util.spec_from_file_location("dbops_drift",p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class DriftTests(unittest.TestCase):
    def test_scope_unknown(self):
        a={"dialect":"postgres","databaseVersion":"18","normalizerVersion":"1","scope":["public"],"coverage":{"complete":True,"kinds":["table"]},"objects":[]}
        self.assertEqual(mod.compare(a,dict(a,scope=["other"]))["status"],"unknown")
