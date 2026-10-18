import importlib.util
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parent / "project_skill_global.py"
spec = importlib.util.spec_from_file_location("project_skill_global", FILE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class GlobalBootstrapTests(unittest.TestCase):
    def test_empty(self):
        self.assertIn(m.START.encode(), m.plan(b""))
    def test_idempotent(self):
        first = m.plan(b"# Custom\n")
        self.assertEqual(first, m.plan(first))
    def test_preserves_custom(self):
        first = m.plan(b"# My Rules\n\nKeep this.\n")
        self.assertTrue(first.startswith(b"# My Rules\n\nKeep this.\n"))
    def test_replaces_managed_only(self):
        first = m.plan(b"Prefix\n")
        modified = first.replace(b"Skill", b"Old Skill")
        second = m.plan(modified)
        self.assertEqual(second, first)
    def test_rejects_bad_markers(self):
        for raw in [m.START.encode(), m.END.encode(), (m.START + m.START + m.END + m.END).encode()]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    m.plan(raw)
    def test_invalid_encoding(self):
        with self.assertRaises(UnicodeError):
            m.plan(b"\xff")
    def test_digest(self):
        self.assertEqual(len(m.digest(b"hello")), 64)
    def test_existing_block_preserves_tail(self):
        a = m.plan(b"Before\n")
        b = m.plan(a + b"After\n")
        self.assertTrue(b.endswith(b"After\n"))
        self.assertEqual(b, m.plan(b))

if __name__ == "__main__":
    unittest.main()
