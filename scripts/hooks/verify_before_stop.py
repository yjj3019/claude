#!/usr/bin/env python3
"""Stop hook: mechanical enforcement of Kernel rule 14.

If tracked or new *.py files were modified during the session but no test
runner has been executed since the latest modification, block the stop once
and ask for verification. Prompt rules request this behavior; this hook
guarantees it. Fails open on any error (missing git, unreadable input, etc.)
so it can never trap a session.
"""
import json
import subprocess
import sys
from pathlib import Path

MARKER = Path(".claude") / ".test-run-marker"


def changed_python_files() -> list:
    proc = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10
    )
    if proc.returncode != 0:
        return []
    files = []
    for line in proc.stdout.splitlines():
        path = line[3:].strip().strip('"')
        if path.endswith(".py") and not path.startswith("scripts/hooks/"):
            candidate = Path(path)
            if candidate.exists():
                files.append(candidate)
    return files


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("stop_hook_active"):
            return 0  # already blocked once this stop; never loop
        changed = changed_python_files()
        if not changed:
            return 0
        newest_change = max(f.stat().st_mtime for f in changed)
        if MARKER.exists() and MARKER.stat().st_mtime >= newest_change:
            return 0
        names = ", ".join(str(f) for f in changed[:5])
        print(json.dumps({
            "decision": "block",
            "reason": (
                "Kernel rule 14: modified Python files (" + names + ") have no test run "
                "recorded after the latest change. Run the relevant test suite "
                "(e.g. python3 -m unittest discover -s tests -p 'test_*.py'), report "
                "the result, then finish. If tests are genuinely not applicable, "
                "state that explicitly as a limitation before finishing."
            ),
        }))
    except Exception:
        pass  # fail open
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
