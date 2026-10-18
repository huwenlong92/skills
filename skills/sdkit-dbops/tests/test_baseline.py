import json
import pathlib
import unittest
class BaselineTests(unittest.TestCase):
    def test_contract(self):
        root=pathlib.Path(__file__).resolve().parents[1]
        schema=json.loads((root/"schemas/baseline.schema.json").read_text())
        self.assertIn("schemaFingerprint",schema["required"])
        self.assertFalse(schema["additionalProperties"])
