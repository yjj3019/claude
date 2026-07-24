#!/usr/bin/env python3
"""Analyze scenario-level paired Fable/FEF results without treating repetitions as independent."""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fable-benchmark.json"


def quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def bootstrap_ci(differences: list[float], *, seed: int, samples: int) -> list[float]:
    rng = random.Random(seed)
    means = [sum(rng.choice(differences) for _ in differences) / len(differences) for _ in range(samples)]
    return [quantile(means, .025), quantile(means, .975)]


def mcnemar_exact(left: list[float], right: list[float]) -> dict:
    if any(value not in {0.0, 1.0} for value in (*left, *right)):
        return {"status": "not_applicable_nonbinary_scenario_summary", "p_value": None}
    b = sum(1 for a, z in zip(left, right) if a == 0 and z == 1)
    c = sum(1 for a, z in zip(left, right) if a == 1 and z == 0)
    discordant = b + c
    if discordant == 0:
        return {"status": "complete", "discordant": 0, "p_value": 1.0}
    tail = sum(math.comb(discordant, k) for k in range(min(b, c) + 1)) / (2 ** discordant)
    return {"status": "complete", "discordant": discordant, "p_value": min(1.0, 2 * tail)}


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    adjusted, running = {}, 0.0
    count = len(ordered)
    for index, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, (count - index) * value))
        adjusted[name] = running
    return adjusted


