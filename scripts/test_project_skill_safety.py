"""Real temporary-file/CLI checks; never opens the user's configuration."""
import fcntl
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

import project_skill_io as io
import project_skill_global as g
import project_skill_bootstrap as p

SCRIPTS = Path(__file__).resolve().parent

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.target = self.root / 'AGENTS.md'
        self.target.write_bytes(b'# Custom\r\nKeep exact bytes.\r\n')
        self.target.chmod(0o640)

    def update(self, **kwargs):
        _, original = io.read(self.root)
        return io.apply(self.root, original, g.plan(original[1]), kwargs.pop('authorized', True), kwargs.pop('expected', io.digest(original[1])), **kwargs)

    def cli(self, script, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True, text=True, env=env)

    def test_backup_restore_and_permissions(self):
        before = self.target.read_bytes()
        out = self.update()
        backup = Path(out['backup'])
        self.assertEqual(backup.read_bytes(), before)
        self.assertEqual(stat.S_IMODE(backup.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(backup.parent.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o640)
        io.restore(self.root, backup, True, io.digest(self.target.read_bytes()))
        self.assertEqual(self.target.read_bytes(), before)
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o640)

    def test_unauthorized_and_stale_leave_bytes(self):
        before = self.target.read_bytes()
        for kwargs in ({'authorized': False}, {'expected': '0'*64}):
            with self.assertRaises(ValueError):
                self.update(**kwargs)
            self.assertEqual(self.target.read_bytes(), before)
        self.assertEqual(sorted(x.name for x in self.root.iterdir()), ['AGENTS.md'])

    def test_noop_still_requires_authorization(self):
        self.update()
        with self.assertRaises(ValueError):
            self.update(authorized=False)

    def test_idempotent_no_extra_backups(self):
        self.update()
        before = sorted(self.root.iterdir())
        self.assertEqual(self.update()['status'], 'unchanged')
        self.assertEqual(sorted(self.root.iterdir()), before)

    def test_external_content_change(self):
        def change():
            self.target.write_bytes(b'External editor')
        with self.assertRaisesRegex(ValueError, 'concurrent'):
            self.update(hook=change)
        self.assertEqual(self.target.read_bytes(), b'External editor')
        self.assertTrue((self.root / '.sdkit-agents-pending.json').is_file())

    def test_external_delete(self):
        with self.assertRaisesRegex(ValueError, 'concurrent'):
            self.update(hook=self.target.unlink)
        self.assertFalse(self.target.exists())

    def test_external_create_missing_target(self):
        self.target.unlink()
        with self.assertRaisesRegex(ValueError, 'concurrent'):
            self.update(hook=lambda: self.target.write_bytes(b'new user file'))
        self.assertEqual(self.target.read_bytes(), b'new user file')

    def test_external_mode_change(self):
        with self.assertRaisesRegex(ValueError, 'concurrent'):
            self.update(hook=lambda: self.target.chmod(0o600))
        self.assertEqual(self.target.read_bytes(), b'# Custom\r\nKeep exact bytes.\r\n')

    def test_external_inode_replacement_same_bytes(self):
        def replace():
            other = self.root / 'other'
            other.write_bytes(self.target.read_bytes())
            other.replace(self.target)
        with self.assertRaisesRegex(ValueError, 'concurrent'):
            self.update(hook=replace)

    def test_two_updaters_lock(self):
        with io.locked(self.root):
            out = self.cli('project_skill_global.py', '--codex-home', str(self.root), '--apply', '--authorized', '--expected-sha256', io.digest(self.target.read_bytes()))
            self.assertNotEqual(out.returncode, 0)
            self.assertIn('holds lock', out.stderr)

    def test_interruption_retains_journal_and_original(self):
        before = self.target.read_bytes()
        def interrupt():
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            self.update(hook=interrupt)
        journal = json.loads((self.root / '.sdkit-agents-pending.json').read_text())
        self.assertEqual(Path(journal['backup']).read_bytes(), before)
        self.assertEqual(self.target.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'pending'):
            self.update()

    def test_new_file_private(self):
        self.target.unlink()
        out = self.update()
        self.assertIsNone(out['backup'])
        self.assertFalse(out['existed'])
        self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)

    def test_target_symlink_rejected(self):
        other = self.root / 'other'
        self.target.rename(other)
        self.target.symlink_to(other)
        with self.assertRaises(OSError):
            io.read(self.root)
        self.assertEqual(other.read_bytes(), b'# Custom\r\nKeep exact bytes.\r\n')

    def test_ancestor_symlink_rejected(self):
        alias = self.root / 'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            io.read(alias)

    def test_directory_and_hardlink_rejected(self):
        self.target.unlink()
        self.target.mkdir()
        with self.assertRaises(ValueError):
            io.read(self.root)
        self.target.rmdir()
        self.target.write_bytes(b'x')
        os.link(self.target, self.root / 'hardlink')
        with self.assertRaises(ValueError):
            io.read(self.root)

    def test_custom_codex_home_dry_run_does_not_write(self):
        before = sorted(self.root.iterdir())
        out = self.cli('project_skill_global.py', env={**os.environ, 'CODEX_HOME': str(self.root)})
        self.assertEqual(out.returncode, 0, out.stderr)
        result = json.loads(out.stdout)
        self.assertEqual(result['status'], 'dry-run')
        self.assertIn('Keep exact bytes.', result['draft'])
        self.assertEqual(sorted(self.root.iterdir()), before)

    def test_project_cli_apply_and_noop_authorization(self):
        args = ['--project', str(self.root), '--skill', 'sdbase-go', '--template', 'sdbase-go', '--revision', '1234567']
        out = self.cli('project_skill_bootstrap.py', *args)
        self.assertEqual(out.returncode, 0, out.stderr)
        raw = self.target.read_bytes()
        applied = self.cli('project_skill_bootstrap.py', *args, '--apply', '--authorized', '--expected-sha256', io.digest(raw))
        self.assertEqual(applied.returncode, 0, applied.stderr)
        denied = self.cli('project_skill_bootstrap.py', *args, '--apply')
        self.assertNotEqual(denied.returncode, 0)
        self.assertTrue(self.target.read_bytes().startswith(raw))

    def test_all_old_new_project_mappings(self):
        for old, new in p.MAPPINGS.items():
            result = p.plan(b'Custom\n\n\n', new, 'fixture', '1234567', old)
            self.assertEqual(result, p.plan(result, new, 'fixture', '1234567', old))
            self.assertTrue(result.startswith(b'Custom\n\n\n'))
            self.assertIn(new.encode(), result)
            with self.assertRaises(ValueError):
                p.plan(old.encode(), new, 'fixture', '1234567', old)

    def test_managed_legacy_is_replaceable_unmanaged_tail_exact(self):
        raw = ('before\r\n\n' + p.START + '\nnuxtjs\n' + p.END + '\r\n\nTAIL').encode()
        result = p.plan(raw, 'sdbase-nuxtjs-portal', 'fixture', '1234567', 'nuxtjs')
        self.assertTrue(result.startswith(b'before\r\n\n'))
        self.assertTrue(result.endswith(b'\r\n\nTAIL'))

    def test_reversed_markers(self):
        with self.assertRaises(ValueError):
            g.plan((g.END + g.START).encode())
        with self.assertRaises(ValueError):
            g.plan(b'<!-- END: no-superpowers --><!-- BEGIN: no-superpowers -->')
        with self.assertRaises(ValueError):
            p.plan((p.END + p.START).encode(), 'sdbase-go', 'fixture', '1234567', None)

    def test_all_seven_user_blocks_and_unique_managed_block(self):
        raw = ''.join(f'<!-- BEGIN: {name} -->\nPrivate preference {i}\n<!-- END: {name} -->\n' for i, name in enumerate(g.KNOWN_BLOCKS)).encode()
        updated = g.plan(raw)
        self.assertTrue(updated.startswith(raw))
        self.assertEqual(updated.count(g.START.encode()), 1)
        self.assertEqual(updated.count(g.END.encode()), 1)
        self.assertEqual(g.plan(updated), updated)

    def test_symlink_substitution_during_transaction(self):
        other = self.root / 'other'
        other.write_bytes(b'Unknown data')
        def change():
            self.target.unlink()
            self.target.symlink_to(other)
        with self.assertRaises(OSError):
            self.update(hook=change)
        self.assertEqual(other.read_bytes(), b'Unknown data')
        self.assertTrue((self.root / '.sdkit-agents-pending.json').is_file())

    def test_restore_requires_current_hash_and_authorization(self):
        out = self.update()
        before = self.target.read_bytes()
        for authorized, expected in [(False, io.digest(before)), (True, 'f'*64)]:
            with self.assertRaises(ValueError):
                io.restore(self.root, out['backup'], authorized, expected)
            self.assertEqual(self.target.read_bytes(), before)

    def test_legacy_word_boundaries(self):
        for name in p.MAPPINGS:
            self.assertTrue(g.audit(name.encode()))
        for name in p.MAPPINGS.values():
            self.assertFalse(g.audit(name.encode()), name)

if __name__ == '__main__':
    unittest.main()
