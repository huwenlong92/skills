"""Regression checks for the SDKit / SDBase primary and legacy packages."""
from pathlib import Path
import re
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

import manager


PAIRS = {
    "sdkit-go-core": "sdkit",
    "sdkit-rust-core": "rust-sdcore",
    "sdbase-go": "sdkitgo",
    "sdbase-vab-admin": "vab-admin",
    "sdbase-nuxtjs-portal": "nuxtjs",
}
TARGETS = (*PAIRS, "sdbase-lite", "sdbase-admin-lite", "sdbase-flutter-app")


def relative_links(path):
    prose = manager.markdown_prose(path.read_text(encoding="utf-8"))
    links = [a or b for a, b in manager.LINK.findall(prose)]
    links += re.findall(r'^ {0,3}\[[^]\n]+\]:\s*<?([^\s>]+)>?', prose, re.M)
    for link in links:
        url = urlsplit(link)
        if not url.scheme and not url.netloc and url.path:
            yield (path.parent / unquote(url.path)).resolve()


class MigrationTests(unittest.TestCase):
    def test_target_catalog_categories(self):
        entries = {s["name"]: s for s in manager.catalog()["skills"]}
        for name in TARGETS:
            with self.subTest(skill=name):
                expected = "framework" if name.startswith("sdkit-") else "template"
                self.assertEqual(entries[name]["category"], expected)
                self.assertTrue(manager.check_skill(manager.source(name), name))
                self.assertTrue((manager.source(name) / "references/repository.md").is_file())

    def test_primary_packages_are_self_contained(self):
        for name in TARGETS:
            root = manager.source(name).resolve()
            for md in root.rglob("*.md"):
                for target in relative_links(md):
                    with self.subTest(skill=name, file=md.relative_to(root), target=target):
                        self.assertTrue(target.is_relative_to(root), "standalone package links outside itself")
                        self.assertTrue(target.exists())

    def test_legacy_detailed_rules_preserved(self):
        # Repository identity is intentionally specific to each entry point.
        # The migrated detailed code rules must retain the compatibility copy.
        for new, old in PAIRS.items():
            legacy = manager.source(old) / "references"
            primary = manager.source(new) / "references"
            for old_file in legacy.rglob("*.md"):
                rel = old_file.relative_to(legacy)
                if rel == Path("repository.md"):
                    continue
                with self.subTest(primary=new, reference=rel):
                    self.assertEqual((primary / rel).read_bytes(), old_file.read_bytes())

    def test_each_target_installs_and_updates_independently(self):
        for name in TARGETS:
            with self.subTest(skill=name), tempfile.TemporaryDirectory() as directory:
                parent = Path(directory).resolve()
                manager.install(name, parent)
                self.assertEqual({p.name for p in parent.iterdir()}, {name})
                self.assertEqual(manager.manifest(parent / name), manager.manifest(manager.source(name)))
                manager.install(name, parent, update=True)
                self.assertEqual(manager.manifest(parent / name), manager.manifest(manager.source(name)))

    def test_legacy_and_primary_never_overwrite_each_other(self):
        # A temporary collision fixture, not a recommended installation scope.
        for new, old in PAIRS.items():
            with self.subTest(primary=new), tempfile.TemporaryDirectory() as directory:
                parent = Path(directory).resolve()
                manager.install(old, parent)
                legacy_before = manager.manifest(parent / old)
                manager.install(new, parent)
                primary_before = manager.manifest(parent / new)
                manager.install(new, parent, update=True)
                self.assertEqual(manager.manifest(parent / old), legacy_before)
                manager.install(old, parent, update=True)
                self.assertEqual(manager.manifest(parent / new), primary_before)
                for name in (old, new):
                    with self.assertRaises(ValueError):
                        manager.install(name, parent)
                self.assertEqual(manager.manifest(parent / old), legacy_before)
                self.assertEqual(manager.manifest(parent / new), primary_before)

    def test_readme_install_names_exist(self):
        readme = (manager.ROOT / "README.md").read_text(encoding="utf-8")
        names = {s["name"] for s in manager.catalog()["skills"]}
        commands = re.findall(r"^.*(?:pnpx|npx) skills add .*$", readme, re.M)
        self.assertTrue(commands)
        for command in commands:
            for name in re.findall(r"--skill ([a-z][a-z0-9-]*)", command):
                with self.subTest(command=command):
                    self.assertIn(name, names)
                    self.assertNotIn(name, PAIRS.values(), "normal install example uses legacy entry")

    def test_all_repository_markdown_relative_paths(self):
        for md in manager.ROOT.rglob("*.md"):
            if any(p.startswith(".") for p in md.relative_to(manager.ROOT).parts):
                continue
            for target in relative_links(md):
                with self.subTest(file=md.relative_to(manager.ROOT), target=target):
                    self.assertTrue(target.is_relative_to(manager.ROOT))
                    self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
