#!/usr/bin/env python3
"""Capture the session's initial worktree, preserving existing state on resume/compact."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.verification_state import hook_error, load_state, repository, save_state, snapshot


def main() -> int:
    try:
        data = json.load(sys.stdin)
        root = repository(data.get("cwd", "."))
        session = data["session_id"]
        if load_state(root, session) is None or data.get("source") == "clear":
            save_state(root, session, {"version": 1, "baseline": snapshot(root), "verification": None})
    except Exception as error:
        hook_error(error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
