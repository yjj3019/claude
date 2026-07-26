#!/usr/bin/env python3
"""Safely import a sanitized, manually captured Claude response."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL_ROOT = ROOT / ".local" / "fable"
RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
MAX_RESPONSE_BYTES = 1_000_000
MAX_EVIDENCE_BYTES = 100_000
SENSITIVE_PATTERNS = [
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(rb"(?i)\b(?:api[_ -]?key|access[_ -]?token|secret)\s*[:=]\s*\S+"),
    re.compile(rb"(?i)\bauthorization:\s*bearer\s+\S+"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_optional_bool(value: str) -> bool | None:
    return {"yes": True, "no": False, "unknown": None}[value]


def contained_file(directory: Path, filename: str) -> Path:
    directory = directory.resolve()
    target = (directory / filename).resolve()
    if target.parent != directory:
        raise ValueError("output path escapes the allowed directory")
    return target


def validate_response_bytes(data: bytes, *, sanitized_confirmed: bool) -> None:
    if not sanitized_confirmed:
        raise ValueError("sanitized response confirmation is required")
    if not data.strip():
        raise ValueError("response file is empty")
    if len(data) > MAX_RESPONSE_BYTES:
        raise ValueError("response file exceeds the 1 MB limit")
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("response must be UTF-8 text") from exc
    if any(pattern.search(data) for pattern in SENSITIVE_PATTERNS):
        raise ValueError("response contains a possible secret and was not imported")


def validate_evidence_bytes(data: bytes, *, suffix: str, sanitized_confirmed: bool) -> None:
    if not sanitized_confirmed:
        raise ValueError("sanitized evidence confirmation is required")
    if not data.strip():
        raise ValueError("surface evidence file is empty")
    if len(data) > MAX_EVIDENCE_BYTES:
        raise ValueError("surface evidence file exceeds the 100 KB limit")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("surface evidence must be UTF-8 text or metadata JSON") from exc
    if any(pattern.search(data) for pattern in SENSITIVE_PATTERNS):
        raise ValueError("surface evidence contains a possible secret and was not imported")
    if suffix == ".json":
        try:
            metadata = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("surface evidence metadata must be valid JSON") from exc
        if not isinstance(metadata, dict):
            raise ValueError("surface evidence metadata must be a JSON object")
    elif suffix not in {".txt", ".md"}:
        raise ValueError("surface evidence must use .txt, .md, or .json")


def validate_plan_binding(plan: dict, *, run_id: str, package_dir: Path) -> dict:
    if not RUN_ID_RE.fullmatch(run_id):
        raise ValueError("unsafe run_id")
    matches = [run for run in plan.get("runs", []) if isinstance(run, dict) and run.get("run_id") == run_id]
    if len(matches) != 1:
        raise ValueError(f"run_id must match exactly one planned run: {run_id}")
    run = matches[0]
    artifact_relative = run.get("artifact_path")
    if not isinstance(artifact_relative, str):
        raise ValueError("planned run has no artifact path")
    package_root = package_dir.resolve()
    artifact_path = (package_root / artifact_relative).resolve()
    if not artifact_path.is_relative_to(package_root) or not artifact_path.is_file():
        raise ValueError("planned artifact is missing or outside the package")
    artifact_hash = sha256_bytes(artifact_path.read_bytes())
    if artifact_hash != run.get("prompt_hash") or not SHA256_RE.fullmatch(artifact_hash):
        raise ValueError("planned artifact hash mismatch")
    if run.get("repository_commit") != plan.get("repository_commit"):
        raise ValueError("run and plan repository commits do not match")
    return run


def model_exclusion(run: dict, served_model: str | None, fallback_detected: bool | None,
                    evidence_status: str) -> str | None:
    requested = run["requested_model"]
    if served_model != requested:
        return "served model is missing or does not match the planned model"
    if run["variant_id"] == "F5" and fallback_detected is not False:
        return "Fable fallback state is not verified as false"
    if run["variant_id"] == "F5" and evidence_status != "verified":
        return "Fable model and fallback evidence is not verified"
    if fallback_detected is True:
        return "fallback was detected"
    return None


def import_response(plan: dict, *, run_id: str, response_file: Path, package_dir: Path,
                    output_dir: Path, served_model: str | None,
                    fallback_detected: bool | None, source_surface: str,
                    sanitized_confirmed: bool, evidence_file: Path | None = None,
                    evidence_sanitized_confirmed: bool = False,
                    allowed_root: Path = LOCAL_ROOT) -> dict:
    allowed_root = allowed_root.resolve()
    output_dir = output_dir.resolve()
    if not output_dir.is_relative_to(allowed_root):
        raise ValueError("output directory must stay inside the local-only benchmark root")
    run = validate_plan_binding(plan, run_id=run_id, package_dir=package_dir)
    if source_surface != run.get("source_surface_required"):
        raise ValueError("response surface does not match the planned surface")
    response_bytes = response_file.read_bytes()
    validate_response_bytes(response_bytes, sanitized_confirmed=sanitized_confirmed)
    evidence_bytes = None
    evidence_suffix = None
    if evidence_file is not None:
        evidence_suffix = evidence_file.suffix.lower()
        evidence_bytes = evidence_file.read_bytes()
        validate_evidence_bytes(
            evidence_bytes, suffix=evidence_suffix,
            sanitized_confirmed=evidence_sanitized_confirmed
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    stored_response = contained_file(output_dir, f"{run_id}.md")
    result_path = contained_file(output_dir, f"{run_id}.json")
    stored_evidence = (
        contained_file(output_dir, f"{run_id}.evidence{evidence_suffix}")
        if evidence_bytes is not None else None
    )
    if stored_response.exists() or result_path.exists() or (stored_evidence and stored_evidence.exists()):
        raise FileExistsError("an import already exists for this run_id")
    evidence_status = "verified" if evidence_bytes is not None else "unavailable"
    exclusion_reason = model_exclusion(run, served_model, fallback_detected, evidence_status)
    status = "excluded" if exclusion_reason else "imported"
    plan_hash = sha256_bytes(json.dumps(plan, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    result = {
        "run_id": run_id, "scenario_id": run.get("scenario_id", run.get("pilot_case_id")),
        "provenance": run.get("provenance"),
        "variant_id": run["variant_id"], "requested_model": run["requested_model"],
        "served_model": served_model, "fallback_detected": fallback_detected,
        "prompt_hash": run["prompt_hash"], "plan_sha256": plan_hash,
        "repository_commit": run["repository_commit"],
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "response_path": stored_response.name, "response_sha256": sha256_bytes(response_bytes),
        "evidence_path": stored_evidence.name if stored_evidence else None,
        "evidence_sha256": sha256_bytes(evidence_bytes) if evidence_bytes is not None else None,
        "evidence_status": evidence_status,
        "source_surface": source_surface, "sanitized_confirmed": True,
        "task_success": None, "hard_failure": None, "completion_claim_accuracy": None,
        "status": status, "exclusion_reason": exclusion_reason
    }
    with stored_response.open("xb") as handle:
        handle.write(response_bytes)
    try:
        if stored_evidence is not None and evidence_bytes is not None:
            with stored_evidence.open("xb") as handle:
                handle.write(evidence_bytes)
        with result_path.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    except Exception:
        stored_response.unlink(missing_ok=True)
        if stored_evidence is not None:
            stored_evidence.unlink(missing_ok=True)
        raise
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--package-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--response-file", type=Path, required=True)
    parser.add_argument("--surface-evidence-file", type=Path)
    parser.add_argument("--served-model")
    parser.add_argument("--fallback", choices=["yes", "no", "unknown"], default="unknown")
    parser.add_argument("--source-surface", choices=["claude_app"], required=True)
    parser.add_argument("--confirm-sanitized", action="store_true", required=True)
    parser.add_argument("--confirm-evidence-sanitized", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=LOCAL_ROOT / "imported")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    result = import_response(
        plan, run_id=args.run_id, response_file=args.response_file,
        package_dir=args.package_dir, output_dir=args.output_dir,
        served_model=args.served_model, fallback_detected=parse_optional_bool(args.fallback),
        source_surface=args.source_surface, sanitized_confirmed=args.confirm_sanitized,
        evidence_file=args.surface_evidence_file,
        evidence_sanitized_confirmed=args.confirm_evidence_sanitized
    )
    print(json.dumps({key: result[key] for key in ("run_id", "variant_id", "status", "response_sha256", "exclusion_reason")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
