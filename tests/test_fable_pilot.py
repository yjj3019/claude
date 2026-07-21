import importlib.util
import json
import unittest
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare_fable_pilot.py"
SPEC = importlib.util.spec_from_file_location("prepare_fable_pilot", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FablePilotPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "fable-benchmark.json").read_text(encoding="utf-8"))

    def test_plan_is_complete_and_deterministic(self):
        first_dir = tempfile.TemporaryDirectory()
        second_dir = tempfile.TemporaryDirectory()
        self.addCleanup(first_dir.cleanup)
        self.addCleanup(second_dir.cleanup)
        first = MODULE.build_plan(self.config, seed=3019, batch_id="PILOT-A", output_dir=Path(first_dir.name))
        second = MODULE.build_plan(self.config, seed=3019, batch_id="PILOT-A", output_dir=Path(second_dir.name))
        self.assertEqual(first, second)
        expected = len(self.config["variants"]) * len(self.config["pilot_cases"]) * 5
        self.assertEqual(first["run_count"], expected)
        self.assertEqual(len({run["run_id"] for run in first["runs"]}), expected)
        self.assertEqual(first["responses_imported"], 0)
        self.assertTrue(first["manual_smoke_ready"])
        self.assertFalse(first["promotion_ready"])
        self.assertEqual(first["artifact_count"], len(self.config["variants"]) * len(self.config["pilot_cases"]))
        self.assertEqual(MODULE.validate_plan(first, Path(first_dir.name)), [])

    def test_seed_changes_order_not_membership(self):
        first_dir = tempfile.TemporaryDirectory()
        second_dir = tempfile.TemporaryDirectory()
        self.addCleanup(first_dir.cleanup)
        self.addCleanup(second_dir.cleanup)
        first = MODULE.build_plan(self.config, seed=1, batch_id="PILOT-A", output_dir=Path(first_dir.name))
        second = MODULE.build_plan(self.config, seed=2, batch_id="PILOT-A", output_dir=Path(second_dir.name))
        first_ids = [run["run_id"] for run in first["runs"]]
        second_ids = [run["run_id"] for run in second["runs"]]
        self.assertNotEqual(first_ids, second_ids)
        self.assertEqual(set(first_ids), set(second_ids))

    def test_rejects_too_few_repetitions(self):
        with self.assertRaises(ValueError):
            with tempfile.TemporaryDirectory() as directory:
                MODULE.build_plan(self.config, seed=1, batch_id="PILOT-A", output_dir=Path(directory), repetitions=4)

    def test_detects_artifact_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            plan = MODULE.build_plan(self.config, seed=1, batch_id="PILOT-A", output_dir=output_dir)
            artifact = output_dir / plan["artifacts"][0]["path"]
            artifact.write_text("tampered", encoding="utf-8")
            errors = MODULE.validate_plan(plan, output_dir)
            self.assertTrue(any("hash mismatch" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
