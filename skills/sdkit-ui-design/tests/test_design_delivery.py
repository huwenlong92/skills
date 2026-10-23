"""Offline regression cases: UTF-8 names, ASCII paths, hashes, ZIP and legacy path rejection."""
import importlib.util
import json
import tempfile
import unittest
import struct
import zlib
from pathlib import Path

spec = importlib.util.spec_from_file_location("delivery", Path(__file__).resolve().parents[1]/"scripts"/"design_delivery.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

class DeliveryTest(unittest.TestCase):
    @staticmethod
    def png():
        def chunk(tag, data):
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))
        return (d.PNG + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(b"\0\xff\x00\x00")) + chunk(b"IEND", b""))

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.source = self.root/"source"
        self.source.mkdir()
        (self.source/"image.png").write_bytes(self.png())
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

    def test_corrupt_png_rejected(self):
        for payload in (d.PNG+b"invalid", self.png()[:-7], self.png()[:-1]+b"X"):
            (self.source/"image.png").write_bytes(payload)
            with self.subTest(payload=payload[-8:]):
                with self.assertRaises(ValueError): d.build(self.plan,self.source,self.out)

    def test_duplicate_zip_entry_rejected(self):
        d.build(self.plan,self.source,self.out)
        archive=self.out/"profile.zip"
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",UserWarning)
            with d.zipfile.ZipFile(archive,"a") as z:
                z.writestr("selected/profile/profile-home.png",self.png())
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_invalid_manifest_module_rejected(self):
        d.build(self.plan,self.source,self.out)
        m=json.loads((self.out/"manifest.json").read_text())
        m["assets"][0]["module"]="unknown"
        (self.out/"manifest.json").write_text(json.dumps(m))
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_png_scanline_integrity(self):
        def chunk(tag, data):
            return struct.pack('>I', len(data))+tag+data+struct.pack('>I', zlib.crc32(tag+data))
        header = self.png()[:33]
        for raw in (b'\0', b'\x05\xff\0\0', b'\0\xff\0\0extra'):
            with self.subTest(raw=raw):
                payload = header+chunk(b'IDAT', zlib.compress(raw))+chunk(b'IEND', b'')
                self.assertFalse(d.valid_png(payload))

    def test_png_formats_and_compressed_stream(self):
        def chunk(tag, data):
            return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data))
        for depth,color,raw,palette in ((1,0,b'\0\0',b''),(8,6,b'\0\xff\0\0\xff',b''),(1,3,b'\0\0',chunk(b'PLTE',b'\xff\0\0'))):
            for interlace in (0,1):
                with self.subTest(depth=depth,color=color,interlace=interlace):
                    header=d.PNG+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,depth,color,0,0,interlace))
                    self.assertTrue(d.valid_png(header+palette+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')))
        header=self.png()[:33]
        for compressed in (zlib.compress(b'\0\xff\0\0')[:-1],zlib.compress(b'\0\xff\0\0')+b'extra'):
            self.assertFalse(d.valid_png(header+chunk(b'IDAT',compressed)+chunk(b'IEND',b'')))

    def test_source_symlinks_rejected(self):
        (self.source/'linked.png').symlink_to(self.source/'image.png')
        (self.source/'linked-dir').symlink_to(self.source, target_is_directory=True)
        for index,name in enumerate(('linked.png', 'linked-dir/image.png', '../outside.png', '/outside.png')):
            with self.subTest(name=name):
                plan = json.loads(self.plan.read_text())
                plan['pages'][0]['selected'] = name
                self.plan.write_text(json.dumps(plan))
                with self.assertRaises(ValueError): d.build(self.plan,self.source,self.root/f'out-{index}')

    def test_output_symlink_rejected(self):
        target = self.root/'outside'
        target.mkdir()
        self.out.symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError): d.build(self.plan,self.source,self.out)
        self.assertEqual(list(target.iterdir()), [])

    def test_delivery_symlinks_rejected(self):
        d.build(self.plan,self.source,self.out)
        for relative in ('manifest.json', 'profile.zip', 'selected/profile/profile-home.png', 'selected/profile'):
            with self.subTest(relative=relative):
                path = self.out/relative
                saved = self.root/('saved-'+path.name)
                path.rename(saved)
                path.symlink_to(saved, target_is_directory=saved.is_dir())
                try:
                    with self.assertRaises(ValueError): d.verify(self.out)
                finally:
                    path.unlink()
                    saved.rename(path)

    def test_zip_missing_and_changed_members(self):
        d.build(self.plan,self.source,self.out)
        for members in ({}, {'selected/profile/profile-home.png': b'changed'}, {'../escape.png': self.png()}):
            with self.subTest(members=list(members)):
                with d.zipfile.ZipFile(self.out/'profile.zip','w') as z:
                    for name,data in members.items(): z.writestr(name,data)
                with self.assertRaises(ValueError): d.verify(self.out)

    def test_missing_file_rejected(self):
        d.build(self.plan,self.source,self.out)
        (self.out/'selected/profile/profile-home.png').unlink()
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_manifest_required_fields_and_hashes(self):
        d.build(self.plan,self.source,self.out)
        original = json.loads((self.out/'manifest.json').read_text())
        import copy
        for field,value in (('sha256','0'*64),('bytes',True),('page_id','../bad'),('page_name',None),('status',None),('path','../escape.png')):
            with self.subTest(field=field):
                m = copy.deepcopy(original)
                m['assets'][0][field] = value
                (self.out/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError): d.verify(self.out)
        m = copy.deepcopy(original)
        del m['assets'][0]['page_name']
        (self.out/'manifest.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError): d.verify(self.out)

    def test_duplicate_manifest_metadata_rejected(self):
        plan = json.loads(self.plan.read_text())
        plan['pages'].append({'id':'another','name':'另一个','module':'profile','selected':'image.png'})
        self.plan.write_text(json.dumps(plan))
        d.build(self.plan,self.source,self.out)
        m = json.loads((self.out/'manifest.json').read_text())
        m['duplicate_sha256'] = {}
        (self.out/'manifest.json').write_text(json.dumps(m))
        with self.assertRaises(ValueError): d.verify(self.out)

if __name__=="__main__": unittest.main()
