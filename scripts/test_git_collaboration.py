"""Git Collaboration V1 low-cost static contract checks."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "standards/git-collaboration.md"


class GitCollaborationContract(unittest.TestCase):
    def test_protocol_sections(self):
        text = PROTOCOL.read_text(encoding="utf-8")
        for token in ("Preflight", "Worktree", "授权与 Git 写入", "PR/MR", "失败恢复", "Provider", "完成标准"):
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_safety_invariants(self):
        text = PROTOCOL.read_text(encoding="utf-8")
        for token in ("UNKNOWN", "reset --hard", "force push", "git add -A", "ff-only", "独立", "不得"):
            with self.subTest(token=token):
                self.assertIn(token, text)

    def test_git_init_safety(self):
        text = PROTOCOL.read_text(encoding="utf-8")
        section = text.split("## Git 初始化与嵌套仓库保护", 1)[1].split("## Remote 独立授权", 1)[0]
        for token in ("git init", "父级 Git Worktree", "子模块", "符号链接", "不得自动初始化", "不授权 Stage"):
            with self.subTest(token=token):
                self.assertIn(token, section)

    def test_remote_authorization(self):
        text = PROTOCOL.read_text(encoding="utf-8")
        section = text.split("## Remote 独立授权", 1)[1].split("## 分支与 Worktree", 1)[0]
        for token in ("git remote add", "git remote set-url", "git remote rename",
                      "git remote remove", "明确", "fetch/push URL", "upstream", "读回验证"):
            with self.subTest(token=token):
                self.assertIn(token, section)

    def test_integration_links(self):
        for relative in (
            "AGENTS.md",
            "standards/skill-orchestration.md",
            "standards/development-execution.md",
            "standards/collaboration-awareness.md",
        ):
            with self.subTest(path=relative):
                self.assertIn("git-collaboration.md", (ROOT / relative).read_text(encoding="utf-8"))

    def test_standalone_skills(self):
        for relative in (
            "skills/foundry/references/publishing.md",
            "skills/wikiops/references/repository.md",
        ):
            with self.subTest(path=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("独立安装", content)
                self.assertIn("不得", content)

    def test_bootstrap_coexists(self):
        text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("## Git Collaboration\n"), 1)
        self.assertEqual(text.count("## Project Skill Bootstrap\n"), 1)
        self.assertIn("不构成额外写入或部署授权", text)
        self.assertIn("全局配置修改同样需要独立授权和可恢复备份", text)

    def test_reference_completion_remains_last(self):
        for relative in ("skills/foundry/references/publishing.md",
                         "skills/wikiops/references/repository.md"):
            with self.subTest(path=relative):
                text = (ROOT / relative).read_text(encoding="utf-8")
                self.assertEqual(text.rsplit("\n## ", 1)[1].splitlines()[0], "完成标准")

    def test_relative_links(self):
        import re
        for path in (PROTOCOL, ROOT / "standards/skill-orchestration.md",
                     ROOT / "standards/development-execution.md",
                     ROOT / "standards/collaboration-awareness.md"):
            for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", path.read_text(encoding="utf-8")):
                if "://" not in link:
                    with self.subTest(path=str(path), link=link):
                        self.assertTrue((path.parent / link).exists())


if __name__ == "__main__":
    unittest.main()
