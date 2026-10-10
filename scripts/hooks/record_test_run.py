#!/usr/bin/env python3
"""Record a recognized verification result against this session and Git snapshot."""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.verification_commands import extract_exit_code, is_verification_command
from lib.verification_state import (RESULT_PREFIX, digest, hook_error, load_state,
                                    repository, save_state, snapshot)

WRAPPER = Path(__file__).resolve().parents[1] / "run_verification.py"


def command_arguments(command: str, tool_name: str) -> list[str] | None:
    if tool_name != "PowerShell":
        return shlex.split(command)
    # A conservative literal subset, not a PowerShell parser. Backslashes are
    # literal here; never use POSIX shlex to reinterpret a Windows path.
    token = r'''(?:"[^"\r\n]*"|'[^'\r\n]*'|[a-zA-Z0-9_./:\\=+-]+)'''
    if not re.fullmatch(r"\s*" + token + r"(?:\s+" + token + r")*\s*", command):
        return None
    return [part[1:-1] if part[0] in ("'", '"') else part
            for part in re.findall(token, command)]


def verification_result(command: str, data: dict, cwd: Path, current: dict) -> int | None:
    # An aggregate shell exit does not prove the verification runner succeeded.
    if any(char in command for char in (";", "&", "|", "\n", "<", ">", "`", "$")):
        return None
    response = data.get("tool_response", {})
    if isinstance(response, dict) and response.get("interrupted"):
        return None
    args = command_arguments(command, data.get("tool_name", "Bash"))
    if not args:
        return None
    if len(args) >= 4 and re.fullmatch(r"(python(?:3(?:\.\d+)?)?|py)(?:\.exe)?", Path(args[0]).name):
        candidate = (cwd / args[1]).resolve()
        if candidate == WRAPPER and args[2] == "--":
            if not is_verification_command(shlex.join(args[3:])):
                return None
            response = data.get("tool_response", {})
            if not isinstance(response, dict) or response.get("interrupted"):
                return None
            lines = str(response.get("stdout", "")).splitlines()
            if not lines or not lines[-1].startswith(RESULT_PREFIX):
                return None
            result = json.loads(lines[-1][len(RESULT_PREFIX):])
            if not isinstance(result, dict):
                return None
            if (result.get("argv_digest") != digest(args[3:])
                    or result.get("snapshot") != digest(current)
                    or result.get("snapshot_before") != result.get("snapshot")):
                return None
            code = result.get("returncode")
            return code if type(code) is int else None
    if not is_verification_command(command):
        return None
    code = extract_exit_code(data)
    return code if type(code) is int else None


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") not in ("Bash", "PowerShell"):
            return 0
        command = data.get("tool_input", {}).get("command", "")
        if not isinstance(command, str):
            raise ValueError("invalid command")
        if not is_verification_command(command) and "run_verification.py" not in command:
            return 0  # Ordinary shell calls need no Git subprocess or content hashing.
        cwd = Path(data.get("cwd", "."))
        root = repository(cwd)
        session = data["session_id"]
        state = load_state(root, session)
        if state is None:
            raise ValueError("SessionStart baseline missing")
        current = snapshot(root)
        try:
            code = verification_result(command, data, cwd, current)
        except ValueError as error:
            hook_error(error)
            code = None  # A malformed attempt must invalidate an earlier pass.
        if code is not None or is_verification_command(command) or "run_verification.py" in command:
            state["verification"] = {"snapshot": digest(current), "returncode": code}
            save_state(root, session, state)
    except Exception as error:
        hook_error(error)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
