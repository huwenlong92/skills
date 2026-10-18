"""Static contract tests for sdkit-ui-design V1.1 (no network or writes)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sdkit-ui-design"
BASELINE = SKILL / "references" / "baseline.md"
HANDOFF = SKILL / "references" / "handoff.md"
REVIEW = SKILL / "references" / "review.md"


class DesignBaselineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        cls.baseline = BASELINE.read_text(encoding="utf-8")
        cls.handoff = HANDOFF.read_text(encoding="utf-8")
        cls.review = REVIEW.read_text(encoding="utf-8")
        cls.readme = (SKILL / "README.md").read_text(encoding="utf-8")

    def test_entry_declares_reference(self):
        self.assertIn("references/baseline.md", self.entry)

    def test_links_resolve(self):
        for source in (SKILL / "SKILL.md", BASELINE, HANDOFF, REVIEW, SKILL / "README.md"):
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", source.read_text(encoding="utf-8")):
                if "://" not in target:
                    with self.subTest(source=source.name, target=target):
                        self.assertTrue((source.parent / target).is_file())

    def test_archive_gates(self):
        for term in ("Foundry", "AGENTS.md", "BLOCKED", "写入授权", "原始图片", "SHA-256", "读回", "Worktree"):
            with self.subTest(term=term):
                self.assertIn(term, self.baseline)

    def test_idempotency_and_history(self):
        for term in ("相同 SHA-256", "同名", "修订", "禁止覆盖", "DESIGN.md", "并发"):
            with self.subTest(term=term):
                self.assertIn(term, self.baseline)

    def test_project_ownership(self):
        for term in ("已立项", "未立项", "Workspace", "迁移", "历史只读"):
            with self.subTest(term=term):
                self.assertIn(term, self.baseline)

    def test_modes(self):
        for term in ("production", "prototype", "undecided"):
            with self.subTest(term=term):
                self.assertIn(term, self.baseline)
                self.assertIn(term, self.handoff)

    def test_git_authorization_boundary(self):
        for term in ("Commit", "Push", "PR", "Merge", "Deploy"):
            with self.subTest(term=term):
                self.assertIn(term, self.baseline)

    def test_visual_review(self):
        for term in ("SHA-256", "视口", "截图", "交互", "差异"):
            with self.subTest(term=term):
                self.assertIn(term, self.review)

    def test_readme_documents_fallback(self):
        self.assertIn("BLOCKED", self.readme)
        self.assertIn("Codex", self.readme)

    def test_only_standard_frontmatter(self):
        match = re.match(r"\A---\n(.*?)\n---", self.entry, re.S)
        self.assertIsNotNone(match)
        keys = re.findall(r"^([\w-]+):", match.group(1), re.M)
        self.assertEqual(keys, ["name", "description"])


if __name__ == "__main__":
    unittest.main()
