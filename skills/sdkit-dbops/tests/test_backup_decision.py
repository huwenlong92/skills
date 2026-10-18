import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/backup_decision.py"
s=importlib.util.spec_from_file_location("dbops_backup",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def request():
    return {"operationRisk":"destructive","databaseSizeBytes":200_000_000_000,"affectedSizeBytes":80_000_000_000,"rpoSeconds":300,"rtoSeconds":3600,"recoveryOptions":[]}
class BackupTests(unittest.TestCase):
    def test_no_recovery_blocked(self):
        self.assertIsNone(m.decide(request())["recommendedStrategy"])
    def test_pitr_preferred_large_database(self):
        x=request();x["recoveryOptions"]=[{"strategy":"existing-pitr","coversAffectedObjects":True,"rpoSeconds":60,"rtoSeconds":600,"restoreVerified":True}]
        self.assertEqual(m.decide(x)["recommendedStrategy"],"existing-pitr")
        self.assertFalse(m.decide(x)["evidenceVerifiedByTool"])
    def test_invalid_size(self):
        x=request();x["affectedSizeBytes"]=300_000_000_000
        with self.assertRaises(ValueError):m.decide(x)
    def test_read_only(self):
        x=request();x["operationRisk"]="read_only"
        self.assertEqual(m.decide(x)["status"],"not_required")
