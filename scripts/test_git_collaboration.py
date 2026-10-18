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
