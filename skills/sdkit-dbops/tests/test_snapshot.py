import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/compare_snapshots.py"
spec=importlib.util.spec_from_file_location("dbops_snapshot",p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def snap(objects=None):
    return {"dialect":"postgres","databaseVersion":"18","normalizerVersion":"1","scope":["public"],"coverage":{"complete":True,"kinds":["table"]},"objects":objects if objects is not None else []}
class SnapshotTests(unittest.TestCase):
    def test_order_independent(self):
        a=snap([{"kind":"table","schema":"public","name":"a"},{"kind":"table","schema":"public","name":"b"}])
        self.assertEqual(mod.compare(a,snap(list(reversed(a["objects"]))))["status"],"equal")
    def test_drift(self):
        self.assertEqual(mod.compare(snap(),snap([{"kind":"table","schema":"public","name":"a"}]))["status"],"drift")
    def test_incomplete(self):
        a=snap();a["coverage"]["complete"]=False
        self.assertEqual(mod.compare(a,snap())["status"],"unknown")
    def test_normalizer(self):
        b=snap();b["normalizerVersion"]="2"
        self.assertEqual(mod.compare(snap(),b)["status"],"unknown")
    def test_duplicate(self):
        x={"kind":"table","schema":"public","name":"a"}
        self.assertEqual(mod.compare(snap([x,x]),snap())["status"],"unknown")
