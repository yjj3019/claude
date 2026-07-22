#!/usr/bin/env python3
"""Validate a local-only private holdout manifest without exposing its content."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

try:
    from scripts.score_fable_smoke import validate_checks
except ModuleNotFoundError:
    from score_fable_smoke import validate_checks

ROOT = Path(__file__).resolve().parents[1]
LOCAL_HOLDOUT = (ROOT / ".local" / "fable" / "holdout").resolve()
ROUTES_CONFIG = ROOT / "config" / "routes.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:sk-ant-|sk-proj-|ghp_)[A-Za-z0-9_-]{12,}"),
]


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_artifact(spec: object, *, label: str, manifest_dir: Path, errors: list[str], require_json_object: bool = False) -> None:
    if not isinstance(spec, dict):
        errors.append(f"{label} must contain path and sha256")
        return
    relative, expected = spec.get("path"), spec.get("sha256")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        errors.append(f"{label}.sha256 must be lowercase SHA-256")
    if not isinstance(relative, str) or Path(relative).is_absolute():
        errors.append(f"{label}.path must be relative")
        return
    path = (manifest_dir / relative).resolve()
    if not contained(path, LOCAL_HOLDOUT):
        errors.append(f"{label}.path escapes local holdout root")
        return
    allowed = {".json"} if require_json_object else {".md", ".txt", ".json"}
    if path.suffix.lower() not in allowed or not path.is_file():
        errors.append(f"{label}.path must reference an existing allowed UTF-8 file")
        return
    raw = path.read_bytes()
    if len(raw) > 1_000_000:
        errors.append(f"{label} exceeds 1 MB")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        errors.append(f"{label} is not UTF-8")
        text = ""
    if any(pattern.search(raw) for pattern in SECRET_PATTERNS):
        errors.append(f"{label} contains a possible credential")
    if isinstance(expected, str) and SHA256.fullmatch(expected) and hashlib.sha256(raw).hexdigest() != expected:
        errors.append(f"{label} hash mismatch")
    if require_json_object and text:
        try:
            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                errors.append(f"{label} must be a JSON object")
            else:
                try:
                    validate_checks(parsed)
                except ValueError as exc:
                    errors.append(f"{label} is not an allowed declarative check spec: {exc}")
        except json.JSONDecodeError:
            errors.append(f"{label} is invalid JSON")


def validate(manifest_path: Path, minimum_per_suite: int = 5) -> dict:
    errors, warnings = [], []
    resolved_manifest = manifest_path.resolve()
    if not contained(resolved_manifest, LOCAL_HOLDOUT):
        return {"valid": False, "intake_gate_ready": False, "errors": ["manifest must be under .local/fable/holdout"], "warnings": []}
    try:
        data = json.loads(resolved_manifest.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "intake_gate_ready": False, "errors": [f"manifest unreadable: {exc}"], "warnings": []}
    entries = data.get("entries")
    if data.get("manifest_version") != "1.1" or not isinstance(entries, list) or not entries:
        errors.append("manifest_version 1.1 and a non-empty entries array are required")
        entries = entries if isinstance(entries, list) else []
    for field in ("dataset_id", "custodian_id"):
        if not isinstance(data.get(field), str) or not SAFE_ID.fullmatch(data[field]):
            errors.append(f"{field} is required and must be a safe opaque ID")
    if not isinstance(data.get("created_at"), str) or not DATE.fullmatch(data["created_at"]):
        errors.append("created_at must use YYYY-MM-DD")
    seen, suites = set(), Counter()
    route_ids = {route["id"] for route in json.loads(ROUTES_CONFIG.read_text(encoding="utf-8-sig"))["routes"]}
    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        scenario_id = entry.get("scenario_id")
        if not isinstance(scenario_id, str) or not SAFE_ID.fullmatch(scenario_id):
            errors.append(f"{label}.scenario_id is unsafe")
        elif scenario_id in seen:
            errors.append(f"duplicate scenario_id: {scenario_id}")
        else:
            seen.add(scenario_id)
        suite = entry.get("suite")
        if not isinstance(suite, str) or not SAFE_ID.fullmatch(suite):
            errors.append(f"{label}.suite is unsafe")
        else:
            suites[suite] += 1
        if entry.get("route_id") not in route_ids:
            errors.append(f"{label}.route_id is not defined in config/routes.json")
        if entry.get("provenance") != "private_holdout" or entry.get("independently_authored") is not True or entry.get("exposed_to_distillation") is not False:
            errors.append(f"{label} lacks private, independent, unexposed provenance")
        canary_hash = entry.get("canary_sha256")
        if canary_hash is not None and (not isinstance(canary_hash, str) or not SHA256.fullmatch(canary_hash)):
            errors.append(f"{label}.canary_sha256 must be null or lowercase SHA-256")
        validate_artifact(entry.get("user_prompt"), label=f"{label}.user_prompt", manifest_dir=resolved_manifest.parent, errors=errors)
        validate_artifact(entry.get("check_spec"), label=f"{label}.check_spec", manifest_dir=resolved_manifest.parent, errors=errors, require_json_object=True)
        fixture_files = entry.get("fixture_files")
        if not isinstance(fixture_files, list):
            errors.append(f"{label}.fixture_files must be an array (empty is allowed)")
        else:
            for fixture_index, fixture_spec in enumerate(fixture_files):
                validate_artifact(fixture_spec, label=f"{label}.fixture_files[{fixture_index}]", manifest_dir=resolved_manifest.parent, errors=errors)
    underfilled = {suite: count for suite, count in suites.items() if count < minimum_per_suite}
    if underfilled:
        warnings.append(f"suites below {minimum_per_suite} independent scenarios: {underfilled}")
    missing_canaries = sum(1 for entry in entries if isinstance(entry, dict) and entry.get("canary_sha256") is None)
    if missing_canaries:
        warnings.append(f"entries without canary hash: {missing_canaries}")
    return {
        "valid": not errors, "intake_gate_ready": not errors and bool(suites) and not underfilled and not missing_canaries,
        "benchmark_promotion_ready": False,
        "entry_count": len(entries), "suite_counts": dict(sorted(suites.items())),
        "errors": errors, "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--minimum-per-suite", type=int, default=5)
    args = parser.parse_args()
    if args.minimum_per_suite < 1:
        parser.error("minimum per suite must be positive")
    result = validate(args.manifest, args.minimum_per_suite)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
