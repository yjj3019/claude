"""Assertions for latency/lightness cold-start contract."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import measure_load  # noqa: E402
import validate_framework as validator  # noqa: E402
from markdown_sections import parse_sections  # noqa: E402


HEAVY = (
    "PROGRESS.md",
    "SESSION_LOG.md",
    "CHANGELOG.md",
    "README.md",
    "docs/model-usage.md",
    "docs/adaptive-effort.md",
)


class LatencyLightnessTests(unittest.TestCase):
    def test_claude_entry_under_budget(self):
        claude = len((ROOT / "CLAUDE.md").read_text(encoding="utf-8-sig").encode("utf-8"))
        agents = len((ROOT / "AGENTS.md").read_text(encoding="utf-8-sig").encode("utf-8"))
        self.assertLessEqual(claude, validator.MAX_CLAUDE_ENTRY_BYTES)
        self.assertLessEqual(claude + agents, measure_load.MAX_COLD_START_BYTES)
        self.assertLessEqual(claude + agents, validator.MAX_COLD_START_BYTES)

    def test_heavy_paths_not_in_task_map_or_routes(self):
        referenced: set[str] = set()
        sections = parse_sections((ROOT / "docs" / "loading-map.md").read_text(encoding="utf-8-sig"))
        for rel in validator.PATH_RE.findall(sections["Task Map"]):
            referenced.add(rel)
        data = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))
        for route in data.get("routes") or []:
            for key in ("module", "workflow", "reviewer"):
                value = route.get(key)
                if value:
                    referenced.add(value)
            for domain in route.get("domains") or []:
                referenced.add(domain)
            for policy in route.get("policies") or []:
                referenced.add(policy)
        for rel in HEAVY:
            self.assertNotIn(rel, referenced)
            self.assertNotIn(rel, validator.REQUIRED_PACKS)
        for rel in referenced:
            lower = rel.lower()
            self.assertFalse(any(f in lower for f in ("optimization", "simulation-", "-report")))

    def test_latency_phrases_present(self):
        claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8-sig")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8-sig")
        model_usage = (ROOT / "docs" / "model-usage.md").read_text(encoding="utf-8-sig")
        self.assertIn("Latency > completeness", claude)
        self.assertIn("Read `CLAUDE.md` first", agents)
        self.assertIn("Guidance Layout", agents)
        self.assertIn("## When to Load This Doc", model_usage)
        self.assertIn("when choosing or switching", model_usage)

    def test_validator_flags_oversize_claude(self):
        errors: list[str] = []
        with patch.object(validator, "CLAUDE", ROOT / "CHANGELOG.md"):
            # CHANGELOG is larger than budget; reuse as stand-in file object path
            oversized = ROOT / "PROGRESS.md"
            with patch.object(validator, "CLAUDE", oversized):
                validator.validate_claude_entry_budget(errors)
        self.assertTrue(any("exceeds budget" in e for e in errors))

    def test_measure_load_fail_over_cold_start(self):
        import io
        from contextlib import redirect_stdout, redirect_stderr
        buf = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(err):
            code = measure_load.main(["--fail-over-cold-start", "1"])
        self.assertEqual(code, 1)
        self.assertIn("SIMPLE Q&A COLD-START", buf.getvalue())
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code_ok = measure_load.main(["--fail-over-cold-start", "999999"])
        self.assertEqual(code_ok, 0)


if __name__ == "__main__":
    unittest.main()
