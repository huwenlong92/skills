"""Offline manager regression tests. Run from repository root with unittest discover."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("manager.py")
spec = importlib.util.spec_from_file_location("sdkit_manager", SCRIPT)
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "skills").mkdir()
        self.catalog = self.root / "catalog.json"
        self.catalog.write_text(json.dumps({
            "schema_version": 1,
            "categories": {"language": "语言"},
            "skills": [{"name": "demo", "category": "language", "path": "skills/demo"}]
        }))
        demo = self.root / "skills" / "demo"
        demo.mkdir()
        (demo / "SKILL.md").write_text("---\nname: demo\ndescription: 测试技能\n---\n\n# Demo\n")
        self.patch_root = patch.object(manager, "ROOT", self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)

    def test_validate(self):
        self.assertEqual(manager.validate(all_skills=True), 1)

    def test_create(self):
        manager.create("new-demo", "language")
        self.assertTrue((self.root / "skills/new-demo/SKILL.md").exists())
        self.assertEqual(manager.validate(all_skills=True), 2)

    def test_create_duplicate(self):
        with self.assertRaises(ValueError):
            manager.create("demo", "language")

    def test_create_invalid_name(self):
        with self.assertRaises(ValueError):
            manager.create("../escape", "language")

    def test_catalog_mismatch(self):
        (self.root / "skills" / "unexpected").mkdir()
        with self.assertRaises(ValueError):
            manager.validate(all_skills=True)

    def test_broken_link(self):
        (self.root / "skills/demo/SKILL.md").write_text(
            "---\nname: demo\ndescription: Test\n---\n\n[missing](missing.md)\n")
        with self.assertRaises(ValueError):
            manager.validate(all_skills=True)

    def test_install_and_update(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        self.assertTrue((target / "demo/SKILL.md").exists())
        (self.root / "skills/demo/SKILL.md").write_text(
            "---\nname: demo\ndescription: Updated\n---\n")
        manager.install("demo", target, update=True)
        self.assertIn("Updated", (target / "demo/SKILL.md").read_text())

    def test_install_no_overwrite(self):
        target = self.root / "agent"
        target.mkdir()
        (target / "demo").mkdir()
        with self.assertRaises(ValueError):
            manager.install("demo", target)

    def test_update_preserves_local_changes(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        (target / "demo/SKILL.md").write_text("locally edited")
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)
        self.assertEqual((target / "demo/SKILL.md").read_text(), "locally edited")

    def test_update_rejects_extra_file(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        (target / "demo/extra.md").write_text("local")
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)

    def test_install_rejects_symlink(self):
        target = self.root / "agent"
        target.mkdir()
        (self.root / "skills/demo/linked").symlink_to(self.catalog)
        with self.assertRaises(ValueError):
            manager.install("demo", target)


if __name__ == "__main__":
    unittest.main()
