import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("catalog.py")
spec = importlib.util.spec_from_file_location("catalog", SCRIPT)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.base = self.root / "node/22-bookworm-slim"
        self.base.mkdir(parents=True)
        (self.root / "images.txt").write_text("node/22-bookworm-slim\n")
        self.source = "docker.io/library/node:22-bookworm-slim"
        self.target = "registry.example.invalid/mirror/node:22-bookworm-slim"
        self.index = "sha256:" + "a" * 64
        self.child = "sha256:" + "b" * 64
        self.config = {"SOURCE_IMAGE": self.source, "TARGET_IMAGE": self.target, "PLATFORM": "linux/amd64,linux/arm64"}
        self.lock = {
            "source_image": self.source, "target_image": self.target,
            "platform": self.config["PLATFORM"], "source_digest": "sha256:" + "c" * 64,
            "target_digest": self.index, "target_pinned_image": self.target + "-sha-" + "a" * 12,
            "synced_at": "2026-01-01T00:00:00Z",
            **{f"{side}_linux_{arch}_digest": self.child for side in ("source", "target") for arch in ("amd64", "arm64")},
        }
        self.write_config()
        self.write_lock()

    def tearDown(self):
        self.temp.cleanup()

    def write_config(self):
        (self.base / "image.conf").write_text("".join(f"{key}={value}\n" for key, value in self.config.items()))

    def write_lock(self):
        (self.base / "digest.lock").write_text("".join(f"{key}={value}\n" for key, value in self.lock.items()))

    def record(self):
        return catalog.catalogue(self.root)[0][0]

    def test_valid_record_is_read_only_and_not_remote_proof(self):
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        records, issues = catalog.catalogue(self.root)
        self.assertEqual(issues, [])
        self.assertEqual(records[0]["status"], "recorded")
        self.assertFalse(records[0]["remote_verified"])
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_missing_lock_is_unrecorded(self):
        (self.base / "digest.lock").unlink()
        self.assertEqual(self.record()["status"], "unrecorded")

    def test_empty_lock_is_inconsistent(self):
        (self.base / "digest.lock").write_text("")
        self.assertEqual(self.record()["status"], "inconsistent")

    def test_single_arch_is_rejected(self):
        self.config["PLATFORM"] = "linux/amd64"
        self.write_config()
        self.assertEqual(self.record()["status"], "inconsistent")

    def test_child_mismatch_and_missing_digest_are_detected(self):
        self.lock["target_linux_arm64_digest"] = "sha256:" + "d" * 64
        self.lock.pop("source_linux_amd64_digest")
        self.write_lock()
        issues = self.record()["issues"]
        self.assertTrue(any("child mismatch" in x for x in issues))
        self.assertTrue(any("missing or invalid" in x for x in issues))

    def test_config_and_pin_drift_are_detected(self):
        self.lock["target_image"] = self.target + "-different"
        self.lock["target_pinned_image"] = self.target + "-sha-incorrect"
        self.write_lock()
        self.assertEqual(self.record()["status"], "inconsistent")

    def test_duplicate_manifest_entry_and_target_are_detected(self):
        second = self.root / "node/other"
        second.mkdir()
        (second / "image.conf").write_text((self.base / "image.conf").read_text())
        (self.root / "images.txt").write_text("node/22-bookworm-slim\nnode/22-bookworm-slim\nnode/other\n")
        issues = catalog.catalogue(self.root)[1]
        self.assertTrue(any("duplicate images.txt" in x for x in issues))
        self.assertTrue(any("duplicate target" in x for x in issues))

    def test_shell_config_is_never_executed(self):
        sentinel = self.root / "executed"
        (self.base / "image.conf").write_text(f"SOURCE_IMAGE=$(touch {sentinel})\n")
        records, issues = catalog.catalogue(self.root)
        self.assertEqual(records, [])
        self.assertTrue(issues)
        self.assertFalse(sentinel.exists())

    def test_traversal_and_external_symlink_are_rejected(self):
        (self.root / "images.txt").write_text("../outside\n")
        self.assertTrue(catalog.catalogue(self.root)[1])
        (self.root / "images.txt").write_text("node/22-bookworm-slim\n")
        (self.base / "image.conf").unlink()
        (self.base / "image.conf").symlink_to(SCRIPT)
        self.assertTrue(catalog.catalogue(self.root)[1])

    def test_builder_discovery_includes_unpublished_recipe(self):
        base = self.root / "go-builder/toolchain"
        base.mkdir(parents=True)
        (base / "Dockerfile").write_text("FROM scratch\n")
        records, issues = catalog.catalogue(self.root)
        self.assertEqual(issues, [])
        self.assertEqual(records[1]["kind"], "builder")
        self.assertEqual(records[1]["status"], "unrecorded")
        data = {"image": "registry.example.invalid/mirror/go-builder:release", "alias_image": "registry.example.invalid/mirror/go-builder:line", "digest": self.index,
                "amd64_digest": self.child, "arm64_digest": self.child, "platform": "linux/amd64,linux/arm64", "published_at": "2026-01-01T00:00:00Z", "source_image": self.target + "@" + self.index}
        (base / "go-builder.lock").write_text("".join(f"{k}={v}\n" for k,v in data.items()))
        self.assertEqual(catalog.catalogue(self.root)[0][1]["status"], "recorded")

    def test_binding_order_and_config_relative_path(self):
        config = self.root / "config.json"
        config.write_text(json.dumps({"mirror_repo": "."}))
        with patch.dict(os.environ, {"DOCKEROPS_CONFIG": str(config)}, clear=True):
            self.assertEqual(catalog.repository(None), self.root)
            with patch.dict(os.environ, {"DOCKEROPS_MIRROR_REPO": str(self.base)}):
                self.assertEqual(catalog.repository(None), self.base)
                self.assertEqual(catalog.repository(str(self.root)), self.root)
        config.write_text("{}")
        with patch.dict(os.environ, {"DOCKEROPS_CONFIG": str(config)}, clear=True):
            with self.assertRaises(ValueError):
                catalog.repository(None)

    def test_filter_does_not_hide_global_errors(self):
        (self.root / "images.txt").write_text("node/22-bookworm-slim\nnode/22-bookworm-slim\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.root), "--search", "absent"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        data = json.loads(result.stdout)
        self.assertEqual(data["images"], [])
        self.assertTrue(data["issues"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
