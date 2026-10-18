#!/usr/bin/env python3
"""Offline regression checks for orchestration and execution standards."""
from pathlib import Path
import json
import re
import unittest
from urllib.parse import unquote, urlsplit

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
        docs = [ROOT / "AGENTS.md", *sorted((ROOT / "standards").glob("*.md")),
                *sorted((ROOT / ".sdkit").rglob("*.md"))]
        for doc in docs:
            # Code examples are not Markdown links. Check inline and reference links.
            prose = re.sub(r"^(`{3,}|~{3,}).*?^\1[^\n]*$", "",
                           doc.read_text(encoding="utf-8"), flags=re.M | re.S)
            links = re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)", prose)
            links += re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", prose, re.M)
            for dest in links:
                url = urlsplit(dest.strip("<>"))
                if url.scheme or url.netloc or not url.path:
                    continue
                with self.subTest(doc=doc.relative_to(ROOT), link=dest):
                    target = (doc.parent / unquote(url.path)).resolve()
                    self.assertTrue(target.is_relative_to(ROOT.resolve()), dest)
                    self.assertTrue(target.exists(), dest)

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
        names = {entry["name"] for entry in json.loads(catalog)["skills"]}
        for new, old in [
            ("sdkit-go-core", "sdkit"), ("sdkit-rust-core", "rust-sdcore"),
            ("sdbase-go", "sdkitgo"), ("sdbase-vab-admin", "vab-admin"),
            ("sdbase-nuxtjs-portal", "nuxtjs"),
        ]:
            with self.subTest(primary=new):
                self.assertIn(f"`{new}`", self.orch)
                self.assertIn(f"`{old}`", self.orch)
                if new in names:
                    self.assertTrue((ROOT / "skills" / new / "SKILL.md").is_file())
        self.assertIn("不得与新入口重复承担同一子任务", self.orch)
        self.assertIn("其 description 仍允许当前开发任务", self.orch)

    def test_verification_requires_actual_evidence(self):
        self.assertIn("只有本阶段全部验收条件通过时才允许标记 verified", self.execution)
        self.assertIn("退出码", self.execution)
        self.assertIn("未执行检查标记待验证", self.execution)
        self.assertIn("无等价证据时保留待验证", self.execution)

    def test_plan_is_persistent_and_immutable_baseline(self):
        self.assertIn("复杂任务必须在 `.sdkit/plans/<task-id>.md`", self.execution)
        self.assertIn("初始基线 SHA 只记录一次", self.execution)
        self.assertIn("revision 并保留历史", self.execution)

    def test_plan_change_does_not_imply_approval(self):
        self.assertIn("不得伪称已批准", self.execution)
        self.assertIn("用户当前明确的新指令", self.execution)

    def test_no_unapproved_execution(self):
        self.assertIn("不得自动安装未授权 Skill", self.orch)
        self.assertIn("不得为感知主动触发 CI", self.orch)
        self.assertIn("不得宣称防漂移已验证", self.execution)

if __name__ == "__main__":
    unittest.main()
