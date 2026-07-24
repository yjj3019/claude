#!/usr/bin/env python3
"""Bind private holdout, leakage evidence, and plan before manual execution."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from scripts.check_fable_leakage import analyze, load_texts
    from scripts.validate_fable_holdout import LOCAL_HOLDOUT, contained, validate as validate_holdout
    from scripts.validate_fable_provenance import validate as validate_provenance
    from scripts.validate_fable_semantic_evidence import validate as validate_semantic
except ModuleNotFoundError:
    from check_fable_leakage import analyze, load_texts
    from validate_fable_holdout import LOCAL_HOLDOUT, contained, validate as validate_holdout
    from validate_fable_provenance import validate as validate_provenance
    from validate_fable_semantic_evidence import validate as validate_semantic


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_artifacts(manifest_path: Path, manifest: dict) -> dict[str, Path]:
    artifacts = {}
    for entry in manifest["entries"]:
        specs = [entry["user_prompt"], entry["check_spec"], *entry["fixture_files"]]
        for spec in specs:
            path = (manifest_path.parent / spec["path"]).resolve()
            artifacts[spec["sha256"]] = path
    return artifacts


def validate_preflight(manifest_path: Path, lexical_path: Path, semantic_path: Path, provenance_path: Path,
                       plan_path: Path, canary_path: Path) -> dict:
    errors, checks = [], {}
    manifest_path, lexical_path, semantic_path, plan_path, canary_path = map(Path.resolve, (manifest_path, lexical_path, semantic_path, plan_path, canary_path))
    if not all(contained(path, LOCAL_HOLDOUT) for path in (manifest_path, plan_path, canary_path)):
        errors.append("manifest, plan, and canary file must stay under .local/fable/holdout")
    holdout = validate_holdout(manifest_path)
    checks["holdout_intake"] = holdout
    if not holdout.get("valid") or not holdout.get("intake_gate_ready"):
        errors.append("holdout intake gate is not ready")
    provenance = validate_provenance(provenance_path, manifest_path)
    checks["provenance"] = provenance
    if not provenance.get("valid") or not provenance.get("provenance_evidence_complete"):
        errors.append("holdout provenance evidence is incomplete")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        expected = manifest_artifacts(manifest_path, manifest)
        canaries = [line.strip() for line in canary_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        expected_canary_hashes = {entry["canary_sha256"] for entry in manifest["entries"]}
        actual_canary_hashes = {hashlib.sha256(item.encode("utf-8")).hexdigest() for item in canaries}
        if actual_canary_hashes != expected_canary_hashes:
            errors.append("local canary values do not exactly match manifest canary hashes")
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"manifest cannot be bound: {exc}")
        expected = {}
    try:
        lexical = json.loads(lexical_path.read_text(encoding="utf-8-sig"))
        lexical_candidates = {item["sha256"]: Path(item["path"]).resolve() for item in lexical["candidates"]}
        lexical_references = {item["sha256"]: Path(item["path"]).resolve() for item in lexical["references"]}
        if set(lexical_candidates) != set(expected):
            errors.append("lexical evidence candidates do not exactly match holdout artifacts")
        if any(not path.is_file() or sha256(path) != digest for digest, path in {**lexical_candidates, **lexical_references}.items()):
            errors.append("lexical evidence path or hash binding is invalid")
        recomputed = analyze(
            load_texts(list(lexical_candidates.values())), load_texts(list(lexical_references.values())),
            ngram_size=lexical["ngram_size"], ceiling=lexical["minhash_similarity_ceiling"], canaries=canaries,
        )
        if set(lexical.get("canary_sha256s", [])) != actual_canary_hashes:
            errors.append("lexical evidence is not bound to the current canary set")
        if not lexical.get("valid") or not recomputed["valid"]:
            errors.append("lexical leakage checks did not pass")
        checks["lexical_leakage"] = {"valid": recomputed["valid"], "candidate_count": len(lexical_candidates),
                                      "reference_count": len(lexical_references)}
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"lexical evidence cannot be validated: {exc}")
        lexical_candidates, lexical_references = {}, {}
    semantic = validate_semantic(semantic_path)
    checks["semantic_leakage"] = semantic
    if not semantic.get("valid") or not semantic.get("semantic_similarity_complete"):
        errors.append("semantic leakage evidence is incomplete")
    try:
        semantic_data = json.loads(semantic_path.read_text(encoding="utf-8-sig"))
        semantic_candidates = {item["sha256"] for item in semantic_data["candidates"]}
        semantic_references = {item["sha256"] for item in semantic_data["references"]}
        if semantic_candidates != set(expected):
            errors.append("semantic evidence candidates do not exactly match holdout artifacts")
        if semantic_references != set(lexical_references):
            errors.append("semantic and lexical evidence use different reference corpora")
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"semantic evidence cannot be bound: {exc}")
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
        if plan.get("manifest_sha256") != sha256(manifest_path):
            errors.append("plan is not bound to the current holdout manifest")
        if plan.get("intake_gate_ready") is not True or plan.get("benchmark_promotion_ready") is not False:
            errors.append("plan readiness flags are invalid")
        artifacts = plan.get("artifacts", [])
        for artifact in artifacts:
            path = (plan_path.parent / artifact["path"]).resolve()
            if not contained(path, LOCAL_HOLDOUT) or not path.is_file() or sha256(path) != artifact["sha256"]:
                errors.append(f"plan artifact binding failed: {artifact.get('artifact_id')}")
                break
        if len(artifacts) != plan.get("artifact_count") or len(plan.get("runs", [])) != plan.get("run_count"):
            errors.append("plan counts do not match its contents")
        checks["execution_plan"] = {"artifact_count": len(artifacts), "run_count": len(plan.get("runs", []))}
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"execution plan cannot be validated: {exc}")
    return {"valid": not errors, "execution_ready": not errors, "benchmark_promotion_ready": False,
            "checks": checks, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--lexical-evidence", required=True, type=Path)
    parser.add_argument("--semantic-evidence", required=True, type=Path)
    parser.add_argument("--provenance-evidence", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--canary-file", required=True, type=Path)
    args = parser.parse_args()
    result = validate_preflight(args.manifest, args.lexical_evidence, args.semantic_evidence,
                                args.provenance_evidence, args.plan, args.canary_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
