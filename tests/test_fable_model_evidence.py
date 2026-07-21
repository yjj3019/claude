import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


PREPARE = load_script("prepare_fable_pilot")
IMPORTER = load_script("import_fable_response")


class ModelEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "fable-benchmark.json").read_text(encoding="utf-8"))

    def import_fable(self, root, evidence=True, **overrides):
        package = root / "package"
        plan = PREPARE.build_plan(self.config, seed=1, batch_id="PILOT-A", output_dir=package)
        run = next(item for item in plan["runs"] if item["variant_id"] == "F5")
        response = root / "response.md"
        response.write_text("No completion claim without verification.", encoding="utf-8")
        evidence_file = root / "surface.json" if evidence else None
        if evidence_file:
            evidence_file.write_text(json.dumps({"surface": "claude_app", "model": run["requested_model"], "fallback": False}), encoding="utf-8")
        arguments = dict(
            plan=plan, run_id=run["run_id"], response_file=response, package_dir=package,
            output_dir=root / "local" / "imported", served_model=run["requested_model"],
            fallback_detected=False, source_surface="claude_app", sanitized_confirmed=True,
            evidence_file=evidence_file, evidence_sanitized_confirmed=evidence,
            allowed_root=root / "local"
        )
        arguments.update(overrides)
        return IMPORTER.import_response(**arguments)

    def test_verified_evidence_is_hashed_and_includes_fable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.import_fable(root)
            self.assertEqual(result["status"], "imported")
            self.assertEqual(result["evidence_status"], "verified")
            self.assertEqual(len(result["evidence_sha256"]), 64)
            self.assertTrue((root / "local" / "imported" / result["evidence_path"]).is_file())

    def test_missing_evidence_excludes_fable(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.import_fable(Path(directory), evidence=False)
            self.assertEqual(result["status"], "excluded")
            self.assertEqual(result["evidence_status"], "unavailable")

    def test_rejects_unsafe_evidence_format(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "surface.png"
            evidence.write_bytes(b"not an image metadata file")
            with self.assertRaises(ValueError):
                self.import_fable(root, evidence_file=evidence, evidence_sanitized_confirmed=True)

    def test_rejects_secret_in_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "surface.txt"
            evidence.write_text("access_token=do-not-store-this", encoding="utf-8")
            with self.assertRaises(ValueError):
                self.import_fable(root, evidence_file=evidence, evidence_sanitized_confirmed=True)


if __name__ == "__main__":
    unittest.main()
