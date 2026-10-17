import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('binding.py')
spec = importlib.util.spec_from_file_location('binding', SCRIPT)
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / 'repo'
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.git('remote', 'add', 'origin', 'git@github.com:example/library.git')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.com',
                 'commit', '--allow-empty', '-qm', 'initial')
        self.url = 'https://github.com/example/library.git'
        self.config = self.root / 'config.json'
        self.config.write_text(json.dumps({'repository': {'url': self.url, 'local_path': 'repo'}}))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], text=True, capture_output=True, check=True)

    def test_relative_binding_and_read_only_cli(self):
        before = self.config.read_bytes()
        status = self.git('status', '--porcelain').stdout
        result = subprocess.run([sys.executable, str(SCRIPT), '--config', str(self.config)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data['fetch_push_verified'])
        self.assertFalse(data['fresh_remote_check'])
        self.assertEqual(data['local_path'], str(self.repo))
        self.assertEqual(before, self.config.read_bytes())
        self.assertEqual(status, self.git('status', '--porcelain').stdout)

    def test_default_config_path_is_skill_specific(self):
        config = self.root / '.config/sdkit/skills' / binding.SKILL_NAME / 'config.json'
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({'repository': {'url': self.url, 'local_path': str(self.repo)}}))
        env = dict(os.environ, HOME=str(self.root))
        env.pop('DOCKEROPS_CONFIG', None)
        result = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['identity_verified'])
        config.unlink()
        result = subprocess.run([sys.executable, str(SCRIPT)], env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(config.exists())

    def test_push_mismatch_fails(self):
        self.git('remote', 'set-url', '--push', 'origin', 'https://github.com/example/other.git')
        with self.assertRaises(ValueError): binding.verify(self.repo, self.url)

    def test_all_remote_urls_are_checked(self):
        for push in (False, True):
            with self.subTest(push=push):
                args = ['config', '--add', 'remote.origin.pushurl' if push else 'remote.origin.url',
                        'https://github.com/example/other.git']
                self.git(*args)
                with self.assertRaises(ValueError): binding.verify(self.repo, self.url)
                self.git('config', '--unset-all', 'remote.origin.pushurl' if push else 'remote.origin.url',
                         'https://github.com/example/other.git')

    def test_non_origin_is_not_used(self):
        self.git('remote', 'rename', 'origin', 'upstream')
        with self.assertRaises(ValueError): binding.verify(self.repo, self.url)

    def test_dirty_and_detached_are_reported_without_mutation(self):
        (self.repo / 'note.txt').write_text('existing work')
        self.git('checkout', '--detach', '-q')
        result = binding.verify(self.repo, self.url)
        self.assertTrue(result['dirty'])
        self.assertIsNone(result['branch'])
        self.assertIsNone(result['upstream'])
        self.assertEqual((self.repo / 'note.txt').read_text(), 'existing work')

    def test_missing_directory_or_config_never_falls_back(self):
        with self.assertRaises(ValueError): binding.verify(self.root / 'missing', self.url)
        with self.assertRaises(OSError): binding.load(self.root / 'missing.json')

    def test_invalid_config_is_rejected(self):
        for data in ([], {}, {'repository': None}, {'repository': {'url': self.url, 'local_path': ''}}):
            with self.subTest(data=data):
                self.config.write_text(json.dumps(data))
                with self.assertRaises(ValueError): binding.load(self.config)

    def test_url_identity_preserves_port_and_generic_path_case(self):
        self.assertEqual(binding.canonical(self.url), binding.canonical('git@github.com:Example/Library.git'))
        self.assertNotEqual(binding.canonical('ssh://git@code.example.invalid:2222/team/lib.git'),
                            binding.canonical('git@code.example.invalid:team/lib.git'))
        self.assertNotEqual(binding.canonical('https://code.example.invalid/team/Lib.git'),
                            binding.canonical('https://code.example.invalid/team/lib.git'))
        for url in ('https://token@github.com/example/lib.git', 'https://github.com/example/lib.git?token=x',
                    'ssh://git:secret@code.example.invalid/team/lib.git'):
            with self.subTest(url=url), self.assertRaises(ValueError): binding.canonical(url)


if __name__ == '__main__':
    unittest.main(verbosity=2)
