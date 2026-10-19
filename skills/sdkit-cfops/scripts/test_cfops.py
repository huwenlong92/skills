"""脱敏临时仓库与假 CLI；不访问真实 Cloudflare、不修改业务项目。"""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('cfops', Path(__file__).with_name('cfops.py'))
cf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cf)


class Project(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.write('.gitignore', 'dist/\n.runtime-dist/\n.sdkit/cloudflare/.local/\n')
        self.write('wrangler.toml', 'name="example-portal"\npages_build_output_dir="dist"\n')
        self.write('fake_cli.py', '''import sys,json
from pathlib import Path
if '--version' in sys.argv:
 print('4.130.0')
else:
 with Path('calls.jsonl').open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')
 if Path('fail-upload').exists() and '--dry-run' not in sys.argv: sys.exit(7)
 if '--dry-run' in sys.argv:
  Path('.runtime-dist').mkdir(exist_ok=True)
  Path('.runtime-dist/worker.js').write_text('export default {}')
''')
        self.write('build.py', "from pathlib import Path\np=Path('dist');p.mkdir(exist_ok=True);(p/'index.html').write_text('Example portal')\n")
        self.t = {
            'kind': 'pages-static', 'project': 'example-portal', 'account_id': '0'*32,
            'config': 'wrangler.toml', 'environment': 'preview', 'production_branch': 'release', 'branch': 'review',
            'wrangler_version': '4.130.0', 'cli': [sys.executable, 'fake_cli.py'], 'build': [sys.executable, 'build.py'],
            'output': 'dist', 'required_files': ['index.html'],
            'probes': [{'path': '/', 'status': 200, 'content_type': 'text/html', 'contains': 'Example portal'}]}
        self.save()
        self.run_git('init', '-q')
        self.run_git('add', '.')
        self.run_git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')

    def write(self, name, content):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def run_git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, check=True)

    def save(self):
        self.write('.sdkit/cloudflare/release.json', json.dumps({'schema_version': 1, 'targets': {'review': self.t}}))

    def load(self):
        self.save()
        return cf.load(self.root, '.sdkit/cloudflare/release.json', 'review')

    def args(self, **kw):
        import argparse
        return argparse.Namespace(target='review', expected_sha=cf.source(self.root)['sha'], write=True, **kw)

    def test_check_readonly_no_cli(self):
        cmd = [sys.executable, str(Path(cf.__file__)), 'check', '--root', str(self.root), '--target', 'review']
        p = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)['cloud_check'], 'NOT_RUN')
        self.assertFalse((self.root/'calls.jsonl').exists())
        self.assertFalse((self.root/'dist').exists())

    def test_wrong_project_stops(self):
        self.t['project'] = 'another-project'
        with self.assertRaises(cf.CheckError): self.load()

    def test_duplicate_config_stops(self):
        self.write('deploy/cloudflare/wrangler.toml', 'name="template"')
        with self.assertRaises(cf.CheckError): self.load()

    def test_production_branch_not_assumed_main(self):
        self.t.update(branch='main', environment='preview')
        self.load()
        self.t['branch'] = 'release'
        with self.assertRaises(cf.CheckError): self.load()
        self.t['environment'] = 'production'
        self.load()

    def test_output_mismatch(self):
        self.t['output'] = 'other'
        with self.assertRaises(cf.CheckError): self.load()

    def test_escape_and_symlink(self):
        for path in ['../outside', '/tmp/outside']:
            with self.assertRaises(cf.CheckError): cf.local_path(self.root, path)
        (self.root/'link').symlink_to(self.root/'dist')
        with self.assertRaises(cf.CheckError): cf.local_path(self.root, 'link')

    def test_jsonc_strings_and_trailing_comma(self):
        self.assertEqual(cf.jsonc('{/*a*/"url":"https://a.invalid/a,}",//b\n"a":[1,],}'), {'url':'https://a.invalid/a,}', 'a':[1]})
        with self.assertRaises(cf.CheckError): cf.jsonc('{/*')

    def test_version_mismatch(self):
        self.t['wrangler_version'] = '4.0.0'
        with self.assertRaises(cf.CheckError): cf.build(self.root, self.t)
        self.assertFalse((self.root/'dist').exists())

    def test_implicit_env_blocks(self):
        with patch.dict(os.environ, {'WRANGLER_ENV':'production'}):
            with self.assertRaises(cf.CheckError): cf.cli_check(self.root, self.t)

    def test_static_build(self):
        digest = cf.build(self.root, self.t)
        self.assertEqual(len(digest), 64)
        self.assertEqual((self.root/'dist/index.html').read_text(), 'Example portal')

    def test_nuxt_missing_worker(self):
        self.t['kind'] = 'pages-nuxt'
        with self.assertRaises(cf.CheckError): cf.build(self.root, self.t)

    def test_artifact_symlink(self):
        cf.build(self.root, self.t)
        (self.root/'dist/leak').symlink_to(self.root/'fake_cli.py')
        with self.assertRaises(cf.CheckError): cf.artifacts(self.root, self.t)

    def test_worker_env_and_dryrun(self):
        self.write('worker.mjs', 'export default {}')
        self.write('wrangler.toml', 'name="example"\nmain="worker.mjs"\n[env.review]\nname="example-portal"\n')
        self.t.update(kind='worker', worker_env='review', output='.runtime-dist', required_files=['worker.js'])
        self.load()
        cf.build(self.root, self.t)
        call = json.loads((self.root/'calls.jsonl').read_text())
        self.assertIn('--dry-run', call)
        self.assertEqual(call[call.index('--env')+1], 'review')

    def test_worker_env_requires_explicit_name(self):
        self.write('wrangler.toml', 'name="example"\nmain="worker.mjs"\n[env.review]\nvars={}\n')
        self.t.update(kind='worker', worker_env='review')
        with self.assertRaises(cf.CheckError): self.load()

    def test_custom_build_hook_stops(self):
        self.write('wrangler.toml', 'name="example-portal"\npages_build_output_dir="dist"\n[build]\ncommand="unreviewed-hook"\n')
        with self.assertRaises(cf.CheckError): self.load()

    def test_root_output_stops(self):
        self.write('wrangler.toml', 'name="example-portal"\npages_build_output_dir="."\n')
        self.t['output'] = '.'
        with self.assertRaises(cf.CheckError): self.load()

    def test_pages_nonroot_config_stops(self):
        (self.root/'wrangler.toml').rename(self.root/'alternate.toml')
        self.t['config'] = 'alternate.toml'
        with self.assertRaises(cf.CheckError): self.load()

    def test_dynamic_and_redirected_config_stops(self):
        for name in ['wrangler.ts', '.wrangler/deploy/config.json']:
            with self.subTest(name=name):
                self.write(name, '{}')
                with self.assertRaises(cf.CheckError): self.load()
                (self.root/name).unlink()

    def test_explicit_deploy_hidden_in_build_stops(self):
        self.t['build'] = ['pnpm', 'exec', 'wrangler', 'pages', 'deploy', 'dist']
        with self.assertRaises(cf.CheckError): self.load()
        self.assertFalse((self.root/'calls.jsonl').exists())

    def test_package_lifecycle_side_effect_stops(self):
        self.write('package.json', json.dumps({'scripts':{'build':'vite build','postbuild':'wrangler pages deploy dist'}}))
        self.t['build'] = ['pnpm', 'run', 'build']
        with self.assertRaises(cf.CheckError): self.load()

    def test_script_infrastructure_side_effect_stops(self):
        self.write('build.sh', 'terraform apply\n')
        self.t['build'] = ['sh', 'build.sh']
        with self.assertRaises(cf.CheckError): self.load()

    def test_no_write_no_build(self):
        args = self.args(); args.write = False
        with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, args)
        self.assertFalse((self.root/'dist').exists())

    def test_wrong_sha_blocks(self):
        args = self.args(); args.expected_sha = 'f'*40
        with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, args)

    def test_wrong_account_blocks(self):
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'f'*32}):
            with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())

    def test_production_dirty_blocks(self):
        self.write('dirty.txt', 'changed')
        self.t['environment'] = 'production'
        with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())

    def test_source_detects_changes_with_same_dirty_boolean(self):
        self.write('dirty.txt', 'first')
        a = cf.source(self.root)
        self.write('dirty.txt', 'second')
        b = cf.source(self.root)
        self.assertTrue(a['dirty'] and b['dirty'])
        self.assertNotEqual(a['worktree_sha256'], b['worktree_sha256'])

    def test_git_operation_blocks(self):
        self.write('.git/MERGE_HEAD', 'f'*40)
        with self.assertRaises(cf.CheckError): cf.source(self.root)

    def test_rebase_blocks(self):
        (self.root/'.git/rebase-merge').mkdir()
        with self.assertRaises(cf.CheckError): cf.source(self.root)

    def test_build_failure_does_not_upload(self):
        self.write('build.py', 'raise SystemExit(9)\n')
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())
        self.assertFalse((self.root/'calls.jsonl').exists())
        self.assertFalse((self.root/'.sdkit/cloudflare/.local/last-deploy.json').exists())

    def test_build_generated_redirect_does_not_upload(self):
        self.write('build.py', "from pathlib import Path\np=Path('.wrangler/deploy');p.mkdir(parents=True);(p/'config.json').write_text('{}')\n")
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())
        self.assertFalse((self.root/'calls.jsonl').exists())

    def test_build_config_rewrite_does_not_upload(self):
        self.write('build.py', "from pathlib import Path\nPath('wrangler.toml').write_text('name=\"other\"')\n")
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())
        self.assertFalse((self.root/'calls.jsonl').exists())

    def test_preview_deploy_true_dirty_receipt(self):
        self.write('dirty.txt', 'authorized preview')
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            cf.deploy(self.root, self.t, self.args())
        call = json.loads((self.root/'calls.jsonl').read_text())
        self.assertIn('--commit-dirty=true', call)
        self.assertNotIn('--config', call)
        self.assertEqual(call[call.index('--branch')+1], 'review')
        receipt = json.loads((self.root/'.sdkit/cloudflare/.local/last-deploy.json').read_text())
        self.assertTrue(receipt['dirty'])
        self.assertEqual(receipt['status'], 'cli-success-provider-readback-required')

    def test_clean_production_records_false(self):
        self.t.update(environment='production', branch='release')
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            cf.deploy(self.root, self.t, self.args())
        call = json.loads((self.root/'calls.jsonl').read_text())
        self.assertIn('--commit-dirty=false', call)
        self.assertEqual(call[call.index('--branch')+1], 'release')

    def test_upload_failure_preserves_unknown_receipt(self):
        self.write('fail-upload', 'fixture')
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):
            with self.assertRaises(cf.CheckError): cf.deploy(self.root, self.t, self.args())
        record = json.loads((self.root/'.sdkit/cloudflare/.local/last-deploy.json').read_text())
        self.assertEqual(record['status'], 'failed-or-unknown')
        calls = (self.root/'calls.jsonl').read_text().splitlines()
        self.assertEqual(len(calls), 1)  # 响应未知时不重试、不回滚。
        self.assertNotIn('rollback', calls[0])

    def test_no_resource_or_ci_side_effects(self):
        protected = ['protected/r2/latest.json','protected/dns.json','protected/access.json','protected/database.sql','.github/workflows/ci.yml']
        for name in protected:self.write(name, 'unchanged fixture')
        with patch.dict(os.environ, {'CLOUDFLARE_ACCOUNT_ID':'0'*32}):cf.deploy(self.root, self.t, self.args())
        for name in protected:self.assertEqual((self.root/name).read_text(),'unchanged fixture')
        calls = [json.loads(line) for line in (self.root/'calls.jsonl').read_text().splitlines()]
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][:2],['pages','deploy'])


