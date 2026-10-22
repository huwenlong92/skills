"""Offline regression cases: UTF-8 names, ASCII paths, hashes, ZIP and legacy path rejection."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("delivery", Path(__file__).resolve().parents[1]/"scripts"/"design_delivery.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

class DeliveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root/"source"
        self.source.mkdir()
        (self.source/"image.png").write_bytes(d.PNG+b"example")
        self.plan = self.root/"plan.json"
        self.plan.write_text(json.dumps({"pages":[{"id":"profile-home","name":"我的首页","module":"profile","selected":"image.png"}]},ensure_ascii=False),encoding="utf-8")
        self.out = self.root/"delivery"

    def test_build_verify(self):
        self.assertEqual(d.build(self.plan,self.source,self.out),1)
        manifest=json.loads((self.out/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["assets"][0]["page_name"],"我的首页")
        self.assertEqual(manifest["assets"][0]["path"],"selected/profile/profile-home.png")
        self.assertEqual(d.verify(self.out),1)

    def test_modified_png_detected(self):
        d.build(self.plan,self.source,self.out)
        (self.out/"selected/profile/profile-home.png").write_bytes(b"bad")
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_old_zip_path_rejected(self):
        d.build(self.plan,self.source,self.out)
        m=json.loads((self.out/"manifest.json").read_text())
        m["assets"][0]["original_zip_path"]="old/中文/old.png"
        (self.out/"manifest.json").write_text(json.dumps(m))
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_ascii_and_traversal(self):
        with self.assertRaises(ValueError): d.safe("../outside.png")
        with self.assertRaises(ValueError): d.safe("selected/中文.png")

    def test_no_overwrite(self):
        d.build(self.plan,self.source,self.out)
        with self.assertRaises(ValueError): d.build(self.plan,self.source,self.out)

    def test_duplicate_hash_report(self):
        plan=json.loads(self.plan.read_text())
        plan["pages"].append({"id":"another","name":"另一个","module":"profile","selected":"image.png"})
        self.plan.write_text(json.dumps(plan,ensure_ascii=False))
        d.build(self.plan,self.source,self.out)
        m=json.loads((self.out/"manifest.json").read_text())
        self.assertEqual(len(m["duplicate_sha256"]),1)

if __name__=="__main__": unittest.main()
