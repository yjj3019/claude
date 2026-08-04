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

# ponytail: exact PostToolUse payload field for Bash exit status is not
# confirmed in public docs at time of writing; check every plausible spelling
# and skip the exit-code gate (old fail-open behavior) if none is present.
_EXIT_CODE_KEYS = ("returncode", "return_code", "exit_code", "exitCode", "exitCode".lower())
_RESPONSE_KEYS = ("tool_response", "tool_output", "toolOutput", "toolResponse")


def _exit_code(data: dict):
    for response_key in _RESPONSE_KEYS:
        response = data.get(response_key)
        if isinstance(response, dict):
            for code_key in _EXIT_CODE_KEYS:
                if code_key in response:
                    return response[code_key]
    return None


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        command = str(data.get("tool_input", {}).get("command", ""))
        if not TEST_COMMAND.search(command):
            return 0
        code = _exit_code(data)
        if code is not None and int(code) != 0:
            return 0  # test command failed: do not credit it as verification
        marker = Path(".claude") / ".test-run-marker"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(command[:500], encoding="utf-8")
    except Exception:
        pass  # fail open: a broken hook must never break the session
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
