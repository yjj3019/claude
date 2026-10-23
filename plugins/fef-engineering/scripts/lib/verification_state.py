"""Session-scoped Git snapshots for the verification reminder, not a security boundary."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STATE_DIR = Path(".claude") / ".verification"
RESULT_PREFIX = "FEF_VERIFY_RESULT="


def git_executable() -> str:
    selected = os.environ.get("FEF_GIT_EXECUTABLE")
    if not selected:
        return "git"
    path = Path(selected)
    if (not path.is_absolute() or not path.is_file()
            or (sys.platform == "win32" and path.suffix.lower() != ".exe")):
        raise OSError("FEF_GIT_EXECUTABLE must name an absolute executable file")
    return selected


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run([git_executable(), *args], cwd=root, check=check,
                              capture_output=True, timeout=15)
    except subprocess.TimeoutExpired as error:
        # Normalize only our own Git calls for the sanitized operation whitelist.
        error.cmd = ["git", *args]
        raise


def git(root: Path, *args: str) -> bytes:
    return run_git(root, *args).stdout


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
    head = run_git(root, "rev-parse", "--verify", "HEAD", check=False)
    result = {"head": head.stdout.decode("ascii", errors="replace").strip() if head.returncode == 0 else None,
              "files": paths}
    submodules = {}
    # Enumerate gitlinks even when submodule.*.ignore hides their dirty status.
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, name_bytes = entry.split(b"\t", 1)
        mode, oid, stage = metadata.split()
        if mode != b"160000":
            continue
        name = os.fsdecode(name_bytes)
        child = root / name
        resolved = child.resolve()
        if child.is_symlink() or resolved == root.resolve() or not resolved.is_relative_to(root.resolve()):
            raise ValueError("submodule path escapes the worktree")
        worktree = "uninitialized"
        if child.is_dir() and repository(child) == resolved:
            worktree = snapshot(child)
        submodules[f"{name}:{stage.decode('ascii')}"] = {
            "index": oid.decode("ascii"), "worktree": worktree,
        }
    if submodules:
        result["submodules"] = submodules
    return result


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


def state_failure_path(root: Path, session_id: str) -> Path:
    return state_path(root, session_id).with_suffix(".failed")


def save_state(root: Path, session_id: str, data: dict) -> None:
    path = state_path(root, session_id)
    marker = state_failure_path(root, session_id)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, sort_keys=True)
        os.replace(temporary, path)
        temporary.unlink(missing_ok=True)
        marker.unlink(missing_ok=True)
    except Exception:
        try:
            marker.touch()
        except OSError as error:
            hook_error(error)
            # shortcut: marker write failure is stderr-only; use host storage for durable reporting.
            print("FEF verification storage failure could not be persisted; verify explicitly.", file=sys.stderr)
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError as error:
                hook_error(error)
        raise  # Preserve the original failure if diagnostics or cleanup also fail.


def error_description(error: Exception) -> str:
    description = type(error).__name__
    if isinstance(error, subprocess.TimeoutExpired):
        args = error.cmd
        if isinstance(args, (list, tuple)) and all(isinstance(arg, str) for arg in args):
            operation = {
                ("git", "rev-parse", "--show-toplevel"): "repository",
                ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"): "status",
                ("git", "rev-parse", "--verify", "HEAD"): "head",
                ("git", "ls-files", "--stage", "-z"): "index",
            }.get(tuple(args))
            if operation:
                description += f"; git_operation={operation}"
    return description


def hook_error(error: Exception) -> None:
    # No payload, command arguments or secret-bearing exception text.
    print(f"FEF verification reminder unavailable ({error_description(error)}); verify explicitly.", file=sys.stderr)
