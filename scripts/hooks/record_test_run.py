#!/usr/bin/env python3
"""PostToolUse(Bash) hook: record that a test runner was executed.

Touches .claude/.test-run-marker whenever a Bash tool call runs a recognized
test command. verify_before_stop.py later compares this marker's mtime against
modified source files to enforce Kernel rule 14 (no completion claim without
verification). Always exits 0 and never blocks anything itself.
"""
import json
import re
import sys
from pathlib import Path

TEST_COMMAND = re.compile(r"\b(pytest|unittest|npm test|go test|cargo test)\b")


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        command = str(data.get("tool_input", {}).get("command", ""))
        if not TEST_COMMAND.search(command):
            return 0
        marker = Path(".claude") / ".test-run-marker"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(command[:500], encoding="utf-8")
    except Exception:
        pass  # fail open: a broken hook must never break the session
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
