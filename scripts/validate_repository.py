#!/usr/bin/env python3
"""Run repository-wide FEF validation and report advisory warnings."""
from __future__ import annotations

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

    tags = set(subprocess.run(["git", "tag"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.split())
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = re.findall(r"^## (v\d+\.\d+(?:\.\d+)?)", changelog, re.MULTILINE)
    if versions and versions[0] not in tags:
        warnings.append(f"latest changelog version has no Git tag: {versions[0]}")
    return warnings


def main() -> int:
    failed = False
    if validate_framework.main():
        failed = True
    if validate_routes.main():
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
    print(f"Repository validation passed: {golden['test_count']} Golden Tests indexed; model runs not executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
