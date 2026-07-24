#!/usr/bin/env python3
"""Validate a local attestation bound to a private holdout manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

try:
    from scripts.validate_fable_holdout import LOCAL_HOLDOUT, SAFE_ID, contained
except ModuleNotFoundError:
    from validate_fable_holdout import LOCAL_HOLDOUT, SAFE_ID, contained

SHA256 = re.compile(r"^[0-9a-f]{64}$")


def validate(evidence_path: Path, manifest_path: Path) -> dict:
    errors = []
    evidence_path, manifest_path = evidence_path.resolve(), manifest_path.resolve()
    if not contained(evidence_path, LOCAL_HOLDOUT) or not contained(manifest_path, LOCAL_HOLDOUT):
        return {"valid": False, "provenance_evidence_complete": False,
                "errors": ["evidence and manifest must stay under .local/fable/holdout"]}
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
        manifest_raw = manifest_path.read_bytes()
        manifest = json.loads(manifest_raw.decode("utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "provenance_evidence_complete": False, "errors": [f"unreadable evidence: {exc}"]}
    if evidence.get("evidence_version") != "1.0":
        errors.append("evidence_version must be 1.0")
    if evidence.get("manifest_sha256") != hashlib.sha256(manifest_raw).hexdigest():
        errors.append("manifest hash mismatch")
    for field in ("dataset_id", "custodian_id"):
        if evidence.get(field) != manifest.get(field):
            errors.append(f"{field} does not match manifest")
    if evidence.get("authoring_method") not in {"human", "non_target_model"}:
        errors.append("authoring_method must be human or non_target_model")
    if evidence.get("target_model_involved") is not False:
        errors.append("target_model_involved must be false")
    if evidence.get("distillation_material_access") is not False:
        errors.append("distillation_material_access must be false")
    if not isinstance(evidence.get("attestor_id"), str) or not SAFE_ID.fullmatch(evidence["attestor_id"]):
        errors.append("attestor_id must be a safe opaque ID")
    try:
        datetime.fromisoformat(evidence.get("attested_at", "").replace("Z", "+00:00"))
    except (TypeError, ValueError):
        errors.append("attested_at must be an ISO-8601 timestamp")
    return {"valid": not errors, "provenance_evidence_complete": not errors,
            "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(), "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    result = validate(args.evidence, args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
