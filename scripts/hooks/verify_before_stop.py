#!/usr/bin/env python3
"""Stop hook: mechanical enforcement of Kernel rule 14.

If tracked or new *.py / *.md / *.json files were modified during the session
but no verification runner has been executed since the latest modification,
block the stop once and ask for verification. Fails open on any error so it
can never trap a session.

S3-07: gate .md/.json as well as .py. Accepted verification commands are
recorded by record_test_run.py (segment-anchored runners plus framework
validate scripts).
"""
import json
import subprocess
import sys
from pathlib import Path

MARKER = Path(".claude") / ".test-run-marker"
GATED_SUFFIXES = (".py", ".md", ".json")


def path_from_status_line(line: str) -> str:
    """Extract the current on-disk path from one git status --porcelain line.

    Rename/copy entries are "XY old/path.py -> new/path.py"; only the target
    (post-arrow) path still exists on disk.
    """
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path.strip(chr(34))


def changed_gated_files() -> list:
    proc = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10
    )
    if proc.returncode != 0:
        return []
    files = []
    for line in proc.stdout.splitlines():
        path = path_from_status_line(line)
        if path.startswith("scripts/hooks/"):
            continue
        if not path.endswith(GATED_SUFFIXES):
            continue
        candidate = Path(path)
        if candidate.exists():
            files.append(candidate)
    return files


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("stop_hook_active"):
            return 0
        changed = changed_gated_files()
        if not changed:
            return 0
        newest_change = max(f.stat().st_mtime for f in changed)
        if MARKER.exists() and MARKER.stat().st_mtime >= newest_change:
            return 0
        names = ", ".join(str(f) for f in changed[:5])
        print(json.dumps({
            "decision": "block",
            "reason": (
                "Kernel rule 14: modified gated files (" + names + ") have no "
                "verification run recorded after the latest change. Run the "
                "relevant suite (e.g. python3 -m unittest discover -s tests "
                "-p test_*.py) or framework validate "
                "(python3 scripts/validate_framework.py / "
                "python3 scripts/validate_repository.py), report the result, "
                "then finish. If verification is genuinely not applicable, "
                "state that explicitly as a limitation before finishing."
            ),
        }))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
