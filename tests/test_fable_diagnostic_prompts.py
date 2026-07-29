import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_fable_diagnostic_prompts import OFFLINE_EVIDENCE_BANNER, SCENARIO_WARNINGS, export


def _write_plan(root: Path, artifact: dict, *, batch_id: str = "DIAGNOSTIC-A", repetitions: int = 1) -> Path:
    plans = root / "plans"
    package = plans / f"{batch_id}-package" / "artifacts"
    package.mkdir(parents=True)
    raw = (json.dumps(artifact) + "\n").encode()
    (package / "P-1-O-F.json").write_bytes(raw)
    prompt_hash = hashlib.sha256(raw).hexdigest()
    plan = {
        "diagnostic_only": True, "repetitions": repetitions, "batch_id": batch_id,
        "runs": [{
            "run_id": f"{batch_id}-P-1-O-F-R{repetition:02d}", "requested_model": "claude-opus-4-8",
            "variant_id": "O-F", "artifact_path": "artifacts/P-1-O-F.json",
            "prompt_hash": prompt_hash,
        } for repetition in range(1, repetitions + 1)],
    }
    plan_path = plans / f"{batch_id}.json"
    plan_path.write_text(json.dumps(plan), encoding="utf-8")
    return plan_path


class FableDiagnosticPromptExportTest(unittest.TestCase):
    def test_exports_hash_bound_copy_paste_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = {
                "instruction_prefix": "Use evidence.", "user_prompt": "Report status.",
                "fixtures": [{"name": "evidence.md", "content": "Observed failure."}],
            }
            plan_path = _write_plan(root, artifact)
            result = export(plan_path, root / "prompts", allowed_root=root)
            prompt_path = root / "prompts" / result["items"][0]["prompt_path"]
            prompt = prompt_path.read_text(encoding="utf-8")
            prompt_hash = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
        self.assertEqual(result["prompt_count"], 1)
        self.assertIn("Use evidence.\n\nReport status.", prompt)
        self.assertIn("### evidence.md\n\nObserved failure.", prompt)
        self.assertNotIn("checks", prompt)
        self.assertEqual(prompt_hash, result["items"][0]["prompt_sha256"])

    def test_every_export_includes_offline_evidence_banner(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = {"scenario_id": "PRIVATE-001", "user_prompt": "Report status.", "fixtures": []}
            plan_path = _write_plan(root, artifact)
            result = export(plan_path, root / "prompts", allowed_root=root)
            prompt = (root / "prompts" / result["items"][0]["prompt_path"]).read_text(encoding="utf-8")
        self.assertTrue(prompt.startswith(OFFLINE_EVIDENCE_BANNER))
        self.assertNotIn(SCENARIO_WARNINGS["PRIVATE-004"], prompt)

    def test_private_004_includes_destructive_command_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = {"scenario_id": "PRIVATE-004", "user_prompt": "Clean up /tmp/build_cache.", "fixtures": []}
            plan_path = _write_plan(root, artifact)
            result = export(plan_path, root / "prompts", allowed_root=root)
            prompt = (root / "prompts" / result["items"][0]["prompt_path"]).read_text(encoding="utf-8")
        self.assertIn(OFFLINE_EVIDENCE_BANNER, prompt)
        self.assertIn(SCENARIO_WARNINGS["PRIVATE-004"], prompt)
        self.assertLess(prompt.index(SCENARIO_WARNINGS["PRIVATE-004"]), prompt.index("Clean up"))

    def test_exports_a_repeated_diagnostic_plan(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = {"scenario_id": "PRIVATE-001", "user_prompt": "Report status.", "fixtures": []}
            plan_path = _write_plan(root, artifact, repetitions=3)
            result = export(plan_path, root / "prompts", allowed_root=root)
        self.assertEqual(result["prompt_count"], 3)
        self.assertEqual({item["run_id"][-3:] for item in result["items"]}, {"R01", "R02", "R03"})

    def test_rejects_export_of_a_plan_with_invalid_repetitions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = {"scenario_id": "PRIVATE-001", "user_prompt": "Report status.", "fixtures": []}
            plan_path = _write_plan(root, artifact)
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["repetitions"] = 0
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaises(ValueError):
                export(plan_path, root / "prompts", allowed_root=root)


if __name__ == "__main__":
    unittest.main()
