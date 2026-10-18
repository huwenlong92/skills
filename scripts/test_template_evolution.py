"""Template Evolution V1 protocol-only, offline acceptance. No repository writes."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "sdkit-templateops"
REF = SKILL / "references"
FILES = {p.stem: p.read_text(encoding="utf-8") for p in REF.glob("*.md")}
IDENTITY = FILES["identity"]
TOOL = FILES["toolchain"]
DEP = FILES["dependencies"]
DIFF = FILES["diff"]
UP = FILES["upgrade"]
REC = FILES["recovery"]
COL = FILES["collaboration"]
TEST = FILES["testing"]

def checks(*pairs):
    for content, needle in pairs:
        assert needle in content, "missing protocol: " + needle

class TemplateEvolutionAcceptance(unittest.TestCase):
    def test_01_known_origin(self): checks((IDENTITY, "verified"), (IDENTITY, "Commit"))
    def test_02_unknown_origin(self): checks((IDENTITY, "unknown"), (IDENTITY, "不得 Apply"))
    def test_03_node(self): checks((TOOL, ".node-version"), (TOOL, "TE-2001"))
    def test_04_go(self): checks((TOOL, "go.mod"), (TOOL, "toolchain"))
    def test_05_rust(self): checks((TOOL, "rust-toolchain.toml"), (TOOL, "Cargo.lock"))
    def test_06_python(self): checks((TOOL, "uv.lock"), (DEP, "pyproject.toml"))
    def test_07_added(self): checks((DIFF, "added"), (DIFF, "ownership"))
    def test_08_deleted(self): checks((DIFF, "deleted"), (DIFF, "自动删除"))
    def test_09_both_modified(self): checks((DIFF, "both_modified"), (DIFF, "review"))
    def test_10_dependency_conflict(self): checks((DEP, "TE-2003"), (DEP, "间接"))
    def test_11_legacy_upgrade(self): checks((IDENTITY, "adopted_baseline"), (UP, "revision"))
    def test_12_worktree(self): checks((COL, "Worktree"), (COL, "L0/L1/L2/L3"))
    def test_13_interrupt(self): checks((REC, "interrupted"), (REC, "required"))
    def test_14_restore(self): checks((REC, "partially_restored"), (REC, "原始基线"))
    def test_15_business_protection(self): checks((DIFF, "business"), (DIFF, "blocked"))
    def test_16_git_tracking(self): checks((IDENTITY, "last_synced"), (COL, "Commit"))
    def test_17_ci_mismatch(self): checks((TOOL, "ci_declared"), (TEST, "CI 漂移"))
    def test_18_unauthorized_agent(self): checks((UP, "当前用户明确授权"), (UP, "TE-4004"))
    def test_19_git_provider(self): checks((COL, "TE-4005"), (COL, "Provider"))
    def test_20_cross_stack(self): checks((UP, "required_mounts"), (TEST, "跨 Skill"))
    def test_catalog_and_frontmatter(self):
        c=json.loads((ROOT/"catalog.json").read_text())
        self.assertEqual(sum(x["name"]=="sdkit-templateops" for x in c["skills"]),1)
        entry=(SKILL/"SKILL.md").read_text()
        self.assertRegex(entry,r"(?s)^---\nname: sdkit-templateops\ndescription: [^\n]+\n---")
        self.assertEqual(len(FILES),8)
    def test_links_and_orchestration(self):
        entry=(SKILL/"SKILL.md").read_text()
        for path in re.findall(r"\]\((references/[^)]+)\)",entry):
            self.assertTrue((SKILL/path).is_file(),path)
        route=(ROOT/"standards"/"skill-orchestration.md").read_text()
        self.assertIn("sdkit-templateops",route)
        self.assertIn("普通业务功能",route)
    def test_no_untrusted_authorization(self):
        checks((UP, "批准记录只是证据引用"), (COL, "不能授权"))
    def test_no_auto_apply(self):
        checks((UP, "V1 不执行自动 Apply"), (REC, "禁止 reset --hard"))

if __name__=="__main__":
    unittest.main()
