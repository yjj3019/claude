#!/usr/bin/env python3
"""Compile a local-only, blinded-execution package from a validated holdout manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

try:
    from scripts.prepare_fable_pilot import CONFIG, git_output, matched_neutral_prompt, read_sources, word_count
    from scripts.validate_fable_holdout import LOCAL_HOLDOUT, contained, validate
except ModuleNotFoundError:  # Direct script execution places scripts/ on sys.path.
    from prepare_fable_pilot import CONFIG, git_output, matched_neutral_prompt, read_sources, word_count
    from validate_fable_holdout import LOCAL_HOLDOUT, contained, validate


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_spec(manifest_dir: Path, spec: dict) -> tuple[Path, bytes]:
    path = (manifest_dir / spec["path"]).resolve()
    return path, path.read_bytes()


def routed_sources(route: dict) -> list[str]:
    paths = ["CLAUDE.md", "docs/loading-map.md", *route.get("policies", [])]
    for key in ("module", "workflow", "reviewer"):
        if route.get(key):
            paths.append(route[key])
    return list(dict.fromkeys(paths))


def compile_plan(manifest_path: Path, output: Path, *, seed: int, batch_id: str, repetitions: int | None = None) -> dict:
    manifest_path, output = manifest_path.resolve(), output.resolve()
    if not contained(output, LOCAL_HOLDOUT):
        raise ValueError("output must stay under .local/fable/holdout")
    if output.exists():
        raise FileExistsError(f"refusing to overwrite existing plan: {output}")
    validation = validate(manifest_path)
    if not validation["valid"] or not validation["intake_gate_ready"]:
        raise ValueError(f"holdout intake gate is not ready: {validation['errors'] + validation['warnings']}")
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8-sig"))
    config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
    repetitions = repetitions or config["execution"]["minimum_repetitions"]
    if repetitions < config["execution"]["minimum_repetitions"]:
        raise ValueError("repetitions cannot be lower than the benchmark minimum")
    if not batch_id or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for character in batch_id):
        raise ValueError("batch_id is unsafe")
    variants = config["variants"]
    repository_commit = git_output("rev-parse", "HEAD")
    routes = {item["id"]: item for item in json.loads((CONFIG.parent / "routes.json").read_text(encoding="utf-8-sig"))["routes"]}
    package = output.with_name(f"{output.stem}-package")
    artifacts_dir = package / "artifacts"
    if package.exists():
        raise FileExistsError(f"refusing to overwrite existing package: {package}")
    artifacts_dir.mkdir(parents=True)
    artifacts, runs = [], []
    for entry in manifest["entries"]:
        prompt_path, prompt_raw = read_spec(manifest_path.parent, entry["user_prompt"])
        prompt = prompt_raw.decode("utf-8-sig")
        fixtures = []
        for spec in entry["fixture_files"]:
            fixture_path, fixture_raw = read_spec(manifest_path.parent, spec)
            fixtures.append({"name": fixture_path.name, "sha256": sha256(fixture_raw), "content": fixture_raw.decode("utf-8-sig")})
        _, checks_raw = read_spec(manifest_path.parent, entry["check_spec"])
        routed_prefix, routed_metadata = read_sources(routed_sources(routes[entry["route_id"]]))
        routed_words = word_count(routed_prefix)
        for variant in variants:
            if variant["framework"] == "routed":
                instruction_prefix, sources = routed_prefix, routed_metadata
            elif variant["framework"] == "negative_control":
                neutral, sources = read_sources(variant["prompt_sources"])
                instruction_prefix = matched_neutral_prompt(neutral, routed_words)
            else:
                instruction_prefix, sources = read_sources(variant["prompt_sources"])
            artifact_id = f"{entry['scenario_id']}-{variant['id']}"
            artifact = {
                "artifact_id": artifact_id, "scenario_id": entry["scenario_id"], "suite": entry["suite"],
                "provenance": entry["provenance"],
                "variant_id": variant["id"], "requested_model": variant["model"],
                "instruction_prefix": instruction_prefix, "user_prompt": prompt, "fixtures": fixtures,
                "source_metadata": sources, "evaluator_check_sha256": sha256(checks_raw),
            }
            artifact_raw = (json.dumps(artifact, ensure_ascii=False, indent=2) + "\n").encode()
            artifact_path = artifacts_dir / f"{artifact_id}.json"
            artifact_path.write_bytes(artifact_raw)
            artifact_relative = str(artifact_path.relative_to(package))
            artifact_hash = sha256(artifact_raw)
            artifacts.append({"artifact_id": artifact_id, "path": str(artifact_path.relative_to(output.parent)), "sha256": artifact_hash})
            for repetition in range(1, repetitions + 1):
                runs.append({
                    "run_id": f"{batch_id}-{artifact_id}-R{repetition:02d}", "artifact_id": artifact_id,
                    "scenario_id": entry["scenario_id"], "variant_id": variant["id"],
                    "provenance": entry["provenance"],
                    "requested_model": variant["model"], "artifact_path": artifact_relative,
                    "prompt_hash": artifact_hash, "repository_commit": repository_commit,
                    "source_surface_required": "claude_app",
                })
    random.Random(seed).shuffle(runs)
    plan = {
        "benchmark_id": config["benchmark_id"], "dataset_id": manifest["dataset_id"], "batch_id": batch_id,
        "seed": seed, "manifest_sha256": sha256(manifest_raw), "repository_commit": repository_commit,
        "artifact_count": len(artifacts),
        "run_count": len(runs), "repetitions": repetitions, "artifacts": artifacts, "runs": runs,
        "surface": "claude_app", "manual_execution_only": True, "responses_imported": 0,
        "intake_gate_ready": True, "benchmark_promotion_ready": False,
        "evaluator_assets_in_execution_package": False,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--seed", type=int, default=3019)
    parser.add_argument("--batch-id", default="PRIVATE-A")
    parser.add_argument("--repetitions", type=int)
    args = parser.parse_args()
    result = compile_plan(args.manifest, args.output, seed=args.seed, batch_id=args.batch_id, repetitions=args.repetitions)
    print(json.dumps({key: result[key] for key in ("batch_id", "artifact_count", "run_count", "intake_gate_ready", "benchmark_promotion_ready")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
