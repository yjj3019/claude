import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.export_fable_diagnostic_prompts import export


class FableDiagnosticPromptExportTest(unittest.TestCase):
    def test_exports_hash_bound_copy_paste_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plans = root / "plans"
            package = plans / "DIAGNOSTIC-A-package" / "artifacts"
            package.mkdir(parents=True)
            artifact = {
                "instruction_prefix": "Use evidence.", "user_prompt": "Report status.",
                "fixtures": [{"name": "evidence.md", "content": "Observed failure."}],
            }
            raw = (json.dumps(artifact) + "\n").encode()
            (package / "P-1-O-F.json").write_bytes(raw)
            plan = {
                "diagnostic_only": True, "repetitions": 1, "batch_id": "DIAGNOSTIC-A",
                "runs": [{
                    "run_id": "DIAGNOSTIC-A-P-1-O-F-R01", "requested_model": "claude-opus-4-8",
                    "variant_id": "O-F", "artifact_path": "artifacts/P-1-O-F.json",
                    "prompt_hash": hashlib.sha256(raw).hexdigest(),
                }],
            }
            plan_path = plans / "DIAGNOSTIC-A.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = export(plan_path, root / "prompts", allowed_root=root)
            prompt_path = root / "prompts" / result["items"][0]["prompt_path"]
            prompt = prompt_path.read_text(encoding="utf-8")
            prompt_hash = hashlib.sha256(prompt_path.read_bytes()).hexdigest()
        self.assertEqual(result["prompt_count"], 1)
        self.assertIn("Use evidence.\n\nReport status.", prompt)
        self.assertIn("### evidence.md\n\nObserved failure.", prompt)
        self.assertNotIn("checks", prompt)
        self.assertEqual(prompt_hash, result["items"][0]["prompt_sha256"])


if __name__ == "__main__":
    unittest.main()
