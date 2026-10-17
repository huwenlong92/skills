import unittest
from awareness import classify, dependencies


class AwarenessTests(unittest.TestCase):
    def test_independent(self):
        self.assertEqual(classify(["skills/a/x"], ["skills/b/y"]), "L0")

    def test_related(self):
        self.assertEqual(classify(["a"], ["b"], related=True), "L1")

    def test_overlap(self):
        self.assertEqual(classify(["a"], ["a"]), "L2")

    def test_incomplete(self):
        self.assertEqual(classify(["a"], ["b"], complete=False), "L3")

    def test_unverified(self):
        self.assertEqual(classify([], [], remote_verified=False), "L3")

    def test_dependencies(self):
        self.assertEqual(dependencies("Collaboration-Depends-On: #7, #8"), {7, 8})


if __name__ == "__main__":
    unittest.main()
