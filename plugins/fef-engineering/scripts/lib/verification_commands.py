"""Load segment-anchored verification runner patterns (S3-07)."""
from __future__ import annotations

import json
import re
from pathlib import Path

_CONFIG = Path(__file__).with_name("verification_runners.json")
_RUNNER_AT_START = re.compile(
    r"^(?:" + "|".join(json.loads(_CONFIG.read_text(encoding="utf-8"))["runners"]) + ")"
)


def is_verification_command(command: str) -> bool:
    for segment in re.split(r"[;&|\n]+", command):
        seg = segment.strip()
        if seg and _RUNNER_AT_START.match(seg):
            return True
    return False


def extract_exit_code(data: dict):
    keys = ("returncode", "return_code", "exit_code", "exitCode")
    # Top-level first (some hosts put exit_code on the payload root).
    for code_key in keys:
        if code_key in data:
            return data[code_key]
    response_keys = (
        "tool_response",
        "tool_output",
        "toolOutput",
        "toolResponse",
        "tool_result",  # S4-08 defensive (host schema UNVERIFIED)
        "toolResult",
    )
    for response_key in response_keys:
        response = data.get(response_key)
        if isinstance(response, dict):
            for code_key in keys:
                if code_key in response:
                    return response[code_key]
    return None