class Probes(unittest.TestCase):
    class Response:
        def __init__(self, status=200, mime='text/html', body=b'Example portal'):
            from email.message import Message
            self.status = status
            self.headers = Message(); self.headers['Content-Type'] = mime
            self.body = body
        def read(self, n): return self.body[:n]
        def __enter__(self): return self
        def __exit__(self, *args): pass

    def setUp(self):
        self.t = {'probes':[{'path':'/', 'status':200, 'content_type':'text/html', 'contains':'Example portal'}]}

    def run_probe(self, response):
        with patch.object(cf.urllib.request, 'build_opener') as mocked, contextlib.redirect_stdout(io.StringIO()):
            mocked.return_value.open.return_value = response
            cf.verify(self.t, 'https://example.invalid')

    def test_success(self): self.run_probe(self.Response())
    def test_wrong_mime(self):
        with self.assertRaises(cf.CheckError): self.run_probe(self.Response(mime='application/json'))
    def test_fallback_or_login_body(self):
        with self.assertRaises(cf.CheckError): self.run_probe(self.Response(body=b'Login'))
    def test_redirect_fails(self):
        with self.assertRaises(cf.CheckError): self.run_probe(self.Response(status=302))
        self.assertIsNone(cf.NoRedirect().redirect_request(None,None,302,'',{},'https://other.invalid'))
    def test_cross_origin_path_rejected_before_network(self):
        self.t['probes'][0]['path'] = '//other.invalid/'
        with patch.object(cf.urllib.request, 'build_opener') as m, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(cf.CheckError): cf.verify(self.t, 'https://example.invalid')
            m.return_value.open.assert_not_called()
    def test_origin_credentials_and_nonlocal_http(self):
        for origin in ['https://user:password@example.invalid', 'http://127.0.0.1', 'https://example.invalid/path']:
            with self.assertRaises(cf.CheckError): cf.verify(self.t, origin)


if __name__ == '__main__':
    unittest.main()
