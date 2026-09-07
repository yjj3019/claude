#!/usr/bin/env python3
"""Run repository-wide FEF validation and report advisory warnings."""
from __future__ import annotations

import sys
import json
import re
import subprocess
from pathlib import Path

import validate_framework
import validate_routes
from run_golden_tests import validate as validate_golden_tests

ROOT = Path(__file__).resolve().parents[1]
PACK_DIRS = ("policies", "modules", "domains", "workflows", "reviewers")


def advisory_warnings() -> list[str]:
    warnings = []
    route_config = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))
    referenced = set()
    for path in [ROOT / "CLAUDE.md", ROOT / "docs" / "loading-map.md"]:
        referenced.update(re.findall(r"`((?:policies|modules|domains|workflows|reviewers)/[^`]+\.md)`", path.read_text(encoding="utf-8")))
    for route in route_config["routes"]:
        referenced.update(route["policies"])
        referenced.update(item for item in [route["module"], route["workflow"], route["reviewer"]] if item)
    referenced.update(domain["path"] for domain in route_config["domains"])

    packs = {str(path.relative_to(ROOT)).replace("\\", "/") for folder in PACK_DIRS for path in (ROOT / folder).glob("*.md")}
    orphaned = sorted(packs - referenced)
    if orphaned:
        warnings.append(f"packs not referenced by loading-map or routes config: {', '.join(orphaned)}")

    tags = set(subprocess.run(["git", "tag"], cwd=ROOT, check=True, text=True,
        encoding="utf-8", errors="replace", capture_output=True).stdout.split())
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = re.findall(r"^## (v\d+\.\d+(?:\.\d+)?)", changelog, re.MULTILINE)
    if versions and versions[0] not in tags:
        warnings.append(f"latest changelog version has no Git tag: {versions[0]}")
    return warnings


def run_sync_kernel_check() -> int:
    """F-08: fail if inlined Kernel drifts from kernel/ sources."""
    script = ROOT / "scripts" / "sync_kernel.py"
    result = subprocess.run(
        ["python", str(script), "--check"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    out = (result.stdout or "") + (result.stderr or "")
    if out.strip():
        print(out.rstrip())
    return result.returncode


def run_measure_load_budget() -> int:
    """S3-01: fail if CLAUDE.md+AGENTS.md cold-start exceeds 9000 bytes."""
    script = ROOT / "scripts" / "measure_load.py"
    result = subprocess.run(
        ["python", str(script), "--fail-over-cold-start", "9000"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    lines = (result.stdout or "").splitlines()
    for line in lines:
        if "COLD-START" in line or "exceeds" in line.lower() or line.startswith("ERROR"):
            print(line)
    err = (result.stderr or "").strip()
    if result.returncode != 0 and err:
        print(err)
    return result.returncode


def _utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main() -> int:
    _utf8_console()
    failed = False
    if validate_framework.main():
        failed = True
    if validate_routes.main():
        failed = True
    if run_sync_kernel_check():
        failed = True
    if run_measure_load_budget():
        failed = True
    golden = validate_golden_tests()
    if not golden["valid"]:
        failed = True
        for error in golden["errors"]:
            print(f"Golden Test validation error: {error}")
    for warning in advisory_warnings():
        print(f"WARNING: {warning}")
    if failed:
        print("Repository validation failed.")
        return 1
    print(
        f"Repository validation passed: {golden['test_count']} Golden Tests indexed; "
        "model runs not executed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
