"""WikiOps workspace resolver regression tests. Run: python -m unittest discover -s skills/foundry/tests -v"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workspace.py"

class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = self.root / "config.json"

    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--config", str(self.config), *args],
                              cwd=cwd or self.root, capture_output=True, text=True)

    def repo(self, remote="git@github.com:example/docs.git"):
        path = self.root / "docs"
        path.mkdir(exist_ok=True)
        subprocess.run(["git", "init", "-q", str(path)], check=True)
        subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote], check=True)
        return path

    def test_init_idempotent_and_empty_override(self):
        self.assertEqual(self.run_cli("init").returncode, 0)
        self.assertEqual(self.run_cli("init").returncode, 0)
        data = json.loads(self.config.read_text())
        self.assertEqual(data["workspaces"], {})
        self.assertIsNone(data["primary_workspace"])
        self.assertNotEqual(self.run_cli("resolve").returncode, 0)

    def test_default_config_is_in_shared_personal_directory(self):
        env = dict(os.environ, HOME=str(self.root))
        command = [sys.executable, str(SCRIPT)]
        result = subprocess.run(command + ["init"], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.root / ".config" / "sdkit" / "skills" / "wikiops" / "config.json"
        self.assertIsNone(json.loads(config.read_text())["primary_workspace"])
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        self.assertEqual(subprocess.run(command + ["list"], env=env, capture_output=True, text=True).returncode, 0)
        self.assertFalse((self.root / ".config" / "wikiops").exists())

    def test_add_and_local_match(self):
        repo = self.repo()
        self.run_cli("init")
        result = self.run_cli("add", "personal", "https://github.com/example/docs.git",
                              "--provider", "github", "--path", str(repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("resolve")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "local")

    def test_duplicate_does_not_overwrite(self):
        self.run_cli("init")
        args = ("add", "personal", "git@github.com:example/docs.git", "--provider", "github")
        self.assertEqual(self.run_cli(*args).returncode, 0)
        self.assertNotEqual(self.run_cli(*args).returncode, 0)

    def test_mismatch_fails_closed(self):
        repo = self.repo("git@github.com:someone/else.git")
        self.run_cli("init")
        self.run_cli("add", "personal", "git@github.com:example/docs.git",
                     "--provider", "github", "--path", str(repo))
        result = self.run_cli("resolve")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('"mode": "remote"', result.stdout)

    def test_missing_local_falls_back(self):
        self.run_cli("init")
        self.run_cli("add", "personal", "git@gitlab.example.com:team/docs.git",
                     "--provider", "gitlab")
        result = self.run_cli("resolve")
        self.assertEqual(json.loads(result.stdout)["mode"], "remote")

    def test_invalid_config(self):
        self.config.write_text("{not-json")
        self.assertNotEqual(self.run_cli("list").returncode, 0)

    def test_invalid_url(self):
        self.run_cli("init")
        result = self.run_cli("add", "personal", "example/docs", "--provider", "github")
        self.assertNotEqual(result.returncode, 0)


    def test_dirty_local_repo_is_reported(self):
        repo = self.repo()
        (repo / "untracked.txt").write_text("pending")
        self.run_cli("init")
        self.run_cli("add", "personal", "https://github.com/example/docs.git",
                     "--provider", "github", "--path", str(repo))
        result = self.run_cli("resolve")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["mode"], "local")
        self.assertTrue(data["dirty"])

    def test_multiple_workspace_selection(self):
        self.run_cli("init")
        self.assertEqual(self.run_cli("add", "first", "git@github.com:example/one.git",
                                      "--provider", "github").returncode, 0)
        self.assertEqual(self.run_cli("add", "second", "git@gitee.com:example/two.git",
                                      "--provider", "gitee").returncode, 0)
        data = json.loads(self.run_cli("resolve", "second").stdout)
        self.assertEqual(data["workspace"], "second")
        self.assertEqual(data["provider"], "gitee")

if __name__ == "__main__":
    unittest.main()
