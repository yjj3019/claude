import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import scripts.prepare_fable_holdout_plan as compiler
import scripts.validate_fable_holdout as holdout


class FableHoldoutPlanTest(unittest.TestCase):
    def make_dataset(self, count=5):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        entries = []
        for index in range(count):
            case = root / f"P-{index}"
            case.mkdir()
            values = {
                "prompt.md": f"private prompt {index}".encode(),
                "evidence.md": f"private evidence {index}".encode(),
                "checks.json": json.dumps({"secret_answer": f"answer-{index}"}).encode(),
            }
            for name, raw in values.items():
                (case / name).write_bytes(raw)
            entries.append({
                "scenario_id": f"P-{index}", "suite": "evidence", "route_id": "research",
                "user_prompt": {"path": f"P-{index}/prompt.md", "sha256": hashlib.sha256(values["prompt.md"]).hexdigest()},
                "fixture_files": [{"path": f"P-{index}/evidence.md", "sha256": hashlib.sha256(values["evidence.md"]).hexdigest()}],
                "check_spec": {"path": f"P-{index}/checks.json", "sha256": hashlib.sha256(values["checks.json"]).hexdigest()},
                "provenance": "private_holdout", "independently_authored": True,
                "exposed_to_distillation": False,
                "canary_sha256": hashlib.sha256(f"canary-{index}".encode()).hexdigest(),
            })
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "manifest_version": "1.1", "dataset_id": "PRIVATE-D1", "created_at": "2026-07-22",
            "custodian_id": "C-1", "entries": entries,
        }), encoding="utf-8")
        return temp, root, manifest

    def compile(self, root, manifest, output):
        with patch.object(holdout, "LOCAL_HOLDOUT", root.resolve()), patch.object(compiler, "LOCAL_HOLDOUT", root.resolve()):
            return compiler.compile_plan(manifest, output, seed=17, batch_id="PRIVATE-A")

    def test_compiles_blinded_execution_package(self):
        temp, root, manifest = self.make_dataset()
        self.addCleanup(temp.cleanup)
        output = root / "plans" / "private-a.json"
        result = self.compile(root, manifest, output)
        self.assertEqual(result["artifact_count"], 45)
        self.assertEqual(result["run_count"], 225)
        self.assertFalse(result["benchmark_promotion_ready"])
        artifact = json.loads((root / "plans" / "private-a-package" / "artifacts" / "P-0-O-F.json").read_text(encoding="utf-8"))
        rendered = json.dumps(artifact)
        self.assertNotIn("answer-0", rendered)
        self.assertNotIn("canary-0", rendered)
        self.assertTrue(any(item["path"] == "modules/Research.md" for item in artifact["source_metadata"]))
        neutral = json.loads((root / "plans" / "private-a-package" / "artifacts" / "P-0-O-N.json").read_text(encoding="utf-8"))
        self.assertEqual(len(neutral["instruction_prefix"].split()), len(artifact["instruction_prefix"].split()))

    def test_rejects_underfilled_intake(self):
        temp, root, manifest = self.make_dataset(1)
        self.addCleanup(temp.cleanup)
        with self.assertRaises(ValueError):
            self.compile(root, manifest, root / "plan.json")

    def test_refuses_overwrite(self):
        temp, root, manifest = self.make_dataset()
        self.addCleanup(temp.cleanup)
        output = root / "plan.json"
        self.compile(root, manifest, output)
        with self.assertRaises(FileExistsError):
            self.compile(root, manifest, output)


if __name__ == "__main__":
    unittest.main()
