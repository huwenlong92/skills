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
        # macOS exposes temporary storage through /var -> /private/var.
        # Use the canonical fixture path while still rejecting user symlinks.
        self.root = Path(self.tmp.name).resolve()
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

    def test_create_catalog_replace_failure_rolls_back(self):
        with patch.object(manager.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                manager.create("new-demo", "language")
        self.assertFalse((self.root / "skills/new-demo").exists())
        self.assertEqual(manager.validate(all_skills=True), 1)

    def test_update_rejects_malformed_record(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        (target / "demo" / manager.RECORD).write_text("{broken")
        with self.assertRaises(json.JSONDecodeError):
            manager.install("demo", target, update=True)
        self.assertTrue((target / "demo/SKILL.md").exists())

    def test_update_rename_failure_restores_original(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        original = (target / "demo/SKILL.md").read_bytes()
        original_rename = Path.rename
        def failing_rename(path, to):
            if path.name.startswith(".sdkit-stage-"):
                raise OSError("stage rename failed")
            return original_rename(path, to)
        with patch.object(Path, "rename", failing_rename):
            with self.assertRaises(OSError):
                manager.install("demo", target, update=True)
        self.assertEqual((target / "demo/SKILL.md").read_bytes(), original)

    def test_update_failed_restore_preserves_backup(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        original = (target / "demo/SKILL.md").read_bytes()
        original_rename = Path.rename

        def fail_stage_and_restore(path, to):
            if path.name.startswith(".sdkit-stage-") or path.name.startswith(".sdkit-backup-"):
                raise OSError("injected rename failure")
            return original_rename(path, to)

        with patch.object(Path, "rename", fail_stage_and_restore):
            with self.assertRaisesRegex(RuntimeError, "backup retained"):
                manager.install("demo", target, update=True)
        backups = list(target.glob(".sdkit-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_bytes(), original)

    def test_target_symlink_parent_rejected(self):
        real = self.root / "real"
        real.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            manager.install("demo", alias)

    def test_install_rejects_symlink(self):
        target = self.root / "agent"
        target.mkdir()
        (self.root / "skills/demo/linked").symlink_to(self.catalog)
        with self.assertRaises(ValueError):
            manager.install("demo", target)

    def test_markdown_code_is_not_a_link(self):
        entry = self.root / "skills/demo/SKILL.md"
        with entry.open("a") as handle:
            handle.write('\n```go\nfunc From[T any](ctx *Context[T]) {}\n```\n'
                         '~~~text\n[example](missing.md)\n~~~\n'
                         '`[example](missing.md)`\n\n    [example](missing.md)\n')
        self.assertEqual(manager.validate(all_skills=True), 1)

    def test_markdown_link_forms(self):
        entry = self.root / "skills/demo/SKILL.md"
        (entry.parent / "with space.md").write_text("# Destination")
        with entry.open("a") as handle:
            handle.write('\n[encoded](with%20space.md#section)\n'
                         '[angle](<with space.md>)\n[title](SKILL.md "entry")\n')
        self.assertEqual(manager.validate(all_skills=True), 1)
        with entry.open("a") as handle:
            handle.write('\n[ref][missing]\n[missing]: absent.md\n')
        with self.assertRaisesRegex(ValueError, "broken link"):
            manager.validate(all_skills=True)

    def test_catalog_replace_failure_preserves_bytes(self):
        original = self.catalog.read_bytes()
        with patch.object(manager.os, "replace", side_effect=OSError("failure")):
            with self.assertRaises(OSError):
                manager.create("new-demo", "language")
        self.assertEqual(self.catalog.read_bytes(), original)
        self.assertEqual(list(self.root.glob(".catalog-*")), [])

    def test_catalog_symlink_rejected(self):
        original = self.catalog.read_bytes()
        other = self.root / "other.json"
        self.catalog.rename(other)
        self.catalog.symlink_to(other)
        with self.assertRaises(ValueError):
            manager.create("new-demo", "language")
        self.assertEqual(other.read_bytes(), original)
        self.assertFalse((self.root / "skills/new-demo").exists())

    def test_source_parent_symlink_rejected(self):
        skills = self.root / "skills"
        real = self.root / "real-skills"
        skills.rename(real)
        skills.symlink_to(real, target_is_directory=True)
        target = self.root / "agent"
        target.mkdir()
        for action in (lambda: manager.create("new-demo", "language"),
                       lambda: manager.install("demo", target)):
            with self.assertRaises(ValueError):
                action()
        self.assertFalse((real / "new-demo").exists())

    def test_install_record_matches_source(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        record = json.loads((target / "demo" / manager.RECORD).read_text())
        self.assertEqual(record, {"name": "demo", "files": manager.manifest(self.root / "skills/demo")})
        self.assertEqual(list(target.glob(".sdkit-*")), [])

    def test_reserved_source_record_rejected(self):
        (self.root / "skills/demo" / manager.RECORD).write_text("private data")
        target = self.root / "agent"
        target.mkdir()
        with self.assertRaises(ValueError):
            manager.install("demo", target)
        self.assertEqual(list(target.iterdir()), [])

    def test_update_rejects_extra_empty_directory(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        (target / "demo/local").mkdir()
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)
        self.assertTrue((target / "demo/local").is_dir())

    def test_update_rejects_non_object_record(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        for value in ([], None, "bad"):
            (target / "demo" / manager.RECORD).write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                manager.install("demo", target, update=True)
        self.assertTrue((target / "demo/SKILL.md").is_file())

    def test_failed_restore_with_existing_destination_preserves_backup(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        original = (target / "demo/SKILL.md").read_bytes()
        original_rename = Path.rename

        def fail_with_competing_destination(path, to):
            if path.name.startswith(".sdkit-stage-"):
                Path(to).mkdir()
                (Path(to) / "other.txt").write_text("keep")
                raise OSError("destination appeared")
            return original_rename(path, to)

        with patch.object(Path, "rename", fail_with_competing_destination):
            with self.assertRaisesRegex(RuntimeError, "backup retained"):
                manager.install("demo", target, update=True)
        backups = list(target.glob(".sdkit-backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_bytes(), original)
        self.assertEqual((target / "demo/other.txt").read_text(), "keep")

    def test_install_copy_failure_leaves_no_destination(self):
        target = self.root / "agent"
        target.mkdir()
        with patch.object(manager.shutil, "copytree", side_effect=OSError("copy failed")):
            with self.assertRaises(OSError):
                manager.install("demo", target)
        self.assertEqual(list(target.iterdir()), [])

    def test_create_existing_lock_is_preserved(self):
        lock = self.root / ".sdkit-catalog.lock"
        lock.write_text("other writer")
        with self.assertRaises(FileExistsError):
            manager.create("new-demo", "language")
        self.assertEqual(lock.read_text(), "other writer")
        self.assertFalse((self.root / "skills/new-demo").exists())

    def test_install_existing_lock_is_preserved(self):
        target = self.root / "agent"
        target.mkdir()
        lock = target / ".sdkit-demo.lock"
        lock.write_text("other writer")
        with self.assertRaises(FileExistsError):
            manager.install("demo", target)
        self.assertEqual(lock.read_text(), "other writer")
        self.assertFalse((target / "demo").exists())

    def test_install_does_not_replace_directory_appearing_during_copy(self):
        target = self.root / "agent"
        target.mkdir()
        copytree = shutil.copytree

        def competing_copy(src, dest, **kwargs):
            result = copytree(src, dest, **kwargs)
            (target / "demo").mkdir()
            return result

        with patch.object(manager.shutil, "copytree", competing_copy):
            with self.assertRaisesRegex(ValueError, "destination appeared"):
                manager.install("demo", target)
        self.assertEqual(list((target / "demo").iterdir()), [])

    def test_update_preserves_changes_during_copy(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        copytree = shutil.copytree

        def editing_copy(src, dest, **kwargs):
            result = copytree(src, dest, **kwargs)
            (target / "demo/SKILL.md").write_text("edit during copy")
            return result

        with patch.object(manager.shutil, "copytree", editing_copy):
            with self.assertRaisesRegex(ValueError, "changed during update"):
                manager.install("demo", target, update=True)
        self.assertEqual((target / "demo/SKILL.md").read_text(), "edit during copy")
        self.assertEqual(list(target.glob(".sdkit-*")), [])

    def test_install_source_change_during_copy(self):
        target = self.root / "agent"
        target.mkdir()
        copytree = shutil.copytree

        def editing_copy(src, dest, **kwargs):
            result = copytree(src, dest, **kwargs)
            (src / "SKILL.md").write_text("changed source")
            return result

        with patch.object(manager.shutil, "copytree", editing_copy):
            with self.assertRaisesRegex(ValueError, "source changed"):
                manager.install("demo", target)
        self.assertEqual(list(target.iterdir()), [])

    def test_update_requires_record_and_existing_installation(self):
        target = self.root / "agent"
        target.mkdir()
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)
        (target / "demo").mkdir()
        (target / "demo/private.txt").write_text("keep")
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)
        self.assertEqual((target / "demo/private.txt").read_text(), "keep")

    def test_install_source_destination_overlap(self):
        for target in (self.root / "skills", self.root / "skills/demo"):
            with self.assertRaisesRegex(ValueError, "overlap"):
                manager.install("demo", target)

    def test_update_rejects_symlinked_record_and_installed_file(self):
        target = self.root / "agent"
        target.mkdir()
        manager.install("demo", target)
        record = target / "demo" / manager.RECORD
        original = record.read_bytes()
        record.unlink()
        record.symlink_to(self.catalog)
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)
        record.unlink()
        record.write_bytes(original)
        entry = target / "demo/SKILL.md"
        entry.unlink()
        entry.symlink_to(self.root / "skills/demo/SKILL.md")
        with self.assertRaises(ValueError):
            manager.install("demo", target, update=True)

    def test_frontmatter_identity_and_extra_fields(self):
        entry = self.root / "skills/demo/SKILL.md"
        for body in ("---\nname: wrong\ndescription: Test\n---\n",
                     "---\nname: demo\ndescription: Test\nallowed-tools: shell\n---\n",
                     "---\nname: demo\ndescription: \n---\n"):
            entry.write_text(body)
            with self.assertRaises(ValueError):
                manager.validate(all_skills=True)

    def test_catalog_duplicate_stale_and_unknown_category(self):
        original = json.loads(self.catalog.read_text())
        for item in ({"name": "demo", "category": "language", "path": "skills/demo"},
                     {"name": "absent", "category": "language", "path": "skills/absent"},
                     {"name": "other", "category": "unknown", "path": "skills/other"}):
            self.catalog.write_text(json.dumps({**original, "skills": original["skills"] + [item]}))
            with self.assertRaises(ValueError):
                manager.validate(all_skills=True)


if __name__ == "__main__":
    unittest.main()
