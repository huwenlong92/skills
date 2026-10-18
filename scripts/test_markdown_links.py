"""Markdown 文件与锚点检查器的正反向夹具测试。"""
from pathlib import Path
import tempfile
import unittest

from check_markdown_links import check


class MarkdownLinksTests(unittest.TestCase):
    def run_fixture(self, source, target=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.md').write_text(source)
            if target is not None:
                (root / 'target file.md').write_text(target)
            return check(root)

    def test_encoded_path_and_chinese_heading(self):
        result = self.run_fixture('[目录](target%20file.md#默认本地保存与-git-边界)', '## 默认本地保存与 Git 边界\n')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['anchors'], 1)

    def test_missing_file(self):
        self.assertEqual(len(self.run_fixture('[x](absent.md)')['errors']), 1)

    def test_existing_file_missing_anchor(self):
        result = self.run_fixture('[x](target%20file.md#not-present)', '# Present\n')
        self.assertEqual(len(result['errors']), 1)
        self.assertIn('missing anchor', result['errors'][0])

    def test_duplicate_and_same_page_headings(self):
        result = self.run_fixture('# Same\n# Same\n[x](#same-1)\n')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['anchors'], 1)

    def test_examples_are_not_links_or_headings(self):
        result = self.run_fixture('````text\n[x](absent.md)\n# Fake\n````\n`[x](absent.md)`\n')
        self.assertEqual(result['relative_links'], 0)
        self.assertEqual(result['errors'], [])

    def test_reference_link_and_explicit_anchor(self):
        result = self.run_fixture('[x][anchor]\n[anchor]: <target%20file.md#explicit>\n', '<a id="explicit"></a>\n')
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['anchors'], 1)

    def test_repository_escape_rejected(self):
        self.assertEqual(len(self.run_fixture('[x](../outside.md)')['errors']), 1)


if __name__ == '__main__':
    unittest.main()
