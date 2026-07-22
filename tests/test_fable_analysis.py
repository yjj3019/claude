import copy
import unittest

from scripts.analyze_fable_results import analyze


class FableAnalysisTest(unittest.TestCase):
    def document(self):
        rows = []
        for batch in ("A", "B"):
            for scenario in range(5):
                for variant in ("O-B", "O-F", "S-B", "S-F"):
                    treatment = variant.endswith("-F")
                    rows.append({
                        "batch_id": batch, "scenario_id": f"P-{scenario}", "variant_id": variant,
                        "planned_runs": 5, "observed_runs": 5,
                        "metrics": {
                            "task_success_rate": .8 if treatment else .4,
                            "hard_failure_rate": .1 if treatment else .4,
                            "completion_claim_accuracy": .9 if treatment else .8,
                            "factuality": .9 if treatment else .8,
                            "unsafe_compliance_rate": 0,
                        },
                    })
        return {"schema_version": "1.0", "batches": ["A", "B"], "scenario_results": rows}

    def test_quality_gate_uses_scenarios_not_repetitions(self):
        result = analyze(self.document(), bootstrap_samples=200)
        self.assertTrue(result["valid"])
        self.assertTrue(result["quality_gate_pass"])
        self.assertFalse(result["benchmark_promotion_ready"])
        self.assertEqual(result["comparisons"]["O-F_minus_O-B"]["scenario_count"], 5)
        self.assertFalse(result["repetitions_treated_as_independent"])
        self.assertEqual(
            result["comparisons"]["O-F_minus_O-B"]["metrics"]["task_success_rate"]["mcnemar"]["status"],
            "not_applicable_nonbinary_scenario_summary",
        )

    def test_requires_two_independent_batches(self):
        document = self.document()
        document["batches"] = ["A"]
        document["scenario_results"] = [row for row in document["scenario_results"] if row["batch_id"] == "A"]
        self.assertFalse(analyze(document, bootstrap_samples=200)["valid"])

    def test_critical_metric_regression_fails_quality_gate(self):
        document = copy.deepcopy(self.document())
        for row in document["scenario_results"]:
            if row["variant_id"].endswith("-F"):
                row["metrics"]["factuality"] = .5
        result = analyze(document, bootstrap_samples=200)
        self.assertTrue(result["valid"])
        self.assertFalse(result["quality_gate_pass"])

    def test_incomplete_scenario_pair_fails(self):
        document = self.document()
        document["scenario_results"] = [row for row in document["scenario_results"]
                                        if not (row["batch_id"] == "B" and row["scenario_id"] == "P-4" and row["variant_id"] == "O-F")]
        self.assertFalse(analyze(document, bootstrap_samples=200)["valid"])

    def test_missing_runs_are_conservatively_counted_as_failures(self):
        document = self.document()
        for row in document["scenario_results"]:
            if row["variant_id"].endswith("-F"):
                row["observed_runs"] = 1
        result = analyze(document, bootstrap_samples=200)
        self.assertTrue(result["valid"])
        self.assertFalse(result["quality_gate_pass"])
        treatment = result["comparisons"]["O-F_minus_O-B"]["metrics"]["task_success_rate"]["treatment_mean"]
        self.assertAlmostEqual(treatment, .16)


if __name__ == "__main__":
    unittest.main()
