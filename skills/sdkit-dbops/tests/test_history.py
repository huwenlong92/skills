import importlib.util
import pathlib
import unittest
p = pathlib.Path(__file__).resolve().parents[1] / "scripts/validate_history.py"
spec = importlib.util.spec_from_file_location("dbops_history", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
MID = "20261018T053000Z_a83f2c_add_avatar"
class HistoryTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(mod.validate({"migrations":[{"migrationId":MID,"checksum":"a"*64,"status":"applied"}]})["count"],1)
    def test_duplicate(self):
        m={"migrationId":MID,"checksum":"a"*64,"status":"applied"}
        with self.assertRaises(ValueError):mod.validate({"migrations":[m,m]})
    def test_unresolved(self):
        with self.assertRaises(ValueError):mod.validate({"migrations":[],"attempts":[{"status":"failed"}]})
    def test_invalid_date(self):
        with self.assertRaises(ValueError):mod.validate({"migrations":[{"migrationId":"20261399T259999Z_a83f2c_bad","checksum":"a"*64,"status":"applied"}]})
