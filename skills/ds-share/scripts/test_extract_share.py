import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("extract_share.py")
SPEC = importlib.util.spec_from_file_location("extract_share", SCRIPT)
extractor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(extractor)
SOURCE = "https://chat.deepseek.com/share/fixture_id"


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "response.json"
        self.messages = [
            {"message_id": 2, "role": "USER", "content": "Fixture question", "status": "FINISHED"},
            {"message_id": 9, "role": "ASSISTANT", "content": "Fixture answer", "status": "FINISHED"},
        ]
        self.data = {"code": 0, "data": {"biz_code": 0, "biz_data": {"messages": self.messages}}}
        self.write()

    def write(self):
        self.input.write_text(json.dumps(self.data), encoding="utf-8")

    def extract(self):
        return extractor.extract(self.input, SOURCE, self.root)

    def test_success_preserves_order_ids_and_scope_without_network_claim(self):
        summary = self.extract()
        output = Path(summary["output_directory"])
        text = (output / "conversation.md").read_text()
        self.assertLess(text.index("Fixture question"), text.index("Fixture answer"))
        self.assertIn("message_id: 2", text)
        self.assertIn("message_id: 9", text)
        self.assertEqual(summary["message_count"], 2)
        self.assertEqual(summary["scope"], "returned_messages_only")
        self.assertFalse(summary["http_verified"])
        self.assertEqual(summary["review_messages"], [])

    def test_business_failure_never_creates_output(self):
        for field in ("code", "biz_code"):
            with self.subTest(field=field):
                data = copy.deepcopy(self.data)
                (data if field == "code" else data["data"])[field] = 1
                self.input.write_text(json.dumps(data))
                before = set(self.root.iterdir())
                with self.assertRaises(ValueError):
                    self.extract()
                self.assertEqual(before, set(self.root.iterdir()))

    def test_boolean_codes_are_not_success(self):
        self.data["code"] = False
        self.write()
        with self.assertRaises(ValueError):
            self.extract()

    def test_empty_or_unreadable_messages_fail(self):
        for messages in ([], [{"role": "USER", "content": "  "}], [{"role": "USER", "content": None}]):
            with self.subTest(messages=messages):
                self.data["data"]["biz_data"]["messages"] = messages
                self.write()
                with self.assertRaises(ValueError):
                    self.extract()

    def test_structure_change_fails_instead_of_substituting_empty_fields(self):
        for data in ([], {"code": 0, "data": []}, {"code": 0, "data": {"biz_code": 0, "biz_data": {"messages": "changed"}}}):
            with self.subTest(data=data):
                self.input.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    self.extract()

    def test_attachment_and_status_signals_are_retained_for_review(self):
        self.messages[1].update(status="UNKNOWN", files=[{"url": "https://files.example.invalid/fixture"}], incomplete_message=True)
        self.messages.append({"role": "TOOL", "content": ""})
        self.write()
        reviews = self.extract()["review_messages"]
        self.assertIn("attachments_not_extracted", reviews[0]["reasons"])
        self.assertIn("incomplete_message", reviews[0]["reasons"])
        self.assertIn("missing_or_unrecognized_status", reviews[0]["reasons"])
        self.assertIn("missing_message_id", reviews[1]["reasons"])
        self.assertIn("unrecognized_role", reviews[1]["reasons"])
        self.assertIn("empty_content", reviews[1]["reasons"])

    def test_malformed_attachment_field_is_reviewed_not_dropped(self):
        self.messages[1]["files"] = {"unexpected": True}
        self.write()
        self.assertIn("unrecognized_files_structure", self.extract()["review_messages"][0]["reasons"])

    def test_reasoning_and_attachment_urls_never_enter_export(self):
        self.messages[1].update(thinking_content="PRIVATE_REASONING_FIXTURE", files=[{"url": "https://files.example.invalid/hidden"}])
        self.write()
        output = Path(self.extract()["output_directory"])
        for path in output.iterdir():
            text = path.read_text()
            self.assertNotIn("PRIVATE_REASONING_FIXTURE", text)
            self.assertNotIn("https://files.example.invalid/hidden", text)

    def test_input_is_unchanged_and_outputs_never_overwrite(self):
        original = self.input.read_bytes()
        first = self.extract()
        second = self.extract()
        self.assertNotEqual(first["output_directory"], second["output_directory"])
        self.assertEqual(self.input.read_bytes(), original)

    def test_skill_directory_cannot_be_an_output_destination(self):
        with self.assertRaises(ValueError):
            extractor.extract(self.input, SOURCE, SCRIPT.parent)

    def test_url_validation_canonicalizes_and_rejects_untrusted_targets(self):
        self.assertEqual(extractor.canonical_url(SOURCE + "/?ignored=1#part"), SOURCE)
        for source in (
            "http://chat.deepseek.com/share/id", "https://other.example.invalid/share/id",
            "https://chat.deepseek.com.evil.example.invalid/share/id", "https://chat.deepseek.com/share/a/b",
            "https://chat.deepseek.com/share/a%20b", "https://user:secret@chat.deepseek.com/share/id",
            "https://chat.deepseek.com:8443/share/id", "https://chat.deepseek.com/share/",
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                extractor.canonical_url(source)

    def test_cli_validates_url_without_input_or_output_files(self):
        before = set(self.root.iterdir())
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", SOURCE, "--check-url"], capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), SOURCE)
        self.assertEqual(before, set(self.root.iterdir()))

    def test_invalid_json_returns_failure_without_echoing_material(self):
        self.input.write_text("PRIVATE_RESPONSE_FIXTURE invalid JSON")
        result = subprocess.run([sys.executable, str(SCRIPT), "--source", SOURCE, "--input", str(self.input)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("PRIVATE_RESPONSE_FIXTURE", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
