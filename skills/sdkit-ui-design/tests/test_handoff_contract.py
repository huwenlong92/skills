"""#22 的十项静态契约回归，映射到 #33 唯一交接规则；不替代 Agent 行为验收。"""
from pathlib import Path
import re
import unittest

SKILL = Path(__file__).resolve().parents[1]


class HandoffContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entry = (SKILL/'SKILL.md').read_text(encoding='utf-8')
        cls.git = (SKILL/'references/git-handoff.md').read_text(encoding='utf-8')
        cls.handoff = (SKILL/'references/handoff.md').read_text(encoding='utf-8')
        cls.review = (SKILL/'references/review.md').read_text(encoding='utf-8')
        cls.readme = (SKILL/'README.md').read_text(encoding='utf-8')
        cls.mcp = (SKILL/'references/mcp-delivery.md').read_text(encoding='utf-8')

    def contains(self, text, terms):
        for term in terms:
            with self.subTest(term=term): self.assertIn(term, text)

    def test_entry_declares_single_handoff_authority(self):
        self.assertIn('references/git-handoff.md', self.entry)
        self.assertFalse((SKILL/'references/baseline.md').exists())

    def test_links_resolve(self):
        for source in SKILL.rglob('*.md'):
            for target in re.findall(r'\]\(([^)#]+)(?:#[^)]+)?\)', source.read_text(encoding='utf-8')):
                if '://' not in target:
                    with self.subTest(source=source.name, target=target):
                        self.assertTrue((source.parent/target).is_file())

    def test_archive_gates(self):
        self.contains(self.git, ('Foundry','AGENTS.md','写入授权','原始图片','SHA-256','读回','Worktree','敏感数据','禁止原样公开提交','停止写入'))

    def test_idempotency_and_history(self):
        self.contains(self.git, ('相同 Design ID 与相同字节 SHA-256','复用资源引用','不创建重复 Revision','同名但 SHA-256 不同','新的修订文件名','禁止覆盖原图','DESIGN.md 必须增量更新','保留已有有效内容和历史','并发索引变化时停止覆盖','保留恢复证据'))

    def test_project_ownership(self):
        self.contains(self.git, ('已立项','未立项','Workspace / Repository Resolver','迁移','来源/去向声明','旧资料历史只读','禁止形成两个可编辑权威源'))

    def test_modes_and_storage_boundary(self):
        for text in (self.git, self.handoff, self.mcp):
            self.contains(text, ('production','prototype','undecided'))
        self.contains(self.mcp, ('项目 Git 仓库不是 MCP 保存前提','ASSET_SAVED','GIT_HANDOFF_PENDING','artifact_begin','artifact_receive','artifact_commit','artifact_recover','artifact_download','原型源码','Foundry','不作为 V1 阻断条件'))

    def test_git_authorization_boundary(self):
        self.contains(self.git, ('Commit','Push','PR','Merge','独立授权','不得宣称仓库归档完成','不能以 MinIO vN 代替 Design Revision 或 Git Commit'))

    def test_visual_review(self):
        self.contains(self.review, ('Design ID','Design Revision','SHA-256','视口','截图','交互','差异','登记新 Revision'))

    def test_readme_documents_fallback(self):
        self.contains(self.readme, ('BLOCKED','Codex','GIT_HANDOFF_PENDING','只读讨论禁止归档写入','未执行项不得标为通过'))

    def test_only_standard_frontmatter(self):
        match = re.match(r'\A---\n(.*?)\n---', self.entry, re.S)
        self.assertIsNotNone(match)
        self.assertEqual(re.findall(r'^([\w-]+):', match.group(1), re.M), ['name','description'])


if __name__ == '__main__': unittest.main()
