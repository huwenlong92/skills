"""G01–G20：仅使用临时仓库的真实 Git CLI 夹具，非 Agent 行为测试。

运行：python3 scripts/test_git_collaboration_cli.py -v
可选 GIT_COLLABORATION_EVIDENCE 指定脱敏 JSON 输出；不写入用户 Git 配置。
授权类场景只验证检查所需 Git 事实与不写入后的保全，不声称 Git 自带授权阻断。
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


EVIDENCE = []


class GitCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="git-collaboration-cli-")
        self.root = Path(self.tmp.name).resolve()
        self.repo = self.root / "local"
        self.peer = self.root / "peer"
        self.remote = self.root / "remote.git"
        home = self.root / "home"
        home.mkdir()
        self.env = {"PATH": os.environ["PATH"], "HOME": str(home),
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_AUTHOR_NAME": "Fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                    "GIT_COMMITTER_NAME": "Fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
                    "GIT_TERMINAL_PROMPT": "0", "GIT_EDITOR": "true", "GIT_SEQUENCE_EDITOR": "true",
                    "LC_ALL": "C"}
        self.events = []
        self.git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(self.root, "init", "--initial-branch=main", str(self.repo))
        self.commit(self.repo, "data.txt", "base\n", "base")
        self.git(self.repo, "remote", "add", "origin", str(self.remote))
        self.git(self.repo, "push", "-u", "origin", "main")
        self.git(self.root, "clone", str(self.remote), str(self.peer))

    def tearDown(self):
        EVIDENCE.append({"id": self._testMethodName.split("_")[1], "test": self._testMethodName,
                         "commands": self.events})
        self.tmp.cleanup()  # 仅清理本测试创建的独立夹具。

    def git(self, cwd, *args, code=0):
        command = ["git", *args]
        p = subprocess.run(command, cwd=cwd, env=self.env, capture_output=True, text=True)
        redact = lambda value: value.replace(str(self.root), "<fixture>")
        self.events.append({"cwd": redact(str(cwd)), "argv": [redact(x) for x in command],
                            "exit_code": p.returncode, "stdout": redact(p.stdout), "stderr": redact(p.stderr)})
        if code is None:
            self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        else:
            self.assertEqual(p.returncode, code, p.stdout + p.stderr)
        return p.stdout.strip()

    def commit(self, repo, path, content, message):
        (repo / path).write_text(content)
        self.git(repo, "add", "--", path)
        self.git(repo, "commit", "-m", message)
        return self.git(repo, "rev-parse", "HEAD")

    def counts(self):
        return self.git(self.repo, "rev-list", "--left-right", "--count", "HEAD...@{upstream}").split()

    def advance(self, path="remote.txt", content="remote\n"):
        sha = self.commit(self.peer, path, content, "peer update")
        self.git(self.peer, "push", "origin", "main")
        return sha

    def test_G01_main(self):
        self.assertEqual(self.git(self.repo, "branch", "--show-current"), "main")
        self.commit(self.repo, "task.txt", "task\n", "single developer")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        self.assertEqual(self.counts(), ["1", "0"])

    def test_G02_fast_forward(self):
        target = self.advance()
        self.git(self.repo, "fetch", "origin")
        self.assertEqual(self.counts(), ["0", "1"])
        self.git(self.repo, "merge-base", "--is-ancestor", "HEAD", "origin/main")
        self.git(self.repo, "pull", "--ff-only")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), target)

    def test_G03_ahead_push(self):
        target = self.commit(self.repo, "task.txt", "task\n", "authorized task")
        self.git(self.repo, "fetch", "origin")
        self.assertEqual(self.counts(), ["1", "0"])
        # 本夹具明确授权普通 Push；权限/用户意图不是 Git 内置能力。
        self.git(self.repo, "push", "origin", "HEAD:main")
        self.assertTrue(self.git(self.repo, "ls-remote", "origin", "refs/heads/main").startswith(target))

    def test_G04_diverged(self):
        self.commit(self.repo, "local.txt", "local\n", "local")
        self.advance()
        self.git(self.repo, "fetch", "origin")
        self.assertEqual(self.counts(), ["1", "1"])
        before = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.repo, "pull", "--ff-only", code=None)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), before)

    def test_G05_dirty(self):
        (self.repo / "data.txt").write_text("private local edit\n")
        self.advance("data.txt", "peer edit\n")
        self.git(self.repo, "fetch", "origin")
        self.assertIn("data.txt", self.git(self.repo, "status", "--porcelain"))
        self.git(self.repo, "pull", "--ff-only", code=None)
        self.assertEqual((self.repo / "data.txt").read_text(), "private local edit\n")
        self.assertEqual(self.git(self.repo, "stash", "list"), "")

    def test_G06_untracked(self):
        (self.repo / "remote.txt").write_text("untracked sentinel\n")
        self.advance()
        self.git(self.repo, "fetch", "origin")
        self.git(self.repo, "pull", "--ff-only", code=None)
        self.assertEqual((self.repo / "remote.txt").read_text(), "untracked sentinel\n")

    def test_G07_upstream_missing(self):
        self.git(self.repo, "switch", "-c", "no-upstream")
        self.git(self.repo, "rev-parse", "--abbrev-ref", "@{upstream}", code=None)
        self.assertEqual(self.git(self.repo, "config", "--get-regexp", "^branch.no-upstream", code=1), "")

    def test_G08_worktree(self):
        other = self.root / "worktree"
        self.git(self.repo, "worktree", "list", "--porcelain")
        self.git(self.repo, "worktree", "add", "-b", "parallel", str(other))
        (other / "data.txt").write_text("parallel edit\n")
        self.assertEqual((self.repo / "data.txt").read_text(), "base\n")
        self.git(self.repo, "worktree", "add", str(self.root / "collision"), "parallel", code=None)

    def test_G09_parallel(self):
        self.commit(self.repo, "local.txt", "local\n", "local")
        self.advance()
        self.git(self.repo, "fetch", "origin")
        self.git(self.repo, "merge", "--no-ff", "origin/main", "-m", "integrate peer")
        self.assertEqual((self.repo / "local.txt").read_text(), "local\n")
        self.assertEqual((self.repo / "remote.txt").read_text(), "remote\n")

    def conflict(self, operation):
        base = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.repo, "switch", "-c", "topic")
        topic = self.commit(self.repo, "data.txt", "topic\n", "topic")
        self.git(self.repo, "switch", "main")
        self.commit(self.repo, "data.txt", "main\n", "main")
        if operation == "merge":
            self.git(self.repo, "merge", "topic", code=None)
        elif operation == "rebase":
            self.git(self.repo, "switch", "topic")
            self.git(self.repo, "rebase", "main", code=None)
        else:
            self.git(self.repo, "cherry-pick", topic, code=None)
        self.assertIn("data.txt", self.git(self.repo, "diff", "--name-only", "--diff-filter=U"))
        # 比较三个索引阶段；审查双方后明确合成，禁止无条件取一侧。
        for stage in (1, 2, 3):
            self.git(self.repo, "show", f":{stage}:data.txt")
        (self.repo / "data.txt").write_text("main\ntopic\n")
        self.git(self.repo, "add", "--", "data.txt")
        self.git(self.repo, operation, "--continue")
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")
        self.assertEqual((self.repo / "data.txt").read_text(), "main\ntopic\n")
        self.git(self.repo, "merge-base", "--is-ancestor", base, "HEAD")

    def test_G10_merge_recovery(self):
        self.conflict("merge")

    def test_G11_rebase_recovery(self):
        # 仅未发布的虚构 topic，非 PR 历史。
        self.conflict("rebase")

    def test_G12_cherry_pick_recovery(self):
        self.conflict("cherry-pick")

    def test_G13_rewritten_remote(self):
        old = self.git(self.repo, "rev-parse", "origin/main")
        self.git(self.peer, "switch", "--orphan", "replacement")
        new = self.commit(self.peer, "new.txt", "new history\n", "replacement fixture")
        self.git(self.peer, "push", "origin", "replacement")
        # 夹具服务端故障注入；不使用 Force Push，不接触真实仓库。
        self.git(self.remote, "update-ref", "refs/heads/main", new, old)
        self.git(self.repo, "fetch", "origin")
        self.git(self.repo, "merge-base", "--is-ancestor", old, "origin/main", code=1)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), old)

    def test_G14_push_rejected(self):
        self.commit(self.repo, "local.txt", "local\n", "local")
        remote = self.advance()
        self.git(self.repo, "push", "origin", "main", code=None)
        self.assertTrue(self.git(self.repo, "ls-remote", "origin", "refs/heads/main").startswith(remote))
        self.git(self.repo, "fetch", "origin")
        self.assertEqual(self.counts(), ["1", "1"])

    def test_G15_transport_failure(self):
        before = self.git(self.repo, "rev-parse", "HEAD")
        # 对本机保留低端口发起真实 Git 网络连接，不访问外部仓库。
        self.git(self.repo, "fetch", "git://localhost:1/fiction.git", code=None)
        self.git(self.repo, "ls-remote", "origin", "refs/heads/main")
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), before)
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")

    def test_G16_cleanup_gate(self):
        other = self.root / "cleanup"
        self.git(self.repo, "worktree", "add", "-b", "cleanup", str(other))
        (other / "sentinel").write_text("keep\n")
        self.assertIn("?? sentinel", self.git(other, "status", "--porcelain"))
        self.git(self.repo, "worktree", "remove", str(other), code=None)
        self.assertTrue((other / "sentinel").exists())
        # 明确清理授权仅覆盖本测试新建的 sentinel 与 Worktree。
        (other / "sentinel").unlink()
        self.git(other, "rev-list", "--count", "main..HEAD")
        self.git(self.repo, "worktree", "remove", str(other))
        self.assertFalse(other.exists())

    def test_G17_existing_init(self):
        before = (self.repo / ".git/config").read_bytes()
        head = self.git(self.repo, "rev-parse", "HEAD")
        self.git(self.repo, "rev-parse", "--show-toplevel")
        self.assertTrue((self.repo / ".git").is_dir())
        # 协议在已识别仓库不重复初始化；不依靠重初始化碰运气。
        self.assertEqual((self.repo / ".git/config").read_bytes(), before)
        self.assertEqual(self.git(self.repo, "rev-parse", "HEAD"), head)

    def test_G18_parent_nested(self):
        child = self.repo / "child"
        child.mkdir()
        index = (self.repo / ".git/index").read_bytes()
        self.assertEqual(Path(self.git(child, "rev-parse", "--show-toplevel")), self.repo)
        self.git(child, "rev-parse", "--show-superproject-working-tree")
        self.git(self.repo, "ls-files", "--stage", "--", "child")
        self.assertFalse((child / ".git").exists())
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_G19_unauthorized_remote(self):
        before = (self.repo / ".git/config").read_bytes()
        self.git(self.repo, "remote", "-v")
        self.git(self.repo, "config", "--show-origin", "--get-regexp", "^(remote|branch)\\.")
        # 无 Remote 写入授权：检查后不执行配置写入；不冒充 Agent 阻断。
        self.assertEqual((self.repo / ".git/config").read_bytes(), before)

    def test_G20_authorized_remote(self):
        self.git(self.repo, "config", "--show-origin", "--get-regexp", "^(remote|branch)\\.")
        url = "https://example.invalid/fixture/repository.git"
        self.git(self.repo, "remote", "add", "review", url)
        self.assertEqual(self.git(self.repo, "remote", "get-url", "review"), url)
        self.assertEqual(self.git(self.repo, "remote", "get-url", "--push", "review"), url)
        self.assertEqual(self.git(self.repo, "config", "--get", "remote.review.fetch"),
                         "+refs/heads/*:refs/remotes/review/*")
        # 夹具明确授权分别替换 fetch 与 push URL，并验证没有混淆。
        fetch = "https://example.invalid/fixture/replacement.git"
        push = "ssh://git@example.invalid/fixture/replacement.git"
        self.git(self.repo, "remote", "set-url", "review", fetch)
        self.git(self.repo, "remote", "set-url", "--push", "review", push)
        self.assertEqual(self.git(self.repo, "remote", "get-url", "review"), fetch)
        self.assertEqual(self.git(self.repo, "remote", "get-url", "--push", "review"), push)
        self.assertEqual(self.git(self.repo, "rev-parse", "--abbrev-ref", "@{upstream}"), "origin/main")
        self.git(self.repo, "config", "--show-origin", "--get-regexp", "^(remote|branch)\\.")


if __name__ == "__main__":
    program = unittest.main(exit=False)
    if os.environ.get("GIT_COLLABORATION_EVIDENCE"):
        Path(os.environ["GIT_COLLABORATION_EVIDENCE"]).write_text(
            json.dumps({"kind": "real-git-cli-not-agent", "tests": EVIDENCE,
                        "run": program.result.testsRun, "failures": len(program.result.failures),
                        "errors": len(program.result.errors)}, ensure_ascii=False, indent=2) + "\n")
    raise SystemExit(not program.result.wasSuccessful())
