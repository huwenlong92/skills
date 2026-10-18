import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/data_safety.py"
s=importlib.util.spec_from_file_location("dbops_data_safety",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class DataSafetyTests(unittest.TestCase):
    def test_truncate(self):
        self.assertEqual(m.assess([{"kind":"sql","text":"TRUNCATE TABLE public.users"}])["risk"],"destructive")
    def test_delete(self):
        self.assertEqual(m.assess([{"kind":"sql","text":"DELETE FROM users"}])["status"],"blocked")
    def test_protected(self):
        self.assertEqual(m.assess([{"kind":"sql","text":"DROP SCHEMA system_data CASCADE"}])["risk"],"destructive")
    def test_seed(self):
        self.assertEqual(m.assess([{"kind":"seed","text":"reset demo accounts"}])["status"],"blocked")
    def test_unknown(self):
        self.assertEqual(m.assess([])["status"],"unknown")
