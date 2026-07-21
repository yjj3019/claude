#!/usr/bin/env python3
"""Compile deterministic manual smoke-pilot artifacts and a randomized plan."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "fable-benchmark.json"
PLAN_SCHEMA = ROOT / "config" / "fable-plan.schema.json"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_output(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()


def read_sources(paths: list[str]) -> tuple[str, list[dict]]:
    chunks, metadata = [], []
    for relative in paths:
        content = (ROOT / relative).read_text(encoding="utf-8-sig")
        chunks.append(f"<!-- SOURCE: {relative} -->\n{content.rstrip()}")
        metadata.append({"path": relative, "sha256": sha256_bytes(content.encode("utf-8"))})
    return "\n\n".join(chunks), metadata


def word_count(text: str) -> int:
    return len(text.split())


def matched_neutral_prompt(template: str, target_words: int) -> str:
    words = template.split()
    if not words:
        raise ValueError("natural neutral-control corpus is empty")
    repeats = (target_words + len(words) - 1) // len(words)
    return " ".join((words * repeats)[:target_words])


def system_prompt(variant: dict, case: dict, routed_target_words: int | None = None) -> tuple[str, list[dict]]:
    if variant["framework"] == "routed":
        return read_sources(case["routed_prompt_sources"])
    if variant["framework"] == "negative_control":
        template, metadata = read_sources(variant["prompt_sources"])
        return matched_neutral_prompt(template, routed_target_words or 0), metadata
    return read_sources(variant["prompt_sources"])


def build_plan(config: dict, *, seed: int, batch_id: str, output_dir: Path, repetitions: int | None = None) -> dict:
    repetitions = repetitions or config["execution"]["minimum_repetitions"]
    if repetitions < config["execution"]["minimum_repetitions"]:
        raise ValueError("repetitions cannot be lower than the benchmark minimum")
    output_dir.mkdir(parents=True, exist_ok=True)
    commit = git_output("rev-parse", "HEAD")
    dirty = bool(git_output("status", "--porcelain"))
    variants = {item["id"]: item for item in config["variants"]}
    artifacts, runs = [], []
    source_hash = hashlib.sha256()

    for case in config["pilot_cases"]:
        user_prompt = (ROOT / case["user_prompt_path"]).read_text(encoding="utf-8-sig")
        check_spec_text = (ROOT / case["check_spec_path"]).read_text(encoding="utf-8-sig")
        fixtures = [{"path": path, "content": (ROOT / path).read_text(encoding="utf-8-sig")} for path in case["fixture_paths"]]
        routed_prompt, _ = read_sources(case["routed_prompt_sources"])
        target_words = word_count(routed_prompt)
        for variant_id, variant in variants.items():
            system, source_metadata = system_prompt(variant, case, target_words)
            artifact = {
                "pilot_case_id": case["id"], "promotion_eligible": False,
                "variant_id": variant_id, "requested_model": variant["model"],
                "instruction_prefix": system, "user_prompt": user_prompt,
                "fixtures": fixtures, "check_spec_path": case["check_spec_path"],
                "check_spec_sha256": sha256_bytes(check_spec_text.encode("utf-8")),
                "prompt_sources": source_metadata,
                "word_counter": "whitespace-v1", "instruction_prefix_word_count": word_count(system),
                "prompt_role": config["manual_execution"]["prompt_role"],
                "source_surface_required": config["manual_execution"]["surface"]
            }
            artifact_bytes = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            artifact_hash = sha256_bytes(artifact_bytes)
            relative = Path("artifacts") / f"{case['id']}-{variant_id}.json"
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(artifact_bytes)
            source_hash.update(artifact_hash.encode("ascii"))
            artifacts.append({"path": str(relative).replace("\\", "/"), "sha256": artifact_hash})
            for repetition in range(1, repetitions + 1):
                runs.append({
                    "run_id": f"{batch_id}-{case['id']}-{variant_id}-R{repetition:02d}",
                    "pilot_case_id": case["id"], "promotion_eligible": False,
                    "variant_id": variant_id, "requested_model": variant["model"],
                    "repetition": repetition, "artifact_path": str(relative).replace("\\", "/"),
                    "prompt_hash": artifact_hash, "repository_commit": commit,
                    "source_surface_required": config["manual_execution"]["surface"], "status": "planned"
                })

    random.Random(seed).shuffle(runs)
    tolerance = config["negative_control"]["maximum_word_count_difference_percent"]
    for case in config["pilot_cases"]:
        counts = {}
        for variant_id in ("O-F", "O-N", "S-F", "S-N"):
            artifact_path = output_dir / "artifacts" / f"{case['id']}-{variant_id}.json"
            counts[variant_id] = json.loads(artifact_path.read_text(encoding="utf-8"))["instruction_prefix_word_count"]
        for treatment, control in (("O-F", "O-N"), ("S-F", "S-N")):
            difference = abs(counts[treatment] - counts[control]) / max(counts[treatment], 1) * 100
            if difference > tolerance:
                raise ValueError(f"{case['id']} {control} length differs from {treatment} by {difference:.2f}%")

    return {
        "benchmark_id": config["benchmark_id"], "benchmark_version": config["version"],
        "batch_id": batch_id, "seed": seed, "repository_commit": commit,
        "working_tree_clean": not dirty,
        "config_sha256": sha256_bytes(json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        "source_tree_sha256": source_hash.hexdigest(), "repetitions": repetitions,
        "artifact_count": len(artifacts), "artifacts": artifacts,
        "run_count": len(runs), "runs": runs,
        "responses_imported": 0, "manual_smoke_ready": True, "promotion_ready": False,
        "promotion_blockers": ["private holdout fixtures not installed", "independent scored batches not completed"]
    }


def validate_plan(plan: dict, output_dir: Path) -> list[str]:
    errors = []
    schema = json.loads(PLAN_SCHEMA.read_text(encoding="utf-8"))
    if missing := set(schema["required"]) - set(plan):
        errors.append(f"plan missing fields: {sorted(missing)}")
    if plan.get("responses_imported") != 0:
        errors.append("new plan must record zero imported responses")
    if plan.get("manual_smoke_ready") is not True:
        errors.append("compiled smoke plan must be ready for manual execution")
    if plan.get("promotion_ready") is not False:
        errors.append("smoke plan must not claim promotion readiness")
    artifacts = plan.get("artifacts", [])
    if plan.get("artifact_count") != len(artifacts):
        errors.append("artifact_count does not match artifacts")
    for artifact in artifacts:
        path = output_dir / artifact.get("path", "")
        if not path.is_file():
            errors.append(f"missing compiled artifact: {artifact.get('path')}")
        elif sha256_bytes(path.read_bytes()) != artifact.get("sha256"):
            errors.append(f"compiled artifact hash mismatch: {artifact.get('path')}")
    runs = plan.get("runs", [])
    if plan.get("run_count") != len(runs):
        errors.append("run_count does not match runs")
    artifact_paths = {item.get("path") for item in artifacts}
    for run in runs:
        if run.get("artifact_path") not in artifact_paths:
            errors.append(f"run {run.get('run_id')} references unknown artifact")
    if len({run.get("run_id") for run in runs}) != len(runs):
        errors.append("duplicate run ID")
    return errors


def normalized_plan(plan: dict) -> dict:
    """Remove only Git checkout state that cannot be reproducible across clones."""
    normalized = json.loads(json.dumps(plan))
    normalized["repository_commit"] = "<normalized>"
    normalized["working_tree_clean"] = "<normalized>"
    for run in normalized.get("runs", []):
        run["repository_commit"] = "<normalized>"
    return normalized


def check_checked_in(plan_path: Path) -> list[str]:
    """Regenerate a checked-in plan and report deterministic content drift."""
    if not plan_path.is_file():
        return [f"checked-in plan missing: {plan_path}"]
    try:
        expected = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read checked-in plan: {exc}"]

    required = ("seed", "batch_id", "repetitions")
    if missing := [key for key in required if key not in expected]:
        return [f"checked-in plan missing regeneration fields: {missing}"]

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    checked_package = plan_path.parent / f"{expected['batch_id']}-package"
    with tempfile.TemporaryDirectory() as directory:
        generated_package = Path(directory) / f"{expected['batch_id']}-package"
        actual = build_plan(
            config,
            seed=expected["seed"],
            batch_id=expected["batch_id"],
            output_dir=generated_package,
            repetitions=expected["repetitions"],
        )
        errors = validate_plan(actual, generated_package)
        if normalized_plan(expected) != normalized_plan(actual):
            errors.append("checked-in plan is stale (excluding normalized Git checkout fields)")

        expected_files = {item["path"] for item in actual["artifacts"]}
        if not checked_package.is_dir():
            errors.append(f"checked-in package missing: {checked_package}")
            return errors
        checked_files = {
            path.relative_to(checked_package).as_posix()
            for path in checked_package.rglob("*") if path.is_file()
        }
        if checked_files != expected_files:
            errors.append("checked-in package file set is stale")
        for relative in sorted(checked_files & expected_files):
            if (checked_package / relative).read_bytes() != (generated_package / relative).read_bytes():
                errors.append(f"checked-in artifact is stale: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int)
    parser.add_argument("--batch-id")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="regenerate and compare the checked-in plan/package")
    args = parser.parse_args()
    if args.check:
        if args.seed is not None or args.batch_id is not None or args.repetitions is not None:
            parser.error("--check derives seed, batch ID, and repetitions from --output")
        if errors := check_checked_in(args.output):
            raise SystemExit("stale pilot output: " + "; ".join(errors))
        print(f"Pilot output check: PASS ({args.output})")
        return 0
    if args.seed is None or args.batch_id is None:
        parser.error("--seed and --batch-id are required unless --check is used")
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    output_dir = args.output.parent / f"{args.batch_id}-package"
    plan = build_plan(config, seed=args.seed, batch_id=args.batch_id, output_dir=output_dir, repetitions=args.repetitions)
    if errors := validate_plan(plan, output_dir):
        raise SystemExit("invalid generated plan: " + "; ".join(errors))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: plan[key] for key in ("benchmark_id", "batch_id", "seed", "artifact_count", "run_count", "responses_imported", "manual_smoke_ready", "promotion_ready")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
