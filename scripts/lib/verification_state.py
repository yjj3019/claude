"""Session-scoped Git snapshots for the verification reminder, not a security boundary."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

STATE_DIR = Path(".claude") / ".verification"
RESULT_PREFIX = "FEF_VERIFY_RESULT="


def git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, check=True,
                          capture_output=True, timeout=15).stdout


def repository(cwd: str | Path) -> Path:
    return Path(os.fsdecode(git(Path(cwd), "rev-parse", "--show-toplevel")).strip()).resolve()


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()


def snapshot(root: Path) -> dict:
    entries = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    paths = {}
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        status = os.fsdecode(entry[:2])
        name = os.fsdecode(entry[3:])
        if "R" in status or "C" in status:
            index += 1  # -z lists target first, then original name.
        if name.startswith(".claude/.verification/") or name == ".claude/.test-run-marker":
            continue
        path = root / name
        # Do not follow links outside the worktree or read their target contents.
        if path.is_symlink():
            content = hashlib.sha256(os.fsencode(os.readlink(path))).hexdigest()
        elif path.is_file():
            hasher = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    hasher.update(chunk)
            content = hasher.hexdigest()
        else:
            content = None  # Deletions count as changes.
        paths[name] = [status, content]
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=root,
                          capture_output=True, timeout=15)
    return {"head": head.stdout.decode("ascii", errors="replace").strip() if head.returncode == 0 else None,
            "files": paths}


def state_path(root: Path, session_id: str) -> Path:
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("missing session_id")
    return root / STATE_DIR / (hashlib.sha256(session_id.encode()).hexdigest() + ".json")


def load_state(root: Path, session_id: str) -> dict | None:
    path = state_path(root, session_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or "baseline" not in data:
        raise ValueError("invalid session state")
    return data


def save_state(root: Path, session_id: str, data: dict) -> None:
    path = state_path(root, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(data, stream, sort_keys=True)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def hook_error(error: Exception) -> None:
    # No payload, command arguments or secret-bearing exception text.
    import sys
    print(f"FEF verification reminder unavailable ({type(error).__name__}); verify explicitly.", file=sys.stderr)
