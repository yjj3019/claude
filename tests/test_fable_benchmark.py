import importlib.util
import copy
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_fable_benchmark.py"
SPEC = importlib.util.spec_from_file_location("validate_fable_benchmark", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class FableBenchmarkContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config" / "fable-benchmark.json").read_text(encoding="utf-8"))

    def test_contract_is_valid(self):
        result = MODULE.validate()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["variant_count"], 9)
        self.assertGreaterEqual(result["scenario_count"], 14)

    def test_holdout_and_transfer_are_covered(self):
        result = MODULE.validate()
        self.assertGreater(result["provenance_coverage"].get("private_holdout", 0), 0)
        self.assertGreater(result["provenance_coverage"].get("out_of_domain", 0), 0)

    def test_rejects_invalid_nested_variant(self):
        data = copy.deepcopy(self.config)
        data["variants"][0]["framework"] = "invalid"
        result = MODULE.validate(data)
        self.assertFalse(result["valid"])
        self.assertTrue(any("invalid framework" in error for error in result["errors"]))

    def test_rejects_missing_scenario_field_without_crashing(self):
        data = copy.deepcopy(self.config)
        del data["scenarios"][0]["id"]
        result = MODULE.validate(data)
        self.assertFalse(result["valid"])
        self.assertTrue(result["errors"])

    def test_rejects_weak_negative_control(self):
        data = copy.deepcopy(self.config)
        data["negative_control"]["maximum_word_count_difference_percent"] = 25
        result = MODULE.validate(data)
        self.assertFalse(result["valid"])

    def test_rejects_single_out_of_domain_case(self):
        data = copy.deepcopy(self.config)
        for scenario in data["scenarios"]:
            if scenario.get("id") in {"FB013", "FB014"}:
                scenario["provenance"] = "private_holdout"
        result = MODULE.validate(data)
        self.assertFalse(result["valid"])
        self.assertTrue(any("three distinct" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
