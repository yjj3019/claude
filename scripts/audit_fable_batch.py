#!/usr/bin/env python3
"""Audit manual benchmark collection completeness without exposing responses."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = (ROOT / ".local" / "fable").resolve()
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def canonical_plan_hash(plan: dict) -> str:
    return digest(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def audit(plan_path: Path, import_dir: Path, *, allowed_root: Path = LOCAL_ROOT) -> dict:
    errors, warnings = [], []
    allowed_root, plan_path, import_dir = allowed_root.resolve(), plan_path.resolve(), import_dir.resolve()
    if not contained(plan_path, allowed_root) or not contained(import_dir, allowed_root):
        return {"valid": False, "collection_complete": False, "scoring_ready": False,
                "errors": ["plan and imports must stay inside the local benchmark root"], "warnings": []}
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "collection_complete": False, "scoring_ready": False,
                "errors": [f"plan unreadable: {exc}"], "warnings": []}
    planned = {}
    for index, run in enumerate(plan.get("runs", [])):
        run_id = run.get("run_id") if isinstance(run, dict) else None
        if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id) or run_id in planned:
            errors.append(f"invalid or duplicate planned run at index {index}")
        else:
            planned[run_id] = run
    if len(planned) != plan.get("run_count"):
        errors.append("plan run_count does not match unique planned runs")
    expected_plan_hash = canonical_plan_hash(plan)
    observed, statuses, variants = {}, Counter(), defaultdict(Counter)
    if import_dir.is_dir():
        metadata_files = sorted(path for path in import_dir.glob("*.json") if not path.name.endswith(".evidence.json"))
    else:
        metadata_files = []
    for metadata_path in metadata_files:
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"unreadable result metadata {metadata_path.name}: {exc}")
            continue
        run_id = metadata.get("run_id")
        if run_id not in planned:
            errors.append(f"unplanned result: {run_id}")
            continue
        if run_id in observed:
            errors.append(f"duplicate result: {run_id}")
            continue
        observed[run_id] = metadata
        run = planned[run_id]
        for field in ("scenario_id", "variant_id", "requested_model", "prompt_hash", "repository_commit"):
            expected = run.get(field, run.get("pilot_case_id") if field == "scenario_id" else None)
            if metadata.get(field) != expected:
                errors.append(f"{run_id} metadata mismatch: {field}")
        if metadata.get("plan_sha256") != expected_plan_hash:
            errors.append(f"{run_id} plan hash mismatch")
        status = metadata.get("status")
        if status not in {"imported", "scored", "excluded"}:
            errors.append(f"{run_id} has invalid status")
            continue
        if status == "excluded" and not metadata.get("exclusion_reason"):
            errors.append(f"{run_id} excluded without reason")
        if status != "excluded" and metadata.get("exclusion_reason") is not None:
            errors.append(f"{run_id} has an unexpected exclusion reason")
        response_name = metadata.get("response_path")
        response_path = (import_dir / response_name).resolve() if isinstance(response_name, str) else import_dir
        if response_path.parent != import_dir or not response_path.is_file() or digest(response_path.read_bytes()) != metadata.get("response_sha256"):
            errors.append(f"{run_id} response binding failed")
        evidence_status = metadata.get("evidence_status")
        evidence_name, evidence_hash = metadata.get("evidence_path"), metadata.get("evidence_sha256")
        if evidence_status == "verified" and isinstance(evidence_name, str) and isinstance(evidence_hash, str):
            evidence_path = (import_dir / evidence_name).resolve()
            if evidence_path.parent != import_dir or not evidence_path.is_file() or digest(evidence_path.read_bytes()) != evidence_hash:
                errors.append(f"{run_id} model evidence binding failed")
        elif evidence_status == "unavailable" and evidence_name is None and evidence_hash is None:
            pass
        else:
            errors.append(f"{run_id} has inconsistent model evidence metadata")
        statuses[status] += 1
        variants[run["variant_id"]][status] += 1
    missing = sorted(set(planned) - set(observed))
    if missing:
        warnings.append(f"missing planned runs: {len(missing)}")
    conservative_failures = len(missing) + statuses["excluded"]
    total = len(planned)
    collection_complete = not errors and not missing
    return {
        "valid": not errors, "collection_complete": collection_complete,
        "scoring_ready": collection_complete, "benchmark_promotion_ready": False,
        "batch_id": plan.get("batch_id"), "plan_sha256": expected_plan_hash,
        "planned_runs": total, "observed_results": len(observed), "missing_runs": len(missing),
        "missing_run_ids": missing, "status_counts": dict(statuses),
        "variant_status_counts": {key: dict(value) for key, value in sorted(variants.items())},
        "conservative_failure_bound": {
            "count": conservative_failures,
            "rate": conservative_failures / total if total else 1.0,
            "rule": "missing_and_excluded_count_as_failure",
        },
        "errors": errors, "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--import-dir", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.plan, args.import_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
