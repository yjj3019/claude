#!/usr/bin/env python3
"""Validate hash-bound semantic-similarity evidence produced by a local tool."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = (ROOT / ".local" / "fable").resolve()
LEAKAGE_ROOT = (LOCAL_ROOT / "leakage").resolve()
BENCHMARK_CONFIG = ROOT / "config" / "fable-benchmark.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_bound_file(spec: object, *, label: str, errors: list[str]) -> tuple[str, Path] | None:
    if not isinstance(spec, dict):
        errors.append(f"{label} must be an object")
        return None
    relative, expected = spec.get("path"), spec.get("sha256")
    if not isinstance(relative, str) or not isinstance(expected, str) or not SHA256.fullmatch(expected):
        errors.append(f"{label} requires path and lowercase SHA-256")
        return None
    path = (ROOT / relative).resolve()
    if not (contained(path, ROOT) or contained(path, LOCAL_ROOT)) or not path.is_file():
        errors.append(f"{label} path is missing or outside allowed roots")
        return None
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(f"{label} hash mismatch")
    return expected, path


def validate(evidence_path: Path) -> dict:
    errors, warnings = [], []
    evidence_path = evidence_path.resolve()
    if not contained(evidence_path, LEAKAGE_ROOT):
        return {"valid": False, "semantic_similarity_complete": False, "promotion_ready": False,
                "errors": ["evidence must stay under .local/fable/leakage"], "warnings": []}
    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "semantic_similarity_complete": False, "promotion_ready": False,
                "errors": [f"evidence unreadable: {exc}"], "warnings": []}
    if data.get("evidence_version") != "1.0":
        errors.append("evidence_version must be 1.0")
    try:
        datetime.fromisoformat(data.get("generated_at", "").replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append("generated_at must be an ISO-8601 timestamp")
    tool = data.get("tool")
    if not isinstance(tool, dict) or tool.get("offline") is not True:
        errors.append("tool metadata must declare offline=true")
    elif any(not isinstance(tool.get(field), str) or not tool[field].strip() for field in ("name", "version", "model")):
        errors.append("tool name, version, and model revision are required")
    threshold = data.get("threshold")
    if not isinstance(threshold, (int, float)) or isinstance(threshold, bool) or not 0 <= threshold <= 1:
        errors.append("threshold must be between 0 and 1")
        threshold = 0
    configured_threshold = json.loads(BENCHMARK_CONFIG.read_text(encoding="utf-8-sig"))["leakage_checks"]["semantic_similarity_ceiling"]
    if threshold != configured_threshold:
        errors.append(f"threshold must equal configured ceiling {configured_threshold}")
    candidates, references = data.get("candidates"), data.get("references")
    if not isinstance(candidates, list) or not candidates or not isinstance(references, list) or not references:
        errors.append("non-empty candidates and references are required")
        candidates, references = [], []
    candidate_hashes = [item[0] for index, spec in enumerate(candidates)
                        if (item := resolve_bound_file(spec, label=f"candidates[{index}]", errors=errors))]
    reference_hashes = [item[0] for index, spec in enumerate(references)
                        if (item := resolve_bound_file(spec, label=f"references[{index}]", errors=errors))]
    if len(set(candidate_hashes)) != len(candidate_hashes) or len(set(reference_hashes)) != len(reference_hashes):
        errors.append("candidate and reference hashes must be unique within each corpus")
    if set(candidate_hashes) & set(reference_hashes):
        errors.append("candidate and reference corpora contain an identical file hash")
    expected_pairs = {(candidate, reference) for candidate in candidate_hashes for reference in reference_hashes}
    observed, maximum = set(), 0.0
    pairs = data.get("pairs")
    if not isinstance(pairs, list):
        errors.append("pairs must be an array")
        pairs = []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            errors.append(f"pairs[{index}] must be an object")
            continue
        key = (pair.get("candidate_sha256"), pair.get("reference_sha256"))
        similarity = pair.get("similarity")
        if key not in expected_pairs:
            errors.append(f"pairs[{index}] is not bound to the declared corpora")
        if key in observed:
            errors.append(f"pairs[{index}] duplicates a corpus pair")
        observed.add(key)
        if not isinstance(similarity, (int, float)) or isinstance(similarity, bool) or not 0 <= similarity <= 1:
            errors.append(f"pairs[{index}].similarity must be between 0 and 1")
        else:
            maximum = max(maximum, float(similarity))
    if observed != expected_pairs:
        errors.append(f"pair matrix is incomplete: expected {len(expected_pairs)}, observed {len(observed & expected_pairs)}")
    if maximum > threshold:
        errors.append(f"maximum similarity {maximum:.6f} exceeds threshold {threshold:.6f}")
    complete = not errors and bool(expected_pairs)
    return {
        "valid": not errors, "semantic_similarity_complete": complete, "promotion_ready": False,
        "candidate_count": len(candidate_hashes), "reference_count": len(reference_hashes),
        "pair_count": len(pairs), "maximum_similarity": maximum, "threshold": threshold,
        "errors": errors, "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.evidence)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
