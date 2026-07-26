import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_fable_pilot.py"
SPEC = importlib.util.spec_from_file_location("prepare_fable_pilot_check", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FablePilotCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "fable-benchmark.json").read_text(encoding="utf-8"))

    def make_checked_output(self, root: Path) -> tuple[Path, dict]:
        plan_path = root / "PILOT-A-plan.json"
        package = root / "PILOT-A-package"
        plan = MODULE.build_plan(self.config, seed=3019, batch_id="PILOT-A", output_dir=package)
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return plan_path, plan

    def test_check_accepts_deterministic_output(self):
        with tempfile.TemporaryDirectory() as directory:
            plan_path, _ = self.make_checked_output(Path(directory))
            self.assertEqual(MODULE.check_checked_in(plan_path), [])

    def test_check_normalizes_only_git_checkout_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            plan_path, plan = self.make_checked_output(Path(directory))
            plan["repository_commit"] = "different-checkout"
            plan["working_tree_clean"] = not plan["working_tree_clean"]
            for run in plan["runs"]:
                run["repository_commit"] = "different-checkout"
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(MODULE.check_checked_in(plan_path), [])

    def test_check_rejects_plan_source_hash_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            plan_path, plan = self.make_checked_output(Path(directory))
            plan["source_tree_sha256"] = "0" * 64
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            errors = MODULE.check_checked_in(plan_path)
            self.assertTrue(any("plan is stale" in error for error in errors))

    def test_check_rejects_artifact_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            plan_path, plan = self.make_checked_output(Path(directory))
            artifact = plan_path.parent / "PILOT-A-package" / plan["artifacts"][0]["path"]
            artifact.write_text("tampered\n", encoding="utf-8")
            errors = MODULE.check_checked_in(plan_path)
            self.assertTrue(any("artifact is stale" in error for error in errors))

    def test_check_rejects_extra_package_file(self):
        with tempfile.TemporaryDirectory() as directory:
            plan_path, _ = self.make_checked_output(Path(directory))
            (plan_path.parent / "PILOT-A-package" / "unexpected.txt").write_text("extra", encoding="utf-8")
            errors = MODULE.check_checked_in(plan_path)
            self.assertTrue(any("file set is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
