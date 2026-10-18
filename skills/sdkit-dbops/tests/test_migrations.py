import importlib.util
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/check_migrations.py"
spec = importlib.util.spec_from_file_location("dbops_checker", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MigrationTests(unittest.TestCase):
    def test_valid_file_and_hash(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            folder = root / "database/migrations"
            folder.mkdir(parents=True)
            (folder / "20261018T053000Z_a83f2c_add_avatar.sql").write_text("ALTER TABLE users ADD COLUMN avatar text;")
            out = module.inspect(root, "postgres", "single")
            self.assertEqual(out["status"], "review_required")
            self.assertEqual(len(out["migrations"][0]["sha256"]), 64)
            self.assertIn("ALTER", out["migrations"][0]["riskTokens"])
            self.assertFalse(out["databaseConnected"])

    def test_invalid_filename(self):
        with tempfile.TemporaryDirectory() as td:
            folder = pathlib.Path(td) / "database/migrations"
            folder.mkdir(parents=True)
            (folder / "001.sql").write_text("SELECT 1")
            with self.assertRaises(ValueError):
                module.inspect(pathlib.Path(td), "postgres", "single")

    def test_multi_dialect(self):
        with tempfile.TemporaryDirectory() as td:
            (pathlib.Path(td) / "database/mysql/migrations").mkdir(parents=True)
            self.assertEqual(module.inspect(pathlib.Path(td), "mysql", "multi")["status"], "empty")

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            target = root / "actual"
            target.mkdir()
            (root / "database").mkdir()
            (root / "database/migrations").symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                module.inspect(root, "postgres", "single")

    def test_invalid_timestamp(self):
        with tempfile.TemporaryDirectory() as td:
            folder = pathlib.Path(td) / "database/migrations"
            folder.mkdir(parents=True)
            (folder / "20261399T259999Z_a83f2c_bad.sql").write_text("SELECT 1")
            with self.assertRaisesRegex(ValueError, "timestamp"):
                module.inspect(pathlib.Path(td), "postgres", "single")

    def test_cross_dialect_collision(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            name = "20261018T053000Z_a83f2c_add_avatar.sql"
            for dialect in ("postgres", "mysql"):
                folder = root / "database" / dialect / "migrations"
                folder.mkdir(parents=True)
                (folder / name).write_text("SELECT 1")
            with self.assertRaisesRegex(ValueError, "collision"):
                module.inspect(root, "postgres", "multi")

    def test_parent_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            actual = root / "actual"
            (actual / "migrations").mkdir(parents=True)
            (root / "database").symlink_to(actual, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                module.inspect(root, "postgres", "single")

if __name__ == "__main__":
    unittest.main()
