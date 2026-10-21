#!/usr/bin/env python3
"""One-shot verification reminder for worktree changes since SessionStart.

Session snapshots cover Git-visible files and deletions, across languages.
Errors fail open with a diagnostic; a reminder is not a test-coverage proof.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.verification_state import (digest, hook_error, load_state, repository,
                                    snapshot, state_failure_path)


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("stop_hook_active"):
            return 0
        root = repository(data.get("cwd", "."))
        if state_failure_path(root, data["session_id"]).exists():
            print(json.dumps({
                "decision": "block",
                "reason": "Verification state could not be saved for this session. "
                          "Run relevant checks again after resolving the storage error; "
                          "an earlier successful record cannot verify this attempt. "
                          "Disclose unavailable verification. This reminder will not loop."
            }))
            return 0
        state = load_state(root, data["session_id"])
        if state is None:
            raise ValueError("SessionStart baseline missing")
        current = snapshot(root)
        if current == state["baseline"]:
            return 0  # An already-dirty, read-only session needs no new test.
        verification = state.get("verification")
        if (isinstance(verification, dict) and verification.get("snapshot") == digest(current)
                and type(verification.get("returncode")) is int and verification["returncode"] == 0):
            return 0
        print(json.dumps({
            "decision": "block",
            "reason": "Worktree changed since SessionStart without successful verification of the current state. "
                      "Run relevant checks, e.g. python scripts/run_verification.py -- python -m unittest discover -s tests. "
                      "Inspect the actual result and coverage; disclose failures or explain why verification is inapplicable. "
                      "This reminder does not prove correctness and will not loop."
        }))
    except Exception as error:
        hook_error(error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
