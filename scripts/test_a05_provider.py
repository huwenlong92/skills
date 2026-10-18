"""A05 真实 gh 代理的离线授权门禁，不替代 Agent 或 GitHub 验收。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'docs/testing/git-collaboration-v1/a05_provider.py'
SPEC = importlib.util.spec_from_file_location('a05_provider', SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProviderGate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.provider = MODULE.RestrictedGH('example/fixture', 'acceptance/a05', 'main', Path(self.temp.name))
        self.create = ['pr', 'create', '--repo', 'example/fixture', '--head', 'acceptance/a05',
                       '--base', 'main', '--draft', '--title', 'Fictional change', '--body', 'Fictional only.']

    def deny(self, args):
        with self.assertRaises(ValueError):
            self.provider.validate(args)

    def test_authorized_draft_shape(self):
        self.assertEqual(self.provider.validate(self.create), self.create)

    def test_non_draft_is_denied(self):
        self.deny([a for a in self.create if a != '--draft'])

    def test_other_repository_is_denied(self):
        self.deny([a.replace('example/fixture', 'example/other') for a in self.create])

    def test_other_head_is_denied(self):
        self.deny([a.replace('acceptance/a05', 'other') for a in self.create])

    def test_other_base_is_denied(self):
        self.deny([a.replace('main', 'release') for a in self.create])

    def test_duplicate_repository_is_denied(self):
        self.deny(self.create + ['-R', 'example/other'])
        self.deny(self.create + ['--repo', 'example/fixture'])

    def test_merge_and_ready_are_denied(self):
        for action in ['merge', 'ready', 'close', 'edit', 'review', 'reopen']:
            with self.subTest(action=action):
                self.deny(['pr', action, '1', '--repo', 'example/fixture'])

    def test_api_write_is_denied(self):
        for flag in ['--method', '-X', '-f', '-F', '--input']:
            with self.subTest(flag=flag):
                self.deny(['api', 'repos/example/fixture', flag, 'POST'])

    def test_api_secret_or_other_repo_is_denied(self):
        for path in ['repos/example/fixture/actions/secrets', 'repos/example/other', 'user/keys']:
            with self.subTest(path=path):
                self.deny(['api', path])

    def test_credential_export_is_denied(self):
        for args in [['auth', 'token'], ['auth', 'login'], ['auth', 'git-credential']]:
            with self.subTest(args=args):
                self.deny(args)

    def test_other_commands_are_denied(self):
        for args in [['repo', 'delete', 'example/fixture'], ['workflow', 'run'], ['run', 'rerun'],
                     ['repo', 'create', 'other'], ['ssh-key', 'list'], ['alias', 'set', 'x', '!env']]:
            with self.subTest(args=args):
                self.deny(args)

    def test_host_body_file_is_not_read_by_broker(self):
        args = self.create[:-2] + ['--body-file', '/not-authorized/secret']
        self.deny(args)

    def test_read_only_ref_is_allowed(self):
        args = ['api', 'repos/example/fixture/git/ref/heads/acceptance/a05']
        self.assertEqual(self.provider.validate(args), args)

    def test_pr_view_is_bound_to_repo(self):
        self.provider.validate(['pr', 'view', '1', '--repo', 'example/fixture'])
        self.deny(['pr', 'view', 'https://github.com/example/other/pull/1', '--repo', 'example/fixture'])

    def test_second_create_is_denied(self):
        self.provider.create_attempted = True
        self.deny(self.create)

    def test_missing_explicit_content_is_denied(self):
        self.deny(self.create[:-2])

    def test_denied_request_never_invokes_real_gh(self):
        with patch.object(MODULE.subprocess, 'run', side_effect=AssertionError('must not execute')):
            result = self.provider.execute(['pr', 'merge', '1', '--repo', 'example/fixture'])
        self.assertEqual(result['exit_code'], 126)
        self.assertFalse(self.provider.calls[-1]['authorized'])

    def test_invalid_argument_types_are_denied(self):
        for args in [None, 'pr create', [1], ['x' * 20001]]:
            with self.subTest(args=type(args).__name__):
                self.deny(args)

    def test_embedded_client_is_valid_python(self):
        compile(MODULE.CLIENT, '<sandbox-gh-client>', 'exec')


if __name__ == '__main__':
    unittest.main()
