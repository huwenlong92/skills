#!/usr/bin/env python3
"""Offline regression checks for orchestration and execution standards."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ORCH = ROOT / "standards" / "skill-orchestration.md"
EXEC = ROOT / "standards" / "development-execution.md"

class ProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orch = ORCH.read_text(encoding="utf-8")
        cls.execution = EXEC.read_text(encoding="utf-8")

    def test_protocols_exist(self):
        self.assertTrue(ORCH.is_file())
        self.assertTrue(EXEC.is_file())

    def test_selection_contract(self):
        for token in ["Primary", "Supporting", "Guardrail", "Discover", "Resolve", "Preflight", "Verify", "Handoff"]:
            with self.subTest(token=token):
                self.assertIn(token, self.orch)

    def test_negative_triggers(self):
        for token in ["不连接数据库", "不自动修改 sdkit core", "不覆盖 PRD", "不执行 DDL"]:
            with self.subTest(token=token):
                self.assertIn(token, self.orch)

    def test_capability_and_authorization_separated(self):
        for token in ["Ready", "Degraded", "Blocked", "授权", "正式数据库"]:
            with self.subTest(token=token):
                self.assertIn(token, self.orch)

    def test_checkpoints(self):
        for token in ["C0 Start", "C1 Stage", "C2 Integration", "C3 Finish"]:
            with self.subTest(token=token):
                self.assertIn(token, self.execution)

    def test_deviations(self):
        for token in ["D0", "D1", "D2", "D3", "revision"]:
            with self.subTest(token=token):
                self.assertIn(token, self.execution)

    def test_persistent_state_compatibility(self):
        for token in ["TASKS.md", "DECISIONS.md", "STATUS.md", "HANDOFF.md"]:
            with self.subTest(token=token):
                self.assertIn(token, self.execution)

    def test_local_relative_links(self):
        for doc in [ORCH, EXEC]:
            for dest in re.findall(r"\]\(([^)]+\.md)\)", doc.read_text(encoding="utf-8")):
                with self.subTest(doc=doc.name, link=dest):
                    self.assertTrue((doc.parent / dest).is_file())

    def test_agent_entrypoints(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("standards/skill-orchestration.md", agents)
        self.assertIn("standards/development-execution.md", agents)

    def test_collaboration_guardrail_is_reused(self):
        for token in ["collaboration-awareness.md", "不得为感知主动触发 CI"]:
            self.assertIn(token, self.orch)
        self.assertIn("collaboration-awareness.md", self.execution)

    def test_stage_gates_and_scope_change(self):
        for token in ["阶段结束", "原始 Git 基线", "暂停受影响修改", "明确批准", "测试证据"]:
            with self.subTest(token=token):
                self.assertIn(token, self.execution)

    def test_long_task_recovery(self):
        for token in ["未提交修改必须保留", "第一个未验收阶段", "不得仅凭交接文档认定完成"]:
            with self.subTest(token=token):
                self.assertIn(token, self.execution)

    def test_parallel_skill_migration_compatibility(self):
        catalog = (ROOT / "catalog.json").read_text(encoding="utf-8")
        self.assertIn('"skills"', catalog)
        self.assertIn("候选的 gitops、dbops", self.orch)
        self.assertIn("已验证的专用模板 Skill", self.orch)

    def test_plan_change_does_not_imply_approval(self):
        self.assertIn("不得伪称已批准", self.execution)
        self.assertIn("用户当前明确的新指令", self.execution)

    def test_no_unapproved_execution(self):
        self.assertIn("不自动安装", self.orch)
        self.assertIn("不得为感知主动触发 CI", self.orch)
        self.assertIn("不得宣称防漂移已验证", self.execution)

if __name__ == "__main__":
    unittest.main()
