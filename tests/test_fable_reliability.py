import json
import tempfile
import unittest
from pathlib import Path

from scripts.calculate_fable_reliability import calculate, weighted_kappa


class FableReliabilityTest(unittest.TestCase):
    def ballots(self, root: Path, left, right):
        paths = []
        for rater, scores in (("RATER-1", left), ("RATER-2", right)):
            path = root / f"{rater}.json"
            path.write_text(json.dumps({"rater_id": rater, "batch_ids": ["A", "B"], "ratings": [
                {"blind_id": f"B{index:04}", "dimension": "quality", "score": score}
                for index, score in enumerate(scores)
            ]}), encoding="utf-8")
            paths.append(path)
        return paths

    def test_perfect_agreement_passes_and_binds_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            result = calculate(self.ballots(Path(directory), [0, 1, 2], [0, 1, 2]))
        self.assertEqual(result["reliability"], 1.0)
        self.assertTrue(result["reliability_gate_pass"])
        self.assertTrue(result["all_raters_observed_full_scale"])
        self.assertEqual(result["observed_scores_by_rater"], [[0, 1, 2], [0, 1, 2]])
        self.assertEqual(result["batch_ids"], ["A", "B"])
        self.assertEqual(len(result["ballot_sha256"]), 2)
        self.assertFalse(result["benchmark_promotion_ready"])

    def test_disagreement_fails(self):
        self.assertLess(weighted_kappa([0, 0, 2, 2], [2, 2, 0, 0]), .70)

    def test_reports_collapsed_observed_scale(self):
        with tempfile.TemporaryDirectory() as directory:
            result = calculate(self.ballots(Path(directory), [0, 1], [0, 1]))
        self.assertFalse(result["all_raters_observed_full_scale"])
        self.assertEqual(result["observed_scores_by_rater"], [[0, 1], [0, 1]])

    def test_requires_matching_items(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = self.ballots(root, [0, 1], [0, 1])
            document = json.loads(paths[1].read_text(encoding="utf-8"))
            document["ratings"][1]["blind_id"] = "OTHER"
            paths[1].write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identical"):
                calculate(paths)


if __name__ == "__main__":
    unittest.main()
