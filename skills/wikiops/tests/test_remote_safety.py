"""Git Remote 异常与本地配置保护回归；仅使用临时本地仓库。"""
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workspace.py"
spec = importlib.util.spec_from_file_location("wikiops_workspace", SCRIPT)
workspace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workspace)
URL = "https://github.com/example/docs.git"
OTHER = "https://github.com/example/other.git"


class RemoteSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "repo"
        self.run_git("init", "-q", str(self.repo), cwd=self.root)
        self.run_git("remote", "add", "origin", URL)
        self.run_git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                     "commit", "--allow-empty", "-qm", "base")
        self.data = {"version": 1, "primary_workspace": "test", "workspaces": {
            "test": {"repository": {"provider": "github", "url": URL}}}}

    def run_git(self, *args, cwd=None):
        return subprocess.run(["git", "-C", str(cwd or self.repo), *args],
                              capture_output=True, text=True, check=True).stdout.strip()

    def test_current_directory_push_mismatch_stops_remote_fallback(self):
        self.run_git("remote", "set-url", "--push", "origin", OTHER)
        with self.assertRaises(ValueError):
            workspace.resolve(self.data, None, self.repo)

    def test_multiple_push_destinations_are_all_verified(self):
        self.data["workspaces"]["test"]["repository"]["local_path"] = str(self.repo)
        self.run_git("remote", "set-url", "--push", "origin", URL)
        self.run_git("remote", "set-url", "--add", "--push", "origin", OTHER)
        with self.assertRaises(ValueError):
            workspace.resolve(self.data, None, self.root)

    def test_multiple_fetch_destinations_are_all_verified(self):
        self.run_git("remote", "set-url", "--add", "origin", OTHER)
        with self.assertRaises(ValueError):
            workspace.resolve(self.data, None, self.repo)

    def test_current_directory_non_origin_match_stops_remote_fallback(self):
        self.run_git("remote", "rename", "origin", "upstream")
        with self.assertRaises(ValueError):
            workspace.resolve(self.data, None, self.repo)

    def test_unrelated_current_directory_can_use_remote(self):
        self.run_git("remote", "set-url", "origin", OTHER)
        self.assertEqual(workspace.resolve(self.data, None, self.repo)["mode"], "remote")

    def test_current_subdirectory_resolves_parent_repository(self):
        nested = self.repo / "nested"
        nested.mkdir()
        result = workspace.resolve(self.data, None, nested)
        self.assertEqual(result["path"], str(self.repo))
        self.assertTrue(result["fetch_push_verified"])

    def test_existing_temporary_configuration_is_preserved(self):
        config = self.root / "config.json"
        config.write_text(json.dumps(self.data))
        pending = self.root / "config.json.tmp"
        pending.write_text("another writer")
        before = config.read_bytes()
        with self.assertRaises(FileExistsError):
            workspace.save(config, self.data)
        self.assertEqual(config.read_bytes(), before)
        self.assertEqual(pending.read_text(), "another writer")

    def test_fetch_guard_blocks_detached_and_missing_upstream_without_fetch(self):
        config = self.root / "config.json"
        config.write_text(json.dumps(self.data))
        self.run_git("checkout", "--detach", "-q")
        real_git = workspace.git
        calls = []

        def record(cwd, *args):
            calls.append(args)
            return real_git(cwd, *args)

        with patch.object(Path, "cwd", return_value=self.repo), patch.object(workspace, "git", side_effect=record):
            with self.assertRaises(ValueError):
                workspace.main(["--config", str(config), "sync-check", "--fetch"])
        self.assertFalse(any(args[0] == "fetch" for args in calls))


if __name__ == "__main__":
    unittest.main()