def analyze(document: dict, *, seed: int = 3019, bootstrap_samples: int = 5000,
            config_path: Path = CONFIG) -> dict:
    errors, warnings = [], []
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    if document.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    batches = document.get("batches")
    if not isinstance(batches, list) or len(set(batches)) < config["gates"]["minimum_independent_batches"]:
        errors.append("at least two distinct independent batches are required")
        batches = batches if isinstance(batches, list) else []
    definitions = config["metrics"]["definitions"]
    rows = document.get("scenario_results")
    if not isinstance(rows, list):
        errors.append("scenario_results must be an array")
        rows = []
    indexed, scenario_batches = {}, defaultdict(set)
    for index, row in enumerate(rows):
        error_count = len(errors)
        if not isinstance(row, dict):
            errors.append(f"scenario_results[{index}] must be an object")
            continue
        key = (row.get("batch_id"), row.get("scenario_id"), row.get("variant_id"))
        if key in indexed or key[0] not in batches or not all(isinstance(item, str) and item for item in key):
            errors.append(f"invalid or duplicate scenario result at index {index}")
            continue
        planned, observed = row.get("planned_runs"), row.get("observed_runs")
        if not isinstance(planned, int) or planned < config["execution"]["minimum_repetitions"] or not isinstance(observed, int) or observed < 0 or observed > planned:
            errors.append(f"invalid run counts at index {index}")
        metrics = row.get("metrics")
        if not isinstance(metrics, dict) or set(metrics) != set(definitions):
            errors.append(f"metric set mismatch at index {index}")
        elif any(not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1 for value in metrics.values()):
            errors.append(f"metrics must be numeric rates from 0 to 1 at index {index}")
        if len(errors) > error_count:
            continue
        conservative = {}
        if isinstance(metrics, dict) and isinstance(planned, int) and planned > 0 and isinstance(observed, int) and 0 <= observed <= planned:
            for metric, value in metrics.items():
                if metric in definitions and isinstance(value, (int, float)) and not isinstance(value, bool):
                    if definitions[metric]["direction"] == "higher_is_better":
                        conservative[metric] = value * observed / planned
                    else:
                        conservative[metric] = (value * observed + planned - observed) / planned
        indexed[key] = {**row, "conservative_metrics": conservative}
        scenario_batches[(key[1], key[2])].add(key[0])
    treatment_comparisons = {"O-F_minus_O-B": ("O-F", "O-B"), "S-F_minus_S-B": ("S-F", "S-B")}
    placebo_comparisons = {"O-N_minus_O-B": ("O-N", "O-B"), "S-N_minus_S-B": ("S-N", "S-B")}
    comparisons = {**treatment_comparisons, **placebo_comparisons}
    results, raw_p = {}, {}
    for comparison, (treatment, baseline) in comparisons.items():
        scenarios = sorted({scenario for _, scenario, variant in indexed if variant == treatment} &
                           {scenario for _, scenario, variant in indexed if variant == baseline})
        complete = [scenario for scenario in scenarios if all((batch, scenario, variant) in indexed
                    for batch, variant in itertools.product(batches, (treatment, baseline)))]
        if len(complete) < config["gates"]["minimum_valid_scenarios_per_suite"]:
            message = f"{comparison} has fewer than required complete independent scenarios"
            (errors if comparison in treatment_comparisons else warnings).append(message)
            continue
        metric_results = {}
        for metric, definition in definitions.items():
            treatment_values, baseline_values = [], []
            for scenario in complete:
                treatment_values.append(sum(indexed[(batch, scenario, treatment)]["conservative_metrics"][metric] for batch in batches) / len(batches))
                baseline_values.append(sum(indexed[(batch, scenario, baseline)]["conservative_metrics"][metric] for batch in batches) / len(batches))
            sign = 1 if definition["direction"] == "higher_is_better" else -1
            differences = [sign * (t - b) for t, b in zip(treatment_values, baseline_values)]
            effect = sum(differences) / len(differences)
            test = mcnemar_exact(baseline_values, treatment_values)
            if test["p_value"] is not None:
                raw_p[f"{comparison}:{metric}"] = test["p_value"]
            metric_results[metric] = {
                "direction": definition["direction"], "improvement_effect": effect,
                "bootstrap_95_ci": bootstrap_ci(differences, seed=seed + len(metric_results), samples=bootstrap_samples),
                "treatment_mean": sum(treatment_values) / len(treatment_values),
                "baseline_mean": sum(baseline_values) / len(baseline_values), "mcnemar": test,
            }
        results[comparison] = {"scenario_count": len(complete), "metrics": metric_results}
    adjusted = holm(raw_p)
    for key, value in adjusted.items():
        comparison, metric = key.split(":", 1)
        results[comparison]["metrics"][metric]["holm_adjusted_p"] = value
    quality_gate = not errors
    for name in treatment_comparisons:
        if name not in results:
            quality_gate = False
            continue
        comparison = results[name]
        success = comparison["metrics"]["task_success_rate"]
        failure = comparison["metrics"]["hard_failure_rate"]
        if success["improvement_effect"] < config["gates"]["minimum_success_rate_gain_points"] / 100:
            quality_gate = False
        if success["bootstrap_95_ci"][0] <= 0:
            quality_gate = False
        if failure["bootstrap_95_ci"][0] <= 0:
            quality_gate = False
        if failure["baseline_mean"] > 0:
            reduction = failure["improvement_effect"] / failure["baseline_mean"] * 100
            if reduction < config["gates"]["minimum_hard_failure_relative_reduction_percent"]:
                quality_gate = False
        elif failure["treatment_mean"] > config["gates"]["maximum_critical_regression_percentage_points"] / 100:
            quality_gate = False
        for metric in config["gates"]["critical_metrics"]:
            if comparison["metrics"][metric]["improvement_effect"] < -config["gates"]["maximum_critical_regression_percentage_points"] / 100:
                quality_gate = False
    placebo_signals = {}
    for name in placebo_comparisons:
        if name not in results:
            continue
        success = results[name]["metrics"]["task_success_rate"]
        failure = results[name]["metrics"]["hard_failure_rate"]
        success_signal = (success["improvement_effect"] >= config["gates"]["minimum_success_rate_gain_points"] / 100
                          and success["bootstrap_95_ci"][0] > 0)
        failure_signal = (failure["baseline_mean"] > 0 and failure["bootstrap_95_ci"][0] > 0
                          and failure["improvement_effect"] / failure["baseline_mean"] * 100
                          >= config["gates"]["minimum_hard_failure_relative_reduction_percent"])
        placebo_signals[name] = {"task_success_signal": success_signal, "hard_failure_signal": failure_signal}
    placebo_complete = len(placebo_signals) == len(placebo_comparisons)
    placebo_gate = placebo_complete and not any(
        signal for comparison in placebo_signals.values() for signal in comparison.values()
    )
    blockers = ["rater_reliability_not_supplied", "final_evidence_gate_not_run"]
    if not placebo_gate:
        blockers.append("placebo_gate_not_passed")
    return {"valid": not errors, "quality_gate_pass": quality_gate, "benchmark_promotion_ready": False,
            "batch_ids": batches,
            "unit_of_analysis": "independent_scenario_fixture", "repetitions_treated_as_independent": False,
            "comparisons": results, "errors": errors, "warnings": warnings,
            "placebo_gate_pass": placebo_gate,
            "placebo": {"status": "complete" if placebo_complete else "not_run", "signals": placebo_signals},
            "promotion_blockers": blockers}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=3019)
    parser.add_argument("--bootstrap-samples", type=int, default=5000)
    args = parser.parse_args()
    if args.bootstrap_samples < 100:
        parser.error("bootstrap samples must be at least 100")
    result = analyze(json.loads(args.input.read_text(encoding="utf-8-sig")), seed=args.seed,
                     bootstrap_samples=args.bootstrap_samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in ("valid", "quality_gate_pass", "benchmark_promotion_ready", "errors")}, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
