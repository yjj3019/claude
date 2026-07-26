import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


PREPARE = load_script("prepare_fable_pilot")
IMPORTER = load_script("import_fable_response")


class ManualResponseImportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "fable-benchmark.json").read_text(encoding="utf-8"))

    def setup_run(self, root: Path, variant_id: str):
        package = root / "package"
        plan = PREPARE.build_plan(self.config, seed=1, batch_id="PILOT-A", output_dir=package)
        run = next(item for item in plan["runs"] if item["variant_id"] == variant_id)
        response = root / "response.md"
        response.write_text("Verification failed; completion is not established.", encoding="utf-8")
        return plan, run, response, package

    def do_import(self, root: Path, variant_id="O-F", **overrides):
        plan, run, response, package = self.setup_run(root, variant_id)
        arguments = {
            "plan": plan, "run_id": run["run_id"], "response_file": response,
            "package_dir": package, "output_dir": root / "local" / "imported",
            "served_model": run["requested_model"], "fallback_detected": False,
            "source_surface": "claude_app", "sanitized_confirmed": True,
            "allowed_root": root / "local"
        }
        arguments.update(overrides)
        return IMPORTER.import_response(**arguments), arguments

    def test_imports_manual_response(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result, _ = self.do_import(root)
            self.assertEqual(result["status"], "imported")
            self.assertTrue((root / "local" / "imported" / result["response_path"]).is_file())

    def test_excludes_unknown_fable_response(self):
        with tempfile.TemporaryDirectory() as directory:
            result, _ = self.do_import(Path(directory), "F5", served_model=None, fallback_detected=None)
            self.assertEqual(result["status"], "excluded")

    def test_excludes_confirmed_fable_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            result, _ = self.do_import(
                Path(directory), "F5", served_model="claude-opus-4-8", fallback_detected=True
            )
            self.assertEqual(result["status"], "excluded")

    def test_excludes_served_model_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            result, _ = self.do_import(Path(directory), "O-F", served_model="claude-sonnet-5")
            self.assertEqual(result["status"], "excluded")

    def test_rejects_duplicate_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, arguments = self.do_import(root)
            with self.assertRaises(FileExistsError):
                IMPORTER.import_response(**arguments)

    def test_rejects_path_traversal_run_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, response, package = self.setup_run(root, "O-F")
            malicious = copy.deepcopy(plan)
            malicious["runs"][0]["run_id"] = "../../escape"
            with self.assertRaises(ValueError):
                IMPORTER.import_response(
                    malicious, run_id="../../escape", response_file=response, package_dir=package,
                    output_dir=root / "local" / "imported", served_model=run["requested_model"],
                    fallback_detected=False, source_surface="claude_app", sanitized_confirmed=True,
                    allowed_root=root / "local"
                )

    def test_rejects_tampered_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, response, package = self.setup_run(root, "O-F")
            (package / run["artifact_path"]).write_text("tampered", encoding="utf-8")
            with self.assertRaises(ValueError):
                IMPORTER.import_response(
                    plan, run_id=run["run_id"], response_file=response, package_dir=package,
                    output_dir=root / "local" / "imported", served_model=run["requested_model"],
                    fallback_detected=False, source_surface="claude_app", sanitized_confirmed=True,
                    allowed_root=root / "local"
                )

    def test_rejects_possible_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan, run, response, package = self.setup_run(root, "O-F")
            response.write_text("api_key = definitely-sensitive-value", encoding="utf-8")
            with self.assertRaises(ValueError):
                IMPORTER.import_response(
                    plan, run_id=run["run_id"], response_file=response, package_dir=package,
                    output_dir=root / "local" / "imported", served_model=run["requested_model"],
                    fallback_detected=False, source_surface="claude_app", sanitized_confirmed=True,
                    allowed_root=root / "local"
                )
