#!/usr/bin/env python3
"""Combine validated Fable evidence into a conservative promotion verdict."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _load(path: Path) -> tuple[dict, dict]:
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value, {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}


def evaluate(analysis_path: Path, reliability_path: Path, preflight_path: Path,
             audit_paths: list[Path]) -> dict:
    if len(audit_paths) < 2:
        raise ValueError("at least two batch audits are required")
    analysis, analysis_source = _load(analysis_path)
    reliability, reliability_source = _load(reliability_path)
    preflight, preflight_source = _load(preflight_path)
    audits, audit_sources = zip(*(_load(path) for path in audit_paths))
    batch_ids = [audit.get("batch_id") for audit in audits]
    errors = []
    if len(set(batch_ids)) != len(batch_ids) or any(not isinstance(item, str) or not item for item in batch_ids):
        errors.append("batch audits must identify distinct non-empty batch_id values")
    failed = []
    checks = {
        "quality": analysis.get("valid") is True and analysis.get("quality_gate_pass") is True,
        "reliability": reliability.get("reliability_gate_pass") is True,
        "private_preflight": preflight.get("valid") is True and preflight.get("execution_ready") is True,
        "batch_collection": all(audit.get("valid") is True and audit.get("collection_complete") is True
                                and audit.get("scoring_ready") is True for audit in audits),
        "placebo": analysis.get("placebo_gate_pass") is True,
    }
    failed.extend(name for name, passed in checks.items() if not passed and name != "placebo")
    verdict = "NO_GO" if errors or failed else "GO" if checks["placebo"] else "CONDITIONAL_GO"
    blockers = [*errors, *(f"{name}_gate_failed" for name in failed)]
    if verdict == "CONDITIONAL_GO":
        blockers.append("placebo_gate_not_passed")
    return {
        "schema_version": "1.0", "valid": not errors, "verdict": verdict,
        "benchmark_promotion_ready": verdict == "GO", "checks": checks,
        "blockers": blockers, "batch_ids": batch_ids,
        "sources": {
            "analysis": analysis_source, "reliability": reliability_source,
            "preflight": preflight_source, "batch_audits": list(audit_sources),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis", required=True, type=Path)
    parser.add_argument("--reliability", required=True, type=Path)
    parser.add_argument("--preflight", required=True, type=Path)
    parser.add_argument("--batch-audit", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = evaluate(args.analysis, args.reliability, args.preflight, args.batch_audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["verdict"] != "NO_GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
