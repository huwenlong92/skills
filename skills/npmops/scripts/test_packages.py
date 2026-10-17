import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('packages.py')
spec = importlib.util.spec_from_file_location('packages', SCRIPT)
packages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packages)


class PackageDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.packages = self.root / 'packages'
        self.packages.mkdir()
        self.config = self.root / 'config.json'
        self.config.write_text(json.dumps({'packages_root': 'packages'}))

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--config', str(self.config), *args],
                              capture_output=True, text=True)

    def test_relative_root_and_read_only_lookup(self):
        before = self.config.read_bytes()
        result = self.cli('root')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['packages_root'], str(self.packages))
        self.assertEqual(self.config.read_bytes(), before)
        self.assertEqual(list(self.packages.iterdir()), [])

    def test_create_only_creates_requested_directory(self):
        result = self.cli('create', 'sample-tools')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data['created'])
        self.assertFalse(data['package_initialized'])
        self.assertEqual(list((self.packages / 'sample-tools').iterdir()), [])
        self.assertFalse((self.packages / '.git').exists())

    def test_existing_directory_or_file_is_preserved(self):
        for name in ('existing-dir', 'existing-file'):
            path = self.packages / name
            if name.endswith('dir'):
                path.mkdir()
                (path / 'note').write_text('keep')
            else:
                path.write_text('keep')
            self.assertNotEqual(self.cli('create', name).returncode, 0)
        self.assertEqual((self.packages / 'existing-dir/note').read_text(), 'keep')
        self.assertEqual((self.packages / 'existing-file').read_text(), 'keep')

    def test_traversal_and_scoped_paths_are_rejected(self):
        for name in ('../outside', '/tmp/outside', '@example/tools', '.', '..', 'two words', 'node_modules'):
            with self.subTest(name=name):
                self.assertNotEqual(self.cli('create', name).returncode, 0)
        self.assertFalse((self.root / 'outside').exists())

    def test_find_matches_directory_and_scoped_package_name(self):
        path = self.packages / 'ui-kit'
        path.mkdir()
        (path / 'package.json').write_text(json.dumps({'name': '@example/components'}))
        for query in ('UI-KIT', '@EXAMPLE/components'):
            result = self.cli('find', query)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['packages'][0]['package_name'], '@example/components')
            self.assertTrue(json.loads(result.stdout)['packages'][0]['package_initialized'])
        self.assertEqual(json.loads(self.cli('find', 'missing').stdout)['packages'], [])

    def test_list_includes_uninitialized_directories_without_recursive_scanning(self):
        (self.packages / 'draft').mkdir()
        nested = self.packages / 'monorepo/packages/child'
        nested.mkdir(parents=True)
        (nested / 'package.json').write_text('{"name":"nested-child"}')
        result = json.loads(self.cli('list').stdout)
        self.assertEqual([p['directory'] for p in result['packages']], ['draft', 'monorepo'])
        self.assertTrue(all(p['package_name'] is None for p in result['packages']))
        self.assertTrue(all(not p['package_initialized'] for p in result['packages']))

    def test_symlinks_are_neither_traversed_nor_overwritten(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.packages / 'linked').symlink_to(outside, target_is_directory=True)
        (self.packages / 'dangling').symlink_to(self.root / 'missing')
        self.assertNotEqual(self.cli('create', 'dangling').returncode, 0)
        self.assertEqual(json.loads(self.cli('list').stdout)['packages'], [])
        self.assertTrue((self.packages / 'dangling').is_symlink())

    def test_invalid_manifest_is_reported_even_when_filter_has_no_match(self):
        path = self.packages / 'broken'
        path.mkdir()
        (path / 'package.json').write_text('{bad-json')
        result = json.loads(self.cli('find', 'missing').stdout)
        self.assertEqual(result['packages'], [])
        self.assertEqual(len(result['issues']), 1)

    def test_missing_or_invalid_configuration_never_initializes_or_falls_back(self):
        for data in ({}, {'packages_root': ''}, {'packages_root': 1}, {'packages_root': 'missing'}, []):
            self.config.write_text(json.dumps(data))
            self.assertNotEqual(self.cli('root').returncode, 0)
        self.config.unlink()
        self.assertNotEqual(self.cli('root').returncode, 0)
        self.assertFalse(self.config.exists())

    def test_default_private_config_path(self):
        config = self.root / '.config/sdkit/skills/npmops/config.json'
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({'packages_root': str(self.packages)}))
        result = subprocess.run([sys.executable, str(SCRIPT), 'root'], env=dict(os.environ, HOME=str(self.root)),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['packages_root'], str(self.packages))


if __name__ == '__main__':
    unittest.main(verbosity=2)
