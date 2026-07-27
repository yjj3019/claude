"""Shared constants and path-safety helpers for the Fable diagnostic scripts."""
from __future__ import annotations

import re
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
