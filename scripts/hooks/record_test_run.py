#!/usr/bin/env python3
"""PostToolUse(Bash) hook: record verification runs (S3-07).

Touches .claude/.test-run-marker when a Bash call runs a recognized
verification command (see scripts/lib/verification_commands.py and
verification_runners.json). Always exits 0.

S3-07: runners must start a shell segment (command-start or after [;&|]);
grep/prose mentions do not credit.

Exit-code policy (fail-closed): credit only when an explicit exit code is
present and equals 0. Unknown/missing exit codes do not write the marker.
Prefers missing verification over a false-green marker.
"""
import json
import sys
from pathlib import Path

# Allow running as scripts/hooks/*.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.verification_commands import extract_exit_code, is_verification_command


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        command = str(data.get("tool_input", {}).get("command", ""))
        if not is_verification_command(command):
            return 0
        code = extract_exit_code(data)
        if code is None or int(code) != 0:
            return 0
        marker = Path(".claude") / ".test-run-marker"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(command[:500], encoding="utf-8")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
