import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.prepare_fable_holdout_plan as compiler
import scripts.preflight_fable_private as preflight
import scripts.validate_fable_holdout as holdout
import scripts.validate_fable_provenance as provenance
import scripts.validate_fable_semantic_evidence as semantic
from scripts.check_fable_leakage import analyze, load_texts
import tests.test_fable_holdout_plan as plan_helpers


class FablePrivatePreflightTest(unittest.TestCase):
    def make_bundle(self):
        helper = plan_helpers.FableHoldoutPlanTest()
        temp, root, manifest = helper.make_dataset()
        leakage = root / "leakage"
        leakage.mkdir()
        reference = root / "reference.md"
        reference.write_text("independent reference corpus with unrelated wording", encoding="utf-8")
        manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
        candidate_paths = []
        for entry in manifest_data["entries"]:
            for spec in (entry["user_prompt"], entry["check_spec"], *entry["fixture_files"]):
                candidate_paths.append(root / spec["path"])
        candidates, references = load_texts(candidate_paths), load_texts([reference])
        canary_path = root / "canaries.txt"
        canary_values = [f"canary-{index}" for index in range(5)]
        canary_path.write_text("\n".join(canary_values) + "\n", encoding="utf-8")
        lexical = analyze(candidates, references, ngram_size=8, ceiling=.8, canaries=canary_values)
        lexical_path = leakage / "lexical.json"
        lexical_path.write_text(json.dumps(lexical), encoding="utf-8")
        pairs = [{"candidate_sha256": item["sha256"], "reference_sha256": references[0]["sha256"], "similarity": .1}
                 for item in candidates]
        semantic_data = {
            "evidence_version": "1.0", "generated_at": "2026-07-22T00:00:00Z",
            "tool": {"name": "offline", "version": "1", "model": "local@rev", "offline": True},
            "threshold": .85, "candidates": lexical["candidates"], "references": lexical["references"], "pairs": pairs,
        }
        semantic_path = leakage / "semantic.json"
        semantic_path.write_text(json.dumps(semantic_data), encoding="utf-8")
        provenance_path = root / "provenance.json"
        provenance_path.write_text(json.dumps({
            "evidence_version": "1.0", "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            "dataset_id": manifest_data["dataset_id"], "custodian_id": manifest_data["custodian_id"],
            "authoring_method": "human", "target_model_involved": False,
            "distillation_material_access": False, "attestor_id": "A-1",
            "attested_at": "2026-07-24T00:00:00Z",
        }), encoding="utf-8")
        plan_path = root / "plan.json"
        with patch.object(holdout, "LOCAL_HOLDOUT", root.resolve()), patch.object(compiler, "LOCAL_HOLDOUT", root.resolve()):
            compiler.compile_plan(manifest, plan_path, seed=3, batch_id="PRIVATE-A")
        return temp, root, manifest, lexical_path, semantic_path, provenance_path, plan_path, canary_path

    def run_preflight(self, root, manifest, lexical, semantic_path, provenance_path, plan, canary_path):
        with patch.object(holdout, "LOCAL_HOLDOUT", root.resolve()), \
             patch.object(preflight, "LOCAL_HOLDOUT", root.resolve()), \
             patch.object(provenance, "LOCAL_HOLDOUT", root.resolve()), \
             patch.object(semantic, "ROOT", root.resolve()), \
             patch.object(semantic, "LOCAL_ROOT", root.resolve()), \
             patch.object(semantic, "LEAKAGE_ROOT", (root / "leakage").resolve()):
            return preflight.validate_preflight(manifest, lexical, semantic_path, provenance_path, plan, canary_path)

    def test_all_evidence_must_bind_before_execution(self):
        temp, root, manifest, lexical, semantic_path, provenance_path, plan, canary_path = self.make_bundle()
        self.addCleanup(temp.cleanup)
        result = self.run_preflight(root, manifest, lexical, semantic_path, provenance_path, plan, canary_path)
        self.assertTrue(result["execution_ready"])
        self.assertFalse(result["benchmark_promotion_ready"])

    def test_semantic_candidate_omission_blocks_execution(self):
        temp, root, manifest, lexical, semantic_path, provenance_path, plan, canary_path = self.make_bundle()
        self.addCleanup(temp.cleanup)
        data = json.loads(semantic_path.read_text(encoding="utf-8"))
        omitted = data["candidates"].pop()
        data["pairs"] = [pair for pair in data["pairs"] if pair["candidate_sha256"] != omitted["sha256"]]
        semantic_path.write_text(json.dumps(data), encoding="utf-8")
        result = self.run_preflight(root, manifest, lexical, semantic_path, provenance_path, plan, canary_path)
        self.assertFalse(result["execution_ready"])
        self.assertTrue(any("semantic evidence candidates" in error for error in result["errors"]))

    def test_canary_substitution_blocks_execution(self):
        temp, root, manifest, lexical, semantic_path, provenance_path, plan, canary_path = self.make_bundle()
        self.addCleanup(temp.cleanup)
        canary_path.write_text("substituted-canary\n", encoding="utf-8")
        result = self.run_preflight(root, manifest, lexical, semantic_path, provenance_path, plan, canary_path)
        self.assertFalse(result["execution_ready"])
        self.assertTrue(any("canary values" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
