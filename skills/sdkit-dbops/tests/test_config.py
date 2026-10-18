import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ConfigTests(unittest.TestCase):
    def test_schemas_are_valid_json(self):
        for name in ("project-config.schema.json", "migration-file.schema.json"):
            obj = json.loads((ROOT / "schemas" / name).read_text())
            self.assertEqual(obj["$schema"], "https://json-schema.org/draft/2020-12/schema")
            self.assertFalse(obj["additionalProperties"])

    def test_skill_entry(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("name: sdkit-dbops", text)
        self.assertIn("references/safety.md", text)

if __name__ == "__main__":
    unittest.main()
