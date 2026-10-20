#!/usr/bin/env python3
"""Run a verification argv without a shell; retain output and emit the real result.

Usage: python scripts/run_verification.py -- python -m unittest discover -s tests
The machine-readable footer allows native Bash hooks without exit_code metadata.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from lib.verification_state import RESULT_PREFIX, digest, repository, snapshot


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or args[0] != "--":
        print(__doc__, file=sys.stderr)
        return 2
    command = args[1:]
    # No shell, redirection or output filtering; child stdout/stderr remain intact.
    try:
        root = repository(Path.cwd())
        before = digest(snapshot(root))
        result = subprocess.run(command, check=False)
        record = {"argv_digest": digest(command), "returncode": result.returncode,
                  "snapshot_before": before, "snapshot": digest(snapshot(root))}
        print("\n" + RESULT_PREFIX + json.dumps(record, sort_keys=True), flush=True)
        return result.returncode if result.returncode >= 0 else 128 - result.returncode
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Verification could not complete ({type(error).__name__}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
