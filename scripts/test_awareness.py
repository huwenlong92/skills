import unittest
from awareness import (classify, dependencies, related_pr, complete_page_count,
                       changed_paths, protocols, affects)


class AwarenessTests(unittest.TestCase):
    def test_independent(self):
        self.assertEqual(classify(["skills/a/x"], ["skills/b/y"]), "L0")

    def test_related(self):
        self.assertEqual(classify(["a"], ["b"], related=True), "L1")

    def test_overlap(self):
        self.assertEqual(classify(["a"], ["a"]), "L2")

    def test_rename_target(self):
        self.assertEqual(classify(["new.md"], [{"filename": "new.md", "status": "renamed", "previous_filename": "old.md"}]), "L2")

    def test_rename_source(self):
        self.assertEqual(classify(["old.md"], [{"filename": "new.md", "status": "renamed", "previous_filename": "old.md"}]), "L2")

    def test_malformed_rename(self):
        self.assertEqual(classify(["old.md"], [{"filename": "new.md", "status": "renamed"}]), "L3")

    def test_incomplete(self):
        self.assertEqual(classify(["a"], ["b"], complete=False), "L3")

    def test_unverified(self):
        self.assertEqual(classify([], [], remote_verified=False), "L3")

    def test_head_advanced(self):
        self.assertEqual(classify(["a"], ["b"], head_unchanged=False), "L3")

    def test_dependencies(self):
        self.assertEqual(dependencies("Collaboration-Depends-On: #7, #8"), {7, 8})

    def test_bad_dependency(self):
        self.assertEqual(dependencies("Collaboration-Depends-On: #0, nonsense, #9"), {9})

    def test_related_dependency(self):
        self.assertTrue(related_pr(7, "Collaboration-Depends-On: #8", 8, ""))

    def test_related_protocol(self):
        self.assertTrue(related_pr(7, "Collaboration-Protocol: workspace-v1", 8, "Collaboration-Protocol: workspace-v1"))

    def test_related_affects(self):
        self.assertTrue(related_pr(7, "Collaboration-Affects: wikiops", 8, "Collaboration-Affects: wikiops"))

    def test_unrelated_protocol(self):
        self.assertFalse(related_pr(7, "Collaboration-Protocol: a", 8, "Collaboration-Protocol: b"))

    def test_metadata(self):
        self.assertEqual(protocols("Collaboration-Protocol: Workspace-V1"), {"workspace-v1"})
        self.assertEqual(affects("Collaboration-Affects: Foundry, WikiOps"), {"foundry", "wikiops"})

    def test_page_complete(self):
        self.assertTrue(complete_page_count([[1, 2]], expected_count=2))

    def test_page_truncated(self):
        self.assertFalse(complete_page_count([[1, 2]], page_size=2))

    def test_page_multiple(self):
        self.assertTrue(complete_page_count([[1, 2], [3]], expected_count=3, page_size=2))

    def test_page_missing_count(self):
        self.assertFalse(complete_page_count([[1]], expected_count=2))

    def test_empty_page(self):
        self.assertTrue(complete_page_count([[]], expected_count=0))

    def test_no_pages(self):
        self.assertFalse(complete_page_count([]))


if __name__ == "__main__":
    unittest.main()
