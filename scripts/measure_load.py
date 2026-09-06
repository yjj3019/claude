#!/usr/bin/env python3
"""Estimate FEF context load (UTF-8 bytes / rough tokens) for Kernel-only and routes.

Uses CLAUDE.md + packs named by config/routes.json. Reports the accidental
full-tree dump size as an anti-pattern upper bound. Fence-aware section helpers
live in markdown_sections.py for docs that need H2 scoping.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "CLAUDE.md"
ROUTES = ROOT / "config" / "routes.json"

PACK_DIRS = ("modules", "domains", "workflows", "reviewers", "policies", "docs", "kernel")


def file_bytes(rel: str | Path) -> int:
    path = ROOT / rel if not isinstance(rel, Path) else rel
    return len(path.read_text(encoding="utf-8-sig").encode("utf-8"))


def rough_tokens(nbytes: int) -> int:
    return max(0, (nbytes + 3) // 4)


def route_paths(route: dict) -> list[str]:
    paths: list[str] = []
    for key in ("module", "workflow", "reviewer"):
        value = route.get(key)
        if value:
            paths.append(value)
    for domain in route.get("domains") or []:
        paths.append(domain)
    for policy in route.get("policies") or []:
        paths.append(policy)
    return paths


def sum_existing(paths: list[str]) -> tuple[int, list[str]]:
    total = 0
    present: list[str] = []
    for rel in paths:
        path = ROOT / rel
        if path.is_file():
            total += file_bytes(path)
            present.append(rel)
    return total, present


def all_pack_bytes() -> int:
    total = 0
    for directory in PACK_DIRS:
        base = ROOT / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*.md"):
            total += file_bytes(path)
    return total


def report() -> int:
    if not CLAUDE.is_file() or not ROUTES.is_file():
        print("missing CLAUDE.md or config/routes.json", file=sys.stderr)
        return 1

    entry = file_bytes(CLAUDE)
    data = json.loads(ROUTES.read_text(encoding="utf-8"))
    routes = data.get("routes") or []

    print("FEF load estimates; excludes host/system prompts and tool schemas.")
    print("Bytes: UTF-8 without BOM. Tokens: uncalibrated bytes/4 heuristic.")
    print(f"{'Scenario':<42} {'bytes':>8} {'~tokens':>8}  files")
    print("-" * 100)

    print(
        f"{'Kernel entry (CLAUDE.md only)':<42} {entry:>8} {rough_tokens(entry):>8}  "
        f"CLAUDE.md"
    )

    max_route = 0
    for route in routes:
        label = route.get("id") or route.get("label") or "route"
        paths = route_paths(route)
        pack_bytes, present = sum_existing(paths)
        # Domains are selected at runtime; routes.json may omit them — still count listed packs.
        total = entry + pack_bytes
        max_route = max(max_route, total)
        files = "CLAUDE.md" + ("; " + ", ".join(present) if present else " (packs via detect)")
        print(f"{label:<42} {total:>8} {rough_tokens(total):>8}  {files}")

    dump = entry + all_pack_bytes()
    print(
        f"{'ANTI-PATTERN all packs+docs+kernel':<42} {dump:>8} {rough_tokens(dump):>8}  "
        f"full tree"
    )
    print()
    if dump <= max_route * 2:
        print("NOTE: full-tree dump is not dramatically larger than max route; still avoid it.")
    else:
        ratio = dump / max(max_route, 1)
        print(f"Full-tree dump is ~{ratio:.1f}x the heaviest mapped route — do not autoload it.")
    print("Load Limits (from routes.json / loading-map): module 1, domain ≤2, workflow 1,")
    print("reviewer 1, policies ≤3. Simple low-risk tasks stay Kernel-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(report())
