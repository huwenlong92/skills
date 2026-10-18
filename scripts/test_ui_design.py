"""ui-design 的离线契约回归；不能替代真实模型选择与行为验收。"""
import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UIDesignTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding='utf-8')

    def test_catalog_and_frontmatter_identity(self):
        entries = json.loads(self.read('catalog.json'))['skills']
        self.assertEqual(len([e for e in entries if e['name'] == 'ui-design']), 1)
        text = self.read('skills/ui-design/SKILL.md')
        fields = text.split('---', 2)[1].strip().splitlines()
        self.assertEqual([line.split(':', 1)[0] for line in fields], ['name', 'description'])
        self.assertEqual(fields[0], 'name: ui-design')

    def test_reference_quality_and_standalone_links(self):
        skill = ROOT / 'skills/ui-design'
        refs = sorted((skill / 'references').glob('*.md'))
        self.assertEqual({p.stem for p in refs}, {'handoff', 'interaction', 'responsive', 'review', 'visual'})
        for path in refs:
            text = path.read_text(encoding='utf-8')
            with self.subTest(reference=path.name):
                self.assertIn('适用范围：', text.splitlines()[2])
                self.assertIn('正向形态：', text)
                self.assertIn('反例：', text)
                self.assertIn('## 完成标准', text)
                self.assertNotRegex(text, r'/Users/|/home/|尽量|适当|视情况|应具有|应保持')
        for path in skill.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                if '://' not in link:
                    target = (path.parent / link.split('#')[0]).resolve()
                    self.assertTrue(target.is_relative_to(skill.resolve()))
                    self.assertTrue(target.exists())

    def test_handoff_records_ten_dimensions_and_unknowns(self):
        text = self.read('skills/ui-design/references/handoff.md')
        for item in ['项目/模块', '独立交互原型', '正式前端', '来源与版本', '页面 ID', '交互状态',
                     '桌面与移动端', '素材来源', '已确认需求', '待确认事项', '技术实现边界', '可执行验收条件', '标记缺失']:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_handoff_distinguishes_three_asset_origins(self):
        text = self.read('skills/ui-design/references/handoff.md')
        for item in ['已有设计稿', '仅有文字描述', '图片工具实际生成', '工具成功结果', '产物可访问性', '停止图片交付声明']:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_handoff_has_no_undeclared_engineering_dependency(self):
        text = self.read('skills/ui-design/references/handoff.md')
        self.assertIn('仅当目标项目提供 Development Execution 协议时', text)
        self.assertIn('否则遵循项目实际工程计划规则', text)
        self.assertIn('禁止猜测源码路径', text)
        self.assertIn('当前回答交付说明', text)

    def test_unique_primary_and_implementation_boundaries(self):
        ui = self.read('skills/ui-design/SKILL.md')
        foundry = self.read('skills/foundry/SKILL.md')
        orch = self.read('standards/skill-orchestration.md')
        self.assertIn('仅开发代码、修复前端 Bug、发布原型或维护 PRD 时不得作为 Primary', ui)
        self.assertIn('由 `ui-design` 作为 Primary', foundry)
        self.assertIn('正式代码实现仍以实际技术栈 Skill 为 Primary', orch)
        for item in ['PRD', '原型', '发布', '项目初始化与导入']:
            self.assertIn(item, foundry)
        self.assertIn('不负责正式业务代码开发', foundry)

    def test_acceptance_matrix_retains_all_scenarios(self):
        text = self.read('skills/ui-design/tests/acceptance.md')
        ids = re.findall(r'^\| (U\d{2}) \|', text, re.M)
        self.assertEqual(ids, [f'U{i:02d}' for i in range(1, 13)])
        self.assertIn('不能将本文件存在视为模型隐式触发通过', text)

    def test_isolated_install_and_update(self):
        spec = importlib.util.spec_from_file_location('ui_acceptance_manager', ROOT / 'skills/sdkit-skills/scripts/manager.py')
        manager = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manager)
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory).resolve()
            manager.install('ui-design', parent)
            self.assertEqual(manager.manifest(parent / 'ui-design'), manager.manifest(manager.source('ui-design')))
            manager.install('ui-design', parent, update=True)
            self.assertEqual(manager.manifest(parent / 'ui-design'), manager.manifest(manager.source('ui-design')))
            self.assertEqual({p.name for p in parent.iterdir()}, {'ui-design'})


if __name__ == '__main__':
    unittest.main()
