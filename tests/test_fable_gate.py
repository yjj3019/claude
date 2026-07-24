import json
import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_fable_gate import evaluate


class FableGateTest(unittest.TestCase):
    def evidence(self, root: Path, *, quality=True, placebo=False):
        identity = {"dataset_id": "PRIVATE-HOLDOUT", "manifest_sha256": "a" * 64}
        documents = {
            "analysis": {"valid": True, "quality_gate_pass": quality, "placebo_gate_pass": placebo,
                         "out_of_domain_gate_pass": True, "batch_ids": ["A", "B"], **identity},
            "reliability": {"reliability_gate_pass": True, "batch_ids": ["A", "B"], **identity},
            "preflight": {"valid": True, "execution_ready": True, **identity},
            "audit-a": {"valid": True, "collection_complete": True, "scoring_ready": True, "batch_id": "A", **identity},
            "audit-b": {"valid": True, "collection_complete": True, "scoring_ready": True, "batch_id": "B", **identity},
        }
        paths = {}
        for name, document in documents.items():
            paths[name] = root / f"{name}.json"
            paths[name].write_text(json.dumps(document), encoding="utf-8")
        return paths

    def test_missing_placebo_is_conditional(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory))
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "CONDITIONAL_GO")
        self.assertFalse(result["benchmark_promotion_ready"])

    def test_failed_quality_is_no_go(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), quality=False)
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "NO_GO")

    def test_missing_out_of_domain_evidence_is_no_go(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), placebo=True)
            document = json.loads(paths["analysis"].read_text(encoding="utf-8"))
            document["out_of_domain_gate_pass"] = False
            paths["analysis"].write_text(json.dumps(document), encoding="utf-8")
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "NO_GO")
        self.assertIn("out_of_domain_gate_failed", result["blockers"])

    def test_all_gates_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), placebo=True)
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "GO")
        self.assertTrue(result["benchmark_promotion_ready"])

    def test_duplicate_batch_is_no_go(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), placebo=True)
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-a"]])
        self.assertEqual(result["verdict"], "NO_GO")
        self.assertFalse(result["valid"])

    def test_unrelated_reliability_batches_are_no_go(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), placebo=True)
            document = json.loads(paths["reliability"].read_text(encoding="utf-8"))
            document["batch_ids"] = ["X", "Y"]
            paths["reliability"].write_text(json.dumps(document), encoding="utf-8")
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "NO_GO")
        self.assertIn("reliability batch_ids do not match batch audits", result["errors"] if "errors" in result else result["blockers"])

    def test_unrelated_dataset_is_no_go(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = self.evidence(Path(directory), placebo=True)
            document = json.loads(paths["analysis"].read_text(encoding="utf-8"))
            document["dataset_id"] = "OTHER-HOLDOUT"
            paths["analysis"].write_text(json.dumps(document), encoding="utf-8")
            result = evaluate(paths["analysis"], paths["reliability"], paths["preflight"],
                              [paths["audit-a"], paths["audit-b"]])
        self.assertEqual(result["verdict"], "NO_GO")
        self.assertIn("analysis holdout identity does not match batch audits", result["blockers"])


if __name__ == "__main__":
    unittest.main()
