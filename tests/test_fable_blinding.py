import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_blinded_fable.py"
SPEC = importlib.util.spec_from_file_location("export_blinded_fable", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class BlindedExportTest(unittest.TestCase):
    def test_exports_without_variant_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            imports = root / "imports"
            imports.mkdir()
            response = b"A captured answer"
            (imports / "RUN-1.md").write_bytes(response)
            metadata = {
                "run_id": "RUN-1", "scenario_id": "PB001", "variant_id": "O-F",
                "requested_model": "claude-opus-4-8", "served_model": "claude-opus-4-8",
                "response_path": "RUN-1.md", "response_sha256": MODULE.sha256_bytes(response),
                "status": "imported"
            }
            (imports / "RUN-1.json").write_text(json.dumps(metadata), encoding="utf-8")
            blinded = root / "blinded"
            mapping = root / "private" / "mapping.json"
            result = MODULE.export_blinded(imports, blinded, mapping, seed=3019, allowed_root=root)
            self.assertEqual(result["eligible_responses"], 1)
            ballot = (blinded / "ballot.json").read_text(encoding="utf-8")
            self.assertNotIn("O-F", ballot)
            self.assertNotIn("claude-opus", ballot)
            self.assertIn("O-F", mapping.read_text(encoding="utf-8"))

    def test_rejects_tampered_response(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            imports = root / "imports"
            imports.mkdir()
            (imports / "RUN-1.md").write_text("tampered", encoding="utf-8")
            metadata = {
                "run_id": "RUN-1", "response_path": "RUN-1.md",
                "response_sha256": "0" * 64, "status": "imported"
            }
            (imports / "RUN-1.json").write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.export_blinded(imports, root / "blinded", root / "mapping.json", seed=1, allowed_root=root)
