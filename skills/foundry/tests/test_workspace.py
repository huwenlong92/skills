"""Foundry workspace resolver regression tests. Run: python -m unittest discover -s skills/foundry/tests -v"""
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
        config = self.root / ".config" / "sdkit" / "skills" / "foundry" / "config.json"
        self.assertIsNone(json.loads(config.read_text())["primary_workspace"])
        self.assertEqual(config.stat().st_mode & 0o777, 0o600)
        result = subprocess.run(command + ["list"], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["workspaces"], [])
        self.assertFalse((self.root / ".config" / "foundry").exists())

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


    def test_default_config_read_without_user_file(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["source"], "skill-default")
        self.assertEqual(data["primary_workspace"], "personal")

    def test_primary_switch_and_path_update(self):
        self.run_cli("init")
        self.run_cli("add", "personal", "git@github.com:example/docs.git", "--provider", "github")
        self.run_cli("add", "team", "git@gitlab.example.com:team/docs.git", "--provider", "gitlab")
        self.assertEqual(self.run_cli("set-primary", "team").returncode, 0)
        self.assertEqual(self.run_cli("set-path", "team", str(self.root / "team")).returncode, 0)
        data = json.loads(self.config.read_text())
        self.assertEqual(data["primary_workspace"], "team")
        self.assertEqual(data["workspaces"]["team"]["repository"]["local_path"], str(self.root / "team"))
        self.assertEqual(self.run_cli("remove", "team").returncode, 0)
        self.assertIsNone(json.loads(self.config.read_text())["primary_workspace"])

    def test_active_workspace_override_is_not_persisted(self):
        self.run_cli("init")
        self.run_cli("add", "personal", "git@github.com:example/docs.git", "--provider", "github")
        self.run_cli("add", "team", "git@gitlab.example.com:team/docs.git", "--provider", "gitlab")
        result = self.run_cli("resolve", "--active", "team")
        self.assertEqual(json.loads(result.stdout)["workspace"], "team")
        self.assertEqual(json.loads(self.config.read_text())["primary_workspace"], "personal")

    def test_dirty_worktree_and_detached_head(self):
        repo = self.repo()
        subprocess.run(["git", "-C", str(repo), "-c", "user.email=test@example.com",
                        "-c", "user.name=Test", "commit", "--allow-empty", "-qm", "initial"], check=True)
        (repo / "note.txt").write_text("dirty")
        self.run_cli("init")
        self.run_cli("add", "personal", "git@github.com:example/docs.git",
                     "--provider", "github", "--path", str(repo))
        result = self.run_cli("resolve")
        self.assertTrue(json.loads(result.stdout)["dirty"])
        subprocess.run(["git", "-C", str(repo), "checkout", "--detach", "-q"], check=True)
        result = self.run_cli("resolve")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(json.loads(result.stdout)["branch"])

    def test_invalid_primary_is_rejected(self):
        self.config.write_text(json.dumps({"version": 1, "primary_workspace": "missing", "workspaces": {}}))
        self.assertNotEqual(self.run_cli("list").returncode, 0)


    def test_upstream_ahead_behind_without_network(self):
        bare = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
        work = self.root / "work"
        subprocess.run(["git", "clone", "-q", str(bare), str(work)], check=True)
        subprocess.run(["git", "-C", str(work), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(work), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(work), "commit", "--allow-empty", "-qm", "base"], check=True)
        subprocess.run(["git", "-C", str(work), "push", "-q", "-u", "origin", "HEAD"], check=True)
        self.run_cli("init")
        self.run_cli("add", "personal", "git@github.com:example/docs.git", "--provider", "github", "--path", str(work))
        # Local file remotes are deliberately not accepted as configured public Git URLs.
        # Use a GitHub-shaped remote identity while retaining the local upstream tracking ref.
        subprocess.run(["git", "-C", str(work), "remote", "set-url", "origin", "git@github.com:example/docs.git"], check=True)
        result = self.run_cli("resolve")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual((data["behind"], data["ahead"]), (0, 0))
        preflight = self.run_cli("sync-check")
        self.assertEqual(json.loads(preflight.stdout)["sync_status"], "up-to-date")
        subprocess.run(["git", "-C", str(work), "commit", "--allow-empty", "-qm", "local"], check=True)
        result = self.run_cli("resolve")
        data = json.loads(result.stdout)
        self.assertEqual((data["behind"], data["ahead"]), (0, 1))
        preflight = self.run_cli("sync-check")
        self.assertEqual(json.loads(preflight.stdout)["sync_status"], "push-candidate")

    def test_clean_fast_forward_and_divergence_are_git_guardrails(self):
        bare = self.root / "remote.git"
        subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
        first = self.root / "first"
        subprocess.run(["git", "clone", "-q", str(bare), str(first)], check=True)
        for repo in (first,):
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(first), "commit", "--allow-empty", "-qm", "base"], check=True)
        subprocess.run(["git", "-C", str(first), "push", "-q", "-u", "origin", "HEAD"], check=True)
        second = self.root / "second"
        subprocess.run(["git", "clone", "-q", str(bare), str(second)], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", str(second), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(first), "commit", "--allow-empty", "-qm", "remote-update"], check=True)
        subprocess.run(["git", "-C", str(first), "push", "-q", "origin", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(second), "fetch", "-q", "origin"], check=True)
        subprocess.run(["git", "-C", str(second), "pull", "-q", "--ff-only"], check=True)
        subprocess.run(["git", "-C", str(second), "commit", "--allow-empty", "-qm", "local-update"], check=True)
        subprocess.run(["git", "-C", str(first), "commit", "--allow-empty", "-qm", "another-remote"], check=True)
        subprocess.run(["git", "-C", str(first), "push", "-q", "origin", "HEAD"], check=True)
        subprocess.run(["git", "-C", str(second), "fetch", "-q", "origin"], check=True)
        blocked = subprocess.run(["git", "-C", str(second), "pull", "--ff-only"], capture_output=True)
        self.assertNotEqual(blocked.returncode, 0)
        blocked_push = subprocess.run(["git", "-C", str(second), "push", "origin", "HEAD"], capture_output=True)
        self.assertNotEqual(blocked_push.returncode, 0)

if __name__ == "__main__":
    unittest.main()
