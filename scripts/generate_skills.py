#!/usr/bin/env python3
"""Generate Claude Code native skills from config/routes.json.

Experiment branch (skills-migration A/B): each route in routes.json becomes a
`.claude/skills/fef-<id>/SKILL.md` whose frontmatter description carries the
route's trigger conditions, so Claude Code's native skill selection replaces
the prompt-driven Autoload Protocol. routes.json stays the single source of
truth; regenerate with this script instead of editing skills by hand.

Usage:
    python scripts/generate_skills.py           # write skills
    python scripts/generate_skills.py --check   # verify, exit 1 on drift
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "config" / "routes.json"
SKILLS_DIR = ROOT / ".claude" / "skills"


def load_config() -> dict:
    return json.loads(ROUTES.read_text(encoding="utf-8-sig"))


def domain_lines(config: dict) -> str:
    lines = []
    for d in config["domains"]:
        name = Path(d["path"]).stem
        kws = ", ".join(d["keywords"])
        extra = ""
        if d.get("subsumes"):
            extra = " (subsumes " + ", ".join(Path(s).stem for s in d["subsumes"]) + ")"
        lines.append(f"- {kws} -> `{d['path']}`{extra}")
    return "\n".join(lines)


def render_skill(route: dict, config: dict) -> str:
    limits = config["limits"]
    keywords = ", ".join(route["keywords"])
    reviewer = route.get("reviewer")
    reviewer_line = (
        f"Reviewer: `{reviewer}` - run at most once per artifact, after a draft exists; do not review reviewer output."
        if reviewer else "Reviewer: none for this route."
    )
    policies = "\n".join(f"- `{p}`" for p in route["policies"])
    high_risk = ", ".join(config["high_risk_keywords"])
    description = (
        f"{route['label']} (FEF route '{route['id']}'). Use when the task involves: {keywords}. "
        f"Base risk level: {route['risk_level']}. Loads the FEF packs for this task type."
    )
    return f"""---
name: fef-{route['id'].replace('_', '-')}
description: {description}
---

# FEF Route: {route['label']}

Generated from `config/routes.json` by `scripts/generate_skills.py`. Do not edit by hand.

When this skill triggers, read and follow these FEF packs from the repository root, in this order:

## Policies

{policies}

## Module and Workflow

- Module: `{route['module']}`
- Workflow: `{route['workflow']}`
- {reviewer_line}

## Domain Packs

If the task names a technology, additionally read the matching domain pack (max {limits['domains']}):

{domain_lines(config)}

## Limits and Risk

- Pack limits per task: {limits['policies']} policies, {limits['modules']} module, {limits['domains']} domains, {limits['workflows']} workflow, {limits['reviewers']} reviewer.
- Base risk level for this route: {route['risk_level']}. If the task mentions any of ({high_risk}), treat it as high risk and raise verification depth per the Kernel Meta Rules.
- The inlined Kernel in `CLAUDE.md` always applies; these packs extend it, never replace it.
"""


def expected_skills(config: dict) -> dict:
    return {
        f"fef-{route['id'].replace('_', '-')}": render_skill(route, config)
        for route in config["routes"]
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify generated skills without writing; exit 1 on drift")
    args = parser.parse_args(argv)
    try:
        config = load_config()
        expected = expected_skills(config)
    except (OSError, ValueError, KeyError) as error:
        print(f"generate_skills error: {error}", file=sys.stderr)
        return 2
    if args.check:
        problems = []
        actual_dirs = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()} if SKILLS_DIR.is_dir() else set()
        for name, content in expected.items():
            path = SKILLS_DIR / name / "SKILL.md"
            if not path.is_file():
                problems.append(f"missing skill: {name}")
            elif path.read_text(encoding="utf-8") != content:
                problems.append(f"stale skill: {name}")
        for extra in sorted(actual_dirs - set(expected)):
            problems.append(f"unexpected skill dir: {extra}")
        if problems:
            for p in problems:
                print(p, file=sys.stderr)
            print("skills are out of sync; run python scripts/generate_skills.py", file=sys.stderr)
            return 1
        print(f"{len(expected)} generated skills are in sync.")
        return 0
    if SKILLS_DIR.is_dir():
        for child in SKILLS_DIR.iterdir():
            if child.is_dir() and child.name.startswith("fef-"):
                shutil.rmtree(child)
    for name, content in expected.items():
        target = SKILLS_DIR / name
        target.mkdir(parents=True, exist_ok=True)
        (target / "SKILL.md").write_text(content, encoding="utf-8")
    print(f"Generated {len(expected)} skills under {SKILLS_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
