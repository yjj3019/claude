#!/usr/bin/env python3
"""Capture the session's initial worktree, preserving existing state on resume/compact."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.verification_state import hook_error, load_state, repository, save_state, snapshot
from sync_kernel import ROOT, rendered_kernel


def main() -> int:
    # Plugin CLAUDE.md is not loaded by the host. Clone installs already load it.
    if os.environ.get("CLAUDE_PLUGIN_ROOT"):
        try:
            context = rendered_kernel() + (
                f"\n\nFEF packs are installed at {ROOT.as_posix()}. "
                f"For substantial tasks, read {(ROOT / 'docs/loading-map.md').as_posix()}. "
                "Resolve all pack paths against that installation, not the working project."
            )
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "SessionStart", "additionalContext": context,
            }}))
        except Exception as error:
            hook_error(error)
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
