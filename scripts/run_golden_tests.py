#!/usr/bin/env python3
"""Validate Golden Test metadata without requiring a model API."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "golden-tests.json"
SCHEMA = ROOT / "config" / "scorecard.schema.json"
HEADER_RE = re.compile(r"^# Golden Test (\d{3}):", re.MULTILINE)


def validate_result(data: dict, path: Path) -> list[str]:
    errors = []
    required = {"test_id", "baseline", "framework", "dimensions", "verdict"}
    missing = required - set(data)
    if missing:
        return [f"{path.relative_to(ROOT)} missing fields: {sorted(missing)}"]
    if not re.fullmatch(r"GT\d{3}", data["test_id"]):
        errors.append(f"{path.relative_to(ROOT)} has invalid test_id")
    for name in ("baseline", "framework"):
        variant = data[name]
        if not isinstance(variant.get("critical_error"), bool) or not 1 <= variant.get("score", 0) <= 5:
            errors.append(f"{path.relative_to(ROOT)} has invalid {name} score/critical_error")
    if data["verdict"] not in {"pass", "fail", "not_run"}:
        errors.append(f"{path.relative_to(ROOT)} has invalid verdict")
    if any(not isinstance(score, int) or not 1 <= score <= 5 for score in data["dimensions"].values()):
        errors.append(f"{path.relative_to(ROOT)} has dimension score outside 1..5")
    if data["framework"]["critical_error"] and data["verdict"] == "pass":
        errors.append(f"{path.relative_to(ROOT)} passes despite framework critical_error")
    return errors


def validate() -> dict:
    errors = []
    metadata = json.loads(CONFIG.read_text(encoding="utf-8"))["tests"]
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    ids = [item["id"] for item in metadata]
    if len(ids) != len(set(ids)):
        errors.append("duplicate Golden Test ID in config/golden-tests.json")

    files = {}
    for path in sorted((ROOT / "tests").glob("GoldenTest-*.md")):
        match = HEADER_RE.search(path.read_text(encoding="utf-8-sig"))
        if match:
            files[match.group(1)] = path
    if set(ids) != set(files):
        errors.append(f"Golden Test metadata/file mismatch: config={sorted(ids)}, files={sorted(files)}")

    for item in metadata:
        for rel in item["required_files"]:
            if not (ROOT / rel).exists():
                errors.append(f"GT{item['id']} missing required file: {rel}")

    required_schema = {"test_id", "baseline", "framework", "dimensions", "verdict"}
    if set(schema.get("required", [])) != required_schema:
        errors.append("scorecard schema required fields do not match the runner contract")
    for path in (ROOT / "tests" / "results").glob("*.json"):
        errors.extend(validate_result(json.loads(path.read_text(encoding="utf-8")), path))

    coverage = {
        "tasks": dict(Counter(item["task"] for item in metadata)),
        "workflows": dict(Counter(item["workflow"] for item in metadata)),
        "domains": dict(Counter(domain for item in metadata for domain in item["domains"])),
        "modes": dict(Counter(item["mode"] for item in metadata))
    }
    return {
        "valid": not errors,
        "test_count": len(metadata),
        "static_or_fixture_count": sum(item["mode"] in {"static", "fixture"} for item in metadata),
        "model_runs_executed": 0,
        "errors": errors,
        "coverage": coverage
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true", help="Validate metadata and fixtures without model execution")
    parser.add_argument("--output", type=Path, help="Optional JSON summary path")
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
