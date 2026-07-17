#!/usr/bin/env python3
"""Generate native Claude Code reviewer agents from reviewer source files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWERS = ROOT / "reviewers"
AGENTS = ROOT / ".claude" / "agents"
PREFIX = "You are running as a read-only reviewer subagent. Produce one review pass and stop."


def kebab_name(stem: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", stem).lower()


def purpose(text: str, source: Path) -> str:
    match = re.search(r"^## Purpose\s*$\n+(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"missing Purpose section: {source.relative_to(ROOT)}")
    sentence = re.search(r"(.+?\.)", " ".join(match.group(1).split()))
    if not sentence:
        raise ValueError(f"Purpose has no complete sentence: {source.relative_to(ROOT)}")
    return sentence.group(1)


def expected_agents() -> dict[str, str]:
    generated = {}
    for source in sorted(REVIEWERS.glob("*.md")):
        body = source.read_text(encoding="utf-8-sig").rstrip()
        name = kebab_name(source.stem)
        description = f"{purpose(body, source)} Use for one review pass after a draft exists."
        generated[f"{name}.md"] = (
            "---\n"
            f"name: {name}\n"
            f"description: {description}\n"
            "tools: Read, Grep, Glob\n"
            "model: opus\n"
            "maxTurns: 15\n"
            "---\n\n"
            f"{PREFIX}\n\n"
            f"{body}\n"
        )
    return generated


def main() -> int:
    AGENTS.mkdir(parents=True, exist_ok=True)
    generated = expected_agents()
    for stale in set(AGENTS.glob("*.md")) - {AGENTS / name for name in generated}:
        stale.unlink()
    for name, content in generated.items():
        (AGENTS / name).write_text(content, encoding="utf-8")
    print(f"Generated {len(generated)} Claude Code reviewer agents.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
