import tempfile
from pathlib import Path
import unittest
from check_layout import check_layout


class LayoutChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.docker = self.root / '.sdkit/docker'
        self.docker.mkdir(parents=True)
        (self.root / 'Makefile').write_text('help:\n\t@true\n')
        (self.docker / 'README.md').write_text('说明')
        (self.docker / 'Dockerfile').write_text('FROM scratch\n')

    def test_single_operations_and_runtime_files(self):
        for p in ('build.sh', 'publish.sh', 'docker-compose.yml', 'nginx.conf.example'):
            (self.docker / p).touch()
        self.assertFalse(check_layout(self.root, 'single', operations=('build', 'publish'), required=('compose', 'nginx')))

    def test_multi_root_rejects_old_generic_scripts(self):
        (self.docker / 'push.sh').touch()
        self.assertTrue(check_layout(self.root, 'multi', ('test', 'release')))

    def test_multi_rejects_business_operation_at_root(self):
        (self.docker / 'build.sh').touch()
        self.assertTrue(check_layout(self.root, 'multi', ('test', 'release')))

    def test_multi_requires_each_environment_operation(self):
        (self.docker / 'test').mkdir()
        (self.docker / 'test/build.sh').touch()
        self.assertTrue(check_layout(self.root, 'multi', ('test', 'release'), ('build',)))

    def test_custom_environment_names(self):
        for env in ('staging', 'production'):
            (self.docker / env).mkdir()
            (self.docker / env / 'build.sh').touch()
        self.assertFalse(check_layout(self.root, 'multi', ('staging', 'production'), ('build',)))

    def test_single_does_not_accept_environment_names(self):
        self.assertTrue(check_layout(self.root, 'single', ('test',)))

    def test_multi_requires_explicit_environments(self):
        self.assertTrue(check_layout(self.root, 'multi'))

    def test_legacy_compose_alias_is_not_canonical(self):
        (self.docker / 'compose.yaml').touch()
        self.assertTrue(check_layout(self.root, 'single'))

    def test_artifact_does_not_require_fake_runtime_files(self):
        self.assertFalse(check_layout(self.root, 'artifact'))

    def test_helpers_allowed_and_broken_helper_reference_detected(self):
        (self.docker / 'scripts').mkdir()
        helper = self.docker / 'scripts/common.sh'
        helper.write_text('sh .sdkit/docker/missing.sh\n')
        self.assertTrue(check_layout(self.root, 'single'))
        helper.write_text('true\n')
        self.assertFalse(check_layout(self.root, 'single'))

    def test_duplicate_make_dockerfile_path_detected(self):
        (self.root / 'Makefile').write_text('package:\n\tdocker build -f .sdkit/docker/.sdkit/docker/Dockerfile .\n')
        self.assertTrue(check_layout(self.root, 'single'))

    def test_make_literal_correct_path_passes(self):
        (self.root / 'Makefile').write_text('build:\n\tdocker build -f .sdkit/docker/Dockerfile .\n')
        self.assertFalse(check_layout(self.root, 'single'))

    def test_broken_compose_link_detected(self):
        (self.docker / 'docker-compose.yml').symlink_to('missing.yml')
        self.assertTrue(check_layout(self.root, 'single'))

    def test_root_makefile_required(self):
        (self.root / 'Makefile').unlink()
        self.assertTrue(check_layout(self.root, 'single'))

    def test_shared_scripts_name_cannot_be_environment(self):
        self.assertTrue(check_layout(self.root, 'multi', ('scripts', 'release')))


if __name__ == '__main__':
    unittest.main()
