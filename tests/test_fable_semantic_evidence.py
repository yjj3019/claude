import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.validate_fable_semantic_evidence as target


class FableSemanticEvidenceTest(unittest.TestCase):
    def make_evidence(self, *, similarity=.4, threshold=.85, include_pair=True, offline=True, tamper=False):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        local = root / ".local" / "fable"
        leakage = local / "leakage"
        holdout = local / "holdout"
        docs = root / "docs"
        leakage.mkdir(parents=True)
        holdout.mkdir(parents=True)
        docs.mkdir()
        candidate_raw, reference_raw = b"private candidate", b"distillation reference"
        candidate, reference = holdout / "candidate.md", docs / "reference.md"
        candidate.write_bytes(candidate_raw + (b" tampered" if tamper else b""))
        reference.write_bytes(reference_raw)
        candidate_hash, reference_hash = hashlib.sha256(candidate_raw).hexdigest(), hashlib.sha256(reference_raw).hexdigest()
        data = {
            "evidence_version": "1.0", "generated_at": "2026-07-22T00:00:00Z",
            "tool": {"name": "offline-tool", "version": "1", "model": "local-model@rev1", "offline": offline},
            "threshold": threshold,
            "candidates": [{"path": ".local/fable/holdout/candidate.md", "sha256": candidate_hash}],
            "references": [{"path": "docs/reference.md", "sha256": reference_hash}],
            "pairs": ([{"candidate_sha256": candidate_hash, "reference_sha256": reference_hash, "similarity": similarity}]
                      if include_pair else []),
        }
        evidence = leakage / "semantic.json"
        evidence.write_text(json.dumps(data), encoding="utf-8")
        return temp, root, local, leakage, evidence

    def run_validation(self, root, local, leakage, evidence):
        benchmark = root / "benchmark.json"
        benchmark.write_text(json.dumps({"leakage_checks": {"semantic_similarity_ceiling": .85}}), encoding="utf-8")
        with patch.object(target, "ROOT", root.resolve()), patch.object(target, "LOCAL_ROOT", local.resolve()), patch.object(target, "LEAKAGE_ROOT", leakage.resolve()), patch.object(target, "BENCHMARK_CONFIG", benchmark):
            return target.validate(evidence)

    def test_complete_hash_bound_matrix_passes_but_not_promotion(self):
        temp, root, local, leakage, evidence = self.make_evidence()
        self.addCleanup(temp.cleanup)
        result = self.run_validation(root, local, leakage, evidence)
        self.assertTrue(result["semantic_similarity_complete"])
        self.assertFalse(result["promotion_ready"])

    def test_missing_pair_fails(self):
        temp, root, local, leakage, evidence = self.make_evidence(include_pair=False)
        self.addCleanup(temp.cleanup)
        self.assertFalse(self.run_validation(root, local, leakage, evidence)["valid"])

    def test_hash_tamper_fails(self):
        temp, root, local, leakage, evidence = self.make_evidence(tamper=True)
        self.addCleanup(temp.cleanup)
        self.assertFalse(self.run_validation(root, local, leakage, evidence)["valid"])

    def test_threshold_regression_fails(self):
        temp, root, local, leakage, evidence = self.make_evidence(similarity=.9)
        self.addCleanup(temp.cleanup)
        self.assertFalse(self.run_validation(root, local, leakage, evidence)["valid"])

    def test_evidence_cannot_raise_registered_threshold(self):
        temp, root, local, leakage, evidence = self.make_evidence(similarity=.9, threshold=1.0)
        self.addCleanup(temp.cleanup)
        result = self.run_validation(root, local, leakage, evidence)
        self.assertFalse(result["valid"])
        self.assertTrue(any("configured ceiling" in error for error in result["errors"]))

    def test_online_tool_claim_fails(self):
        temp, root, local, leakage, evidence = self.make_evidence(offline=False)
        self.addCleanup(temp.cleanup)
        self.assertFalse(self.run_validation(root, local, leakage, evidence)["valid"])


if __name__ == "__main__":
    unittest.main()
