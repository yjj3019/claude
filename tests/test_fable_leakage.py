import tempfile
import unittest
from pathlib import Path

from scripts.check_fable_leakage import analyze, load_texts


class FableLeakageTest(unittest.TestCase):
    def records(self, candidate: str, reference: str):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "candidate.md").write_text(candidate, encoding="utf-8")
        (root / "reference.md").write_text(reference, encoding="utf-8")
        return temp, load_texts([root / "candidate.md"]), load_texts([root / "reference.md"])

    def test_distinct_text_passes_and_semantic_is_not_faked(self):
        temp, candidates, references = self.records("alpha beta gamma delta", "one two three four")
        self.addCleanup(temp.cleanup)
        result = analyze(candidates, references, ngram_size=3, ceiling=.8, canaries=[])
        self.assertTrue(result["valid"])
        self.assertEqual(result["semantic_similarity"]["status"], "not_run")

    def test_ngram_overlap_fails(self):
        temp, candidates, references = self.records("start shared phrase appears here end", "shared phrase appears here today")
        self.addCleanup(temp.cleanup)
        result = analyze(candidates, references, ngram_size=3, ceiling=1, canaries=[])
        self.assertFalse(result["valid"])
        self.assertGreater(result["pairs"][0]["normalized_ngram_overlap_count"], 0)

    def test_canary_fails_case_insensitively(self):
        temp, candidates, references = self.records("Contains HOLDOUT-CANARY-7", "unrelated reference")
        self.addCleanup(temp.cleanup)
        result = analyze(candidates, references, ngram_size=3, ceiling=1, canaries=["holdout-canary-7"])
        self.assertFalse(result["valid"])
        self.assertEqual(result["canary_hits"][0]["values"], ["holdout-canary-7"])


if __name__ == "__main__":
    unittest.main()
