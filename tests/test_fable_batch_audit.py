import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_fable_batch import audit, canonical_plan_hash


class FableBatchAuditTest(unittest.TestCase):
    def make_batch(self, statuses=("imported", "excluded")):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        imports = root / "imports"
        imports.mkdir()
        runs = []
        for index in range(2):
            runs.append({
                "run_id": f"B-P-{index}-O-F-R01", "scenario_id": f"P-{index}", "variant_id": "O-F",
                "provenance": "private_holdout" if index == 0 else "out_of_domain",
                "requested_model": "claude-opus-4-8", "prompt_hash": "a" * 64,
                "repository_commit": "commit-1",
            })
        plan = {"dataset_id": "PRIVATE-HOLDOUT", "manifest_sha256": "a" * 64,
                "run_count": len(runs), "runs": runs}
        plan_path = root / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        plan_hash = canonical_plan_hash(plan)
        for run, status in zip(runs, statuses):
            response = f"response for {run['run_id']}".encode()
            response_name = f"{run['run_id']}.md"
            (imports / response_name).write_bytes(response)
            metadata = {
                **run, "plan_sha256": plan_hash, "status": status,
                "exclusion_reason": "model evidence unavailable" if status == "excluded" else None,
                "response_path": response_name, "response_sha256": hashlib.sha256(response).hexdigest(),
                "evidence_status": "unavailable", "evidence_path": None, "evidence_sha256": None,
            }
            (imports / f"{run['run_id']}.json").write_text(json.dumps(metadata), encoding="utf-8")
        return temp, root, plan_path, imports

    def test_complete_batch_is_scoring_ready_with_conservative_exclusion(self):
        temp, root, plan, imports = self.make_batch()
        self.addCleanup(temp.cleanup)
        result = audit(plan, imports, allowed_root=root)
        self.assertTrue(result["scoring_ready"])
        self.assertEqual(result["conservative_failure_bound"]["count"], 1)
        self.assertFalse(result["benchmark_promotion_ready"])
        self.assertEqual(result["scenario_provenance"]["P-1"], "out_of_domain")

    def test_missing_run_is_valid_but_incomplete_and_bounded_as_failure(self):
        temp, root, plan, imports = self.make_batch(("imported",))
        self.addCleanup(temp.cleanup)
        result = audit(plan, imports, allowed_root=root)
        self.assertTrue(result["valid"])
        self.assertFalse(result["collection_complete"])
        self.assertEqual(result["missing_runs"], 1)
        self.assertEqual(result["conservative_failure_bound"]["count"], 1)

    def test_response_tamper_fails(self):
        temp, root, plan, imports = self.make_batch()
        self.addCleanup(temp.cleanup)
        next(imports.glob("*.md")).write_text("tampered", encoding="utf-8")
        self.assertFalse(audit(plan, imports, allowed_root=root)["valid"])

    def test_unplanned_result_fails(self):
        temp, root, plan, imports = self.make_batch()
        self.addCleanup(temp.cleanup)
        (imports / "extra.json").write_text(json.dumps({"run_id": "UNPLANNED"}), encoding="utf-8")
        self.assertFalse(audit(plan, imports, allowed_root=root)["valid"])

    def test_json_surface_evidence_is_not_treated_as_run_metadata(self):
        temp, root, plan, imports = self.make_batch()
        self.addCleanup(temp.cleanup)
        (imports / "B-P-0-O-F-R01.evidence.json").write_text(json.dumps({"served_model": "verified"}), encoding="utf-8")
        result = audit(plan, imports, allowed_root=root)
        self.assertTrue(result["valid"])
        self.assertEqual(result["observed_results"], 2)


if __name__ == "__main__":
    unittest.main()
