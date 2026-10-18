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

    def test_unknown_object_field(self):
        obj = {"kind": "table", "schema": "public", "name": "a", "unexpected": True}
        self.assertEqual(mod.compare(snap([obj]), snap())["status"], "unknown")

    def test_invalid_attributes(self):
        obj = {"kind": "table", "schema": "public", "name": "a", "attributes": []}
        self.assertEqual(mod.compare(snap([obj]), snap())["status"], "unknown")

    def test_unknown_snapshot_field(self):
        obj = snap()
        obj["dsn"] = "unexpected"
        self.assertEqual(mod.compare(obj, snap())["status"], "unknown")


    def test_boolean_number_distinction(self):
        a = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": True}}])
        b = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": 1}}])
        self.assertEqual(mod.compare(a, b)["status"], "drift")

    def test_integer_float_distinction(self):
        a = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": 1}}])
        b = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": 1.0}}])
        self.assertEqual(mod.compare(a, b)["status"], "drift")

    def test_signed_zero_distinction(self):
        a = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": -0.0}}])
        b = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": 0.0}}])
        self.assertEqual(mod.compare(a, b)["status"], "drift")

    def test_unknown_coverage_field(self):
        a = snap()
        a["coverage"]["extra"] = "discarded"
        self.assertEqual(mod.compare(a, snap())["status"], "unknown")

    def test_nan_rejected(self):
        a = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": float("nan")}}])
        self.assertEqual(mod.compare(a, snap())["status"], "unknown")

    def test_infinity_rejected(self):
        a = snap([{"kind": "table", "schema": "public", "name": "a", "attributes": {"x": float("inf")}}])
        self.assertEqual(mod.compare(a, snap())["status"], "unknown")
