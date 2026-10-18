import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dbops_baseline", ROOT / "scripts/validate_baseline.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def baseline():
    return {"baselineId": "initial", "dialect": "postgres", "scope": ["public"],
            "schemaFingerprint": "a" * 64, "normalizerVersion": "1", "checksum": "b" * 64}

class BaselineTests(unittest.TestCase):
    def test_schema_contract(self):
        schema = json.loads((ROOT / "schemas/baseline.schema.json").read_text())
        self.assertEqual(set(schema["required"]), set(mod.FIELDS))
        self.assertFalse(schema["additionalProperties"])

    def test_valid_descriptor_does_not_adopt(self):
        self.assertFalse(mod.validate(baseline())["adopted"])

    def test_duplicate_scope(self):
        doc = baseline()
        doc["scope"] = ["public", "public"]
        with self.assertRaisesRegex(ValueError, "scope"):
            mod.validate(doc)

    def test_invalid_checksum(self):
        doc = baseline()
        doc["checksum"] = "bad"
        with self.assertRaises(ValueError):
            mod.validate(doc)

    def test_unknown_field(self):
        doc = baseline()
        doc["connectionString"] = "example"
        with self.assertRaises(ValueError):
            mod.validate(doc)

    def test_unknown_dialect(self):
        doc = baseline()
        doc["dialect"] = "unknown"
        with self.assertRaises(ValueError):
            mod.validate(doc)
