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


    def test_project_resolution_priority_and_ambiguity(self):
        terms = ('1. 用户明确指定的项目标识', '2. 当前会话已确认的项目身份', '3. 当前 ChatGPT 项目的唯一业务产品身份', '4. 已核验的既有项目绑定')
        positions = [self.mcp.index(term) for term in terms]
        self.assertEqual(positions, sorted(positions))
        self.contains(self.mcp, ('不要求用户重复输入', '多个合理候选', '必须询问', '不能仅凭相似名称、目录名称或聊天标题', '不得假定宿主自动提供隐藏项目资料'))

    def test_independent_authorization_states(self):
        self.contains(self.mcp, ('PROJECT_IDENTIFIED', 'REGISTRATION_AUTHORIZED', 'SAVE_AUTHORIZED', 'ASSET_SAVED', 'GIT_HANDOFF_PENDING', '注册权限不代表保存授权', '不代表项目读写权限', '工具发现不等于权限'))

    def test_save_authorization_reuse_and_reset(self):
        self.contains(self.entry, ('自动归档入口', '不逐张重复询问'))
        self.contains(self.mcp, ('未获 SAVE_AUTHORIZED 时必须先询问', '禁止先注册或上传再补问', '同一项目、同一已确认任务范围', '不逐张询问', '切换项目、撤销授权', '必须重新确认', '不能跨项目自动继承'))

    def test_registration_cannot_bypass_binding_or_permissions(self):
        self.contains(self.mcp, ('artifact_project_resolve', 'artifact_project_register', '项目存在则复用', 'FORBIDDEN/UNAUTHORIZED 不能解释为项目不存在', '不得用注册绕过绑定或接管历史项目', '重新 resolve 核验', '无写权限时必须停止上传', '禁止提交自报 Grants', '不得编造已读取服务器策略'))

    def test_fallbacks_are_explicit_and_fail_closed(self):
        self.contains(self.mcp, ('MCP 未连接', '当前服务版本不支持自动注册', 'REGISTRATION_PERMISSION_REQUIRED', 'PROJECT_REGISTRATION_CONFLICT', 'LEGACY_BINDING_REQUIRED', 'PROJECT_AUTHORIZATION_REQUIRED', 'BLOCKED', '禁止近似重绘、截图替代或虚构成功回执'))

    def test_fixed_set_chain_and_no_git_requirement(self):
        self.contains(self.mcp, ('artifact_begin', 'artifact_receive', 'artifact_status', 'artifact_commit', 'artifact_list', 'artifact_download', 'artifact_recover', '复用原', 'upload_id', '每个页面必须保留独立文件', 'high_fidelity', 'prototype', '宿主不保证必然提供可用原图引用', '原字节 SHA-256'))
        self.assertNotIn('PROJECT_REGISTRATION_POLICIES_JSON=', self.mcp)
        self.assertNotIn('"$schema"', self.mcp)

    def test_archive_matrix_is_not_real_model_evidence(self):
        matrix = (SKILL/'tests/acceptance.md').read_text(encoding='utf-8')
        self.assertEqual(re.findall(r'^\| (A\d{2}) \|', matrix, re.M), [f'A{i:02d}' for i in range(1,11)])
        self.contains(matrix, ('STATIC_ONLY', '尚未通过真实 ChatGPT/Agent 会话验收', '原生 fileParams', 'GIT_HANDOFF_PENDING'))


if __name__ == '__main__': unittest.main()
