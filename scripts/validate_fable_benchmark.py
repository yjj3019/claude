#!/usr/bin/env python3
"""Validate the Fable/FEF comparison contract without calling a model API."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fable-benchmark.json"
SCHEMA = ROOT / "config" / "fable-benchmark.schema.json"


def validate(data: dict | None = None) -> dict:
    errors: list[str] = []
    if data is None:
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"valid": False, "errors": [f"cannot load benchmark config: {exc}"], "responses_imported": 0}
    if not isinstance(data, dict):
        return {"valid": False, "errors": ["benchmark config must be an object"], "responses_imported": 0}
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    required = set(schema["required"])
    missing = required - set(data)
    if missing:
        errors.append(f"benchmark config missing fields: {sorted(missing)}")

    if not re.fullmatch(r"FEF-FABLE-COMPARE-\d{3}", str(data.get("benchmark_id", ""))):
        errors.append("invalid benchmark_id")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(data.get("version", ""))):
        errors.append("invalid semantic version")

    variants = data.get("variants", [])
    if not isinstance(variants, list):
        variants = []
        errors.append("variants must be an array")
    variant_ids = [item.get("id") for item in variants if isinstance(item, dict)]
    if len(variant_ids) != len(variants):
        errors.append("every variant must be an object with an id")
    if len(variant_ids) != len(set(variant_ids)):
        errors.append("duplicate variant ID")
    required_variants = {"F5", "O-B", "O-K", "O-F", "S-B", "S-K", "S-F", "O-N", "S-N"}
    if set(variant_ids) != required_variants:
        errors.append(f"variant set mismatch: expected={sorted(required_variants)}, actual={sorted(variant_ids)}")
    allowed_frameworks = {"reference", "off", "kernel", "routed", "negative_control"}
    allowed_roles = {"reference", "baseline", "treatment", "control"}
    for item in variants:
        if not isinstance(item, dict):
            continue
        missing_variant = {"id", "model", "framework", "role", "prompt_sources"} - set(item)
        if missing_variant:
            errors.append(f"variant {item.get('id', '<unknown>')} missing fields: {sorted(missing_variant)}")
        if item.get("framework") not in allowed_frameworks:
            errors.append(f"variant {item.get('id', '<unknown>')} has invalid framework")
        if item.get("role") not in allowed_roles:
            errors.append(f"variant {item.get('id', '<unknown>')} has invalid role")
        sources = item.get("prompt_sources")
        if not isinstance(sources, list) or not all(isinstance(source, str) for source in sources):
            errors.append(f"variant {item.get('id', '<unknown>')} has invalid prompt_sources")
        else:
            for source in sources:
                if not (ROOT / source).is_file():
                    errors.append(f"variant {item.get('id', '<unknown>')} missing prompt source: {source}")

    controls = data.get("negative_control", {})
    if not isinstance(controls, dict):
        controls = {}
        errors.append("negative_control must be an object")
    if not controls.get("artifact_template") or "{variant_id}" not in controls.get("artifact_template", ""):
        errors.append("negative control artifact_template must include {variant_id}")
    tolerance = controls.get("maximum_word_count_difference_percent")
    if not isinstance(tolerance, (int, float)) or not 0 <= tolerance <= 10:
        errors.append("negative control word-count tolerance must be between 0 and 10 percent")
    if controls.get("must_not_contain_required_behavior_terms") is not True or controls.get("record_prompt_hash") is not True:
        errors.append("negative control irrelevance and prompt hash checks are required")
    if (controls.get("promotion_eligible") is not False
            or controls.get("purpose") != "attention_load_diagnostic_only"
            or controls.get("construction") != "natural_neutral_corpus"
            or controls.get("validation_status") != "candidate_not_promotion_gate"):
        errors.append("negative control must remain diagnostic-only and promotion-ineligible")

    manual_execution = data.get("manual_execution", {})
    expected_manual = {
        "surface": "claude_app",
        "prompt_role": "single_user_message_with_instruction_prefix",
        "fresh_chat_required": True,
        "project_instructions": "none",
        "memory_state": "disabled_or_empty",
        "surface_evidence_required": True,
    }
    if not isinstance(manual_execution, dict) or any(manual_execution.get(key) != value for key, value in expected_manual.items()):
        errors.append("manual execution isolation contract is incomplete")

    scenarios = data.get("scenarios", [])
    if not isinstance(scenarios, list):
        scenarios = []
        errors.append("scenarios must be an array")
    scenario_ids = [item.get("id") for item in scenarios if isinstance(item, dict)]
    if len(scenario_ids) != len(scenarios):
        errors.append("every scenario must be an object with an id")
    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("duplicate scenario ID")
    if any(not re.fullmatch(r"FB\d{3}", str(item)) for item in scenario_ids):
        errors.append("invalid scenario ID")
    if len(scenarios) < 14:
        errors.append("at least 14 scenarios are required")
    allowed_difficulties = {"easy", "medium", "hard"}
    allowed_provenance = {"distillation", "validation", "private_holdout", "out_of_domain"}
    for item in scenarios:
        if not isinstance(item, dict):
            continue
        missing_scenario = {"id", "title", "suite", "difficulty", "provenance", "required_behaviors", "hard_failures", "automated_checks"} - set(item)
        if missing_scenario:
            errors.append(f"{item.get('id', '<unknown>')} missing fields: {sorted(missing_scenario)}")
        if item.get("difficulty") not in allowed_difficulties:
            errors.append(f"{item.get('id', '<unknown>')} has invalid difficulty")
        if item.get("provenance") not in allowed_provenance:
            errors.append(f"{item.get('id', '<unknown>')} has invalid provenance")
        for field in ("required_behaviors", "hard_failures", "automated_checks"):
            if not isinstance(item.get(field), list) or not item.get(field) or not all(isinstance(value, str) for value in item.get(field, [])):
                errors.append(f"{item.get('id', '<unknown>')} has empty {field}")

    provenance = Counter(item.get("provenance") for item in scenarios if isinstance(item, dict))
    if provenance["private_holdout"] < 1:
        errors.append("private holdout scenario is required")
    out_domains = {item.get("domain") for item in scenarios if isinstance(item, dict) and item.get("provenance") == "out_of_domain"}
    if provenance["out_of_domain"] < 3 or len(out_domains - {None}) < 3:
        errors.append("at least three distinct out-of-domain scenarios and domains are required")

    execution = data.get("execution", {})
    if execution.get("minimum_repetitions", 0) < 5:
        errors.append("minimum_repetitions must be at least 5")
    required_metadata = set(execution.get("required_run_metadata", []))
    critical_metadata = {
        "requested_model", "served_model", "fallback_detected", "prompt_hash",
        "repository_commit", "captured_at", "response_path", "response_sha256", "source_surface"
    }
    if missing_metadata := critical_metadata - required_metadata:
        errors.append(f"missing critical run metadata: {sorted(missing_metadata)}")
    if not execution.get("exclude_unverified_fable_fallback"):
        errors.append("unverified Fable fallback must be excluded")

    gates = data.get("gates", {})
    if not gates.get("require_private_holdout"):
        errors.append("GO gate must require private holdout")
    if gates.get("minimum_independent_batches", 0) < 2:
        errors.append("GO gate must require at least two independent batches")
    if gates.get("minimum_valid_scenarios_per_suite", 0) < 5:
        errors.append("GO gate must require at least five independent scenarios per suite")
    if gates.get("minimum_out_of_domain_scenarios", 0) < 3:
        errors.append("GO gate must require at least three out-of-domain scenarios")
    critical_metrics = gates.get("critical_metrics", [])
    if not isinstance(critical_metrics, list) or len(critical_metrics) < 3:
        errors.append("GO gate must define critical_metrics")

    metrics = data.get("metrics", {})
    expected_metric_contract = {
        "unit_of_analysis": "independent_scenario_fixture",
        "repetitions_role": "reliability_estimation_only",
        "pairing_rule": "compare_condition_summaries_within_scenario_not_run_labels",
        "planned_run_accounting": "all_planned_runs_reported",
        "excluded_run_rule": "report_primary_bound_as_failure_and_secondary_complete_case",
    }
    if not isinstance(metrics, dict) or any(metrics.get(key) != value for key, value in expected_metric_contract.items()):
        errors.append("metric estimand, pairing, or missingness contract is incomplete")
    definitions = metrics.get("definitions", {}) if isinstance(metrics, dict) else {}
    required_definitions = {"task_success_rate", "hard_failure_rate", "completion_claim_accuracy", "factuality", "unsafe_compliance_rate"}
    if not isinstance(definitions, dict) or not required_definitions.issubset(definitions):
        errors.append("required metric definitions are missing")
    else:
        for metric, definition in definitions.items():
            if definition.get("direction") not in {"higher_is_better", "lower_is_better"}:
                errors.append(f"metric {metric} has no valid direction")
            if definition.get("missing_rule") != "count_as_failure":
                errors.append(f"metric {metric} must define conservative missingness")
            if definition.get("direction") == "lower_is_better" and definition.get("zero_baseline_rule") != "absolute_noninferiority_only":
                errors.append(f"metric {metric} must define the zero-baseline rule")

    leakage = data.get("leakage_checks", {})
    required_leakage = {"exact_hash", "normalized_ngram", "minhash", "semantic_similarity", "canary"}
    if not isinstance(leakage, dict) or not required_leakage.issubset(set(leakage.get("required", []))):
        errors.append("all required leakage checks must be configured")
    if leakage.get("record_tool_version") is not True or leakage.get("record_evidence_path") is not True:
        errors.append("leakage checks must record tool versions and evidence paths")

    pilot_cases = data.get("pilot_cases", [])
    if not isinstance(pilot_cases, list) or len(pilot_cases) < 2:
        errors.append("at least two pilot cases are required")
        pilot_cases = []
    pilot_ids = []
    for case in pilot_cases:
        if not isinstance(case, dict):
            errors.append("every pilot case must be an object")
            continue
        pilot_ids.append(case.get("id"))
        required_case = {"id", "title", "promotion_eligible", "user_prompt_path", "fixture_paths", "check_spec_path", "routed_prompt_sources"}
        if missing_case := required_case - set(case):
            errors.append(f"pilot case {case.get('id', '<unknown>')} missing fields: {sorted(missing_case)}")
        if not re.fullmatch(r"PB\d{3}", str(case.get("id", ""))):
            errors.append(f"pilot case {case.get('id', '<unknown>')} has invalid id")
        if case.get("promotion_eligible") is not False:
            errors.append(f"pilot case {case.get('id', '<unknown>')} must not be promotion eligible")
        paths = [case.get("user_prompt_path"), case.get("check_spec_path"), *case.get("fixture_paths", []), *case.get("routed_prompt_sources", [])]
        for relative in paths:
            if not isinstance(relative, str) or not (ROOT / relative).is_file():
                errors.append(f"pilot case {case.get('id', '<unknown>')} missing source: {relative}")
    if len(pilot_ids) != len(set(pilot_ids)):
        errors.append("duplicate pilot case ID")

    return {
        "valid": not errors,
        "benchmark_id": data.get("benchmark_id"),
        "variant_count": len(variant_ids),
        "scenario_count": len(scenarios),
        "pilot_case_count": len(pilot_cases),
        "suite_coverage": dict(sorted(Counter(item.get("suite") for item in scenarios if isinstance(item, dict)).items())),
        "provenance_coverage": dict(sorted(provenance.items())),
        "errors": errors,
        "responses_imported": 0
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.validate_only:
        parser.error("model execution is not implemented; use --validate-only")
    result = validate()
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
