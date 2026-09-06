#!/usr/bin/env python3
"""Install the FEF Claude framework pack for local AI hosts.

Python 3.11+, standard library only. Intended entry after:
  git clone https://github.com/yjj3019/claude.git && cd claude

Preferred Claude Code usage is opening this clone as the workspace so CLAUDE.md
loads. Skill-style hosts get a copy under <skills-root>/fef-claude/.
Claude Projects (web) cannot be fully automated; use --print-claude.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_NAME = "fef-claude"
REQUIRED_FILES = ("CLAUDE.md", "AGENTS.md", "README.md")
REQUIRED_DIRS = (
    "kernel",
    "policies",
    "modules",
    "domains",
    "reviewers",
    "workflows",
    "docs",
    "scripts",
    "config",
)
OPTIONAL_DIRS = ("tests", "examples", ".claude")
MARKER_FILE = "CLAUDE.md"

# (label, home marker dir, skills/packs root relative to home)
HOSTS: list[tuple[str, str, str]] = [
    ("Claude Code", ".claude", ".claude/skills"),
    ("Codex CLI", ".codex", ".agents/skills"),
    ("Grok", ".grok", ".grok/skills"),
    ("AGENTS.md compatible", ".agents", ".agents/skills"),
    ("Cursor", ".cursor", ".cursor/skills"),
]
FALLBACK_SKILLS_DIR = ".agents/skills"

COPY_IGNORE = shutil.ignore_patterns(
    "__pycache__",
    "*.pyc",
    ".pytest_cache",
    ".git",
    ".github",
)


def _utf8_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def detect_targets(home: Path | None = None) -> list[tuple[str, Path]]:
    """Return (label, skills-or-packs-root) for detected AI hosts and env overrides."""
    home = home or Path.home()
    found: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    for label, marker, skills_dir in HOSTS:
        if not (home / marker).is_dir():
            continue
        target = (home / skills_dir).resolve()
        if target not in seen:
            seen.add(target)
            found.append((label, target))

    for env_name in ("AI_PACK_DIR", "AI_SKILLS_DIR", "CURSOR_PACK_DIR", "CURSOR_SKILLS_DIR"):
        raw = os.environ.get(env_name)
        if not raw:
            continue
        target = Path(raw).expanduser().resolve()
        if target not in seen:
            seen.add(target)
            found.append((f"${env_name}", target))

    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        target = (Path(codex_home).expanduser() / "skills").resolve()
        if target not in seen:
            seen.add(target)
            found.append(("$CODEX_HOME/skills", target))

    return found


def pack_source_paths(with_tests: bool) -> list[tuple[str, Path]]:
    """Relative name → absolute source path for items to copy."""
    items: list[tuple[str, Path]] = []
    for name in REQUIRED_FILES:
        path = REPO_ROOT / name
        if not path.is_file():
            raise SystemExit(f"Missing required pack file: {name}")
        items.append((name, path))
    readme_ko = REPO_ROOT / "README.ko.md"
    if readme_ko.is_file():
        items.append(("README.ko.md", readme_ko))
    for name in REQUIRED_DIRS:
        path = REPO_ROOT / name
        if not path.is_dir():
            raise SystemExit(f"Missing required pack directory: {name}")
        items.append((name, path))
    if with_tests:
        for name in OPTIONAL_DIRS:
            path = REPO_ROOT / name
            if path.is_dir() or path.is_file():
                items.append((name, path))
    else:
        # Always include .claude settings/agents when present (hooks discovery).
        claude_dir = REPO_ROOT / ".claude"
        if claude_dir.is_dir():
            items.append((".claude", claude_dir))
    return items


def write_skill_hint(dest_pack: Path) -> None:
    """Write a minimal SKILL.md so skill-style hosts can discover the pack."""
    content = """# FEF Claude Framework Pack

Claude-oriented engineering guidance: Kernel, task packs, routing, and integrity rules.

## When to use

- Engineering, RCA, proposals, coding, reviews, and evidence-backed completion
- Prefer opening a clone of this repository as a Claude Code workspace (`CLAUDE.md`)
- For Claude Projects (web): paste `CLAUDE.md` into Project Instructions (`python scripts/install_pack.py --print-claude`)

## Layout

- `CLAUDE.md` — runtime entry (inlined Kernel + Autoload)
- `AGENTS.md` — lightweight repository entry for AGENTS-compatible hosts
- `kernel/` `policies/` `modules/` `domains/` `reviewers/` `workflows/`
- `docs/loading-map.md` — task pack routing; `docs/model-usage.md` — model floor
- `scripts/` — sync / validate / measure / install / detect_task

## Context Budget

Normally Kernel (via `CLAUDE.md`) + packs named by `docs/loading-map.md` within Load Limits
(Module 1 / Domain ≤2 / Workflow 1 / Reviewer 1 / Policies ≤3). Do not preload every
module, domain, or doc. Model changes keep the same integrity rules; escalate the
model when blocked — do not expand unrelated packs.
"""
    (dest_pack / "SKILL.md").write_text(content, encoding="utf-8")


def write_bootstrap_note(dest_pack: Path) -> None:
    """Short note at pack root pointing users at CLAUDE.md / clone workflow."""
    note = """# Installed pack bootstrap

This directory is a copy of the FEF Claude framework for skill-style hosts.

**Preferred Claude Code setup:** clone https://github.com/yjj3019/claude.git and open that
repository as the workspace so `CLAUDE.md` loads at the workspace root.

**This copy:** use `CLAUDE.md` here as the runtime entry when the host loads skills from
this folder. Keep Operational Integrity and Context Budget unchanged across models
(Opus / Fable / Sonnet / Haiku). See `docs/model-usage.md`.

**Claude Projects:** paste `CLAUDE.md` into Project Instructions; attach needed packs as
project knowledge. Run `python scripts/install_pack.py --print-claude` from a clone.

**Verify:** `python scripts/validate_framework.py` (from this pack or the clone).
"""
    (dest_pack / "INSTALL_NOTE.md").write_text(note, encoding="utf-8")


def install_pack(
    skills_root: Path,
    *,
    with_tests: bool = False,
    dry_run: bool = False,
) -> Path:
    """Copy the pack into skills_root/fef-claude/. Overwrites idempotently."""
    skills_root = skills_root.expanduser()
    if skills_root.exists() and not skills_root.is_dir():
        raise SystemExit(f"Destination is not a directory: {skills_root}")
    dest = skills_root / PACK_NAME
    items = pack_source_paths(with_tests=with_tests)

    if dry_run:
        return dest

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    for relative, source in items:
        target = dest / relative
        if source.is_dir():
            shutil.copytree(source, target, ignore=COPY_IGNORE)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    write_skill_hint(dest)
    write_bootstrap_note(dest)

    if not (dest / MARKER_FILE).is_file():
        shutil.rmtree(dest, ignore_errors=True)
        raise SystemExit(f"Installation verification failed: missing {MARKER_FILE} in {dest}")
    return dest


def verify_install(dest_pack: Path) -> list[str]:
    """Return problems found in an installed pack (empty = OK)."""
    problems: list[str] = []
    if not dest_pack.is_dir():
        return [f"missing pack directory: {dest_pack}"]
    for name in REQUIRED_FILES:
        if not (dest_pack / name).is_file():
            problems.append(f"missing file: {name}")
    for name in REQUIRED_DIRS:
        if not (dest_pack / name).is_dir():
            problems.append(f"missing directory: {name}")
        elif name == "scripts":
            for script in (
                "validate_framework.py",
                "sync_kernel.py",
                "install_pack.py",
                "detect_task.py",
            ):
                if not (dest_pack / "scripts" / script).is_file():
                    problems.append(f"missing scripts/{script}")
    return problems


def run_validate(tree: Path) -> int:
    """Run validate_framework.py from an installed or source tree. Return exit code."""
    script = tree / "scripts" / "validate_framework.py"
    if not script.is_file():
        print(f"validate script missing: {script}", file=sys.stderr)
        return 1
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(script)],
        cwd=str(tree),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def print_claude_steps() -> None:
    entry = REPO_ROOT / "CLAUDE.md"
    print("Claude Projects (web) — paste steps")
    print("=" * 60)
    print("1. Open Claude → create or open a Project.")
    print("2. Open Project Instructions / custom instructions for the project.")
    print("3. Paste the full contents of CLAUDE.md (path below).")
    print(f"   File: {entry}")
    print("4. Attach needed modules/domains/workflows as project knowledge.")
    print("   Do not attach every file under docs/ unless the task requires it.")
    print("5. Keep Context Budget: Kernel + loading-map packs within Load Limits.")
    print("6. Model choice (advisory): see docs/model-usage.md")
    print("   (Opus 5 / Fable 5.1 / Sonnet 5 / Haiku 4.5). Same floor on every model.")
    print()
    print("Exact file to paste:")
    print(f"  {entry}")
    if entry.is_file():
        size = entry.stat().st_size
        print(f"  ({size} bytes UTF-8 on disk)")


def destination_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser()
    for env_name in ("AI_PACK_DIR", "AI_SKILLS_DIR", "CURSOR_PACK_DIR", "CURSOR_SKILLS_DIR"):
        raw = os.environ.get(env_name)
        if raw:
            return Path(raw).expanduser()
    if raw := os.environ.get("CODEX_HOME"):
        return Path(raw).expanduser() / "skills"
    raise SystemExit(
        "Set --dest, AI_PACK_DIR / AI_SKILLS_DIR / CURSOR_* / CODEX_HOME, or use --auto."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/install_pack.py --auto\n"
            "  python scripts/install_pack.py --dest ~/.agents/skills\n"
            "  python scripts/install_pack.py --print-claude\n"
            "  python scripts/install_pack.py --check --dest ~/.agents/skills\n"
        ),
    )
    parser.add_argument(
        "--dest",
        help="Parent skills/packs directory (pack lands in <dest>/fef-claude/)",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Detect AI hosts and install into each skills directory "
        f"(fallback: ~/{FALLBACK_SKILLS_DIR})",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="Print detected install targets without installing",
    )
    parser.add_argument(
        "--print-claude",
        action="store_true",
        help="Print exact steps to paste CLAUDE.md into Claude Project Instructions",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify installed pack files and run validate_framework.py when tests/ present",
    )
    parser.add_argument(
        "--with-tests",
        action="store_true",
        help="Also copy tests/ examples/ into the installed pack",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show destinations without copying files",
    )
    args = parser.parse_args(argv)
    _utf8_console()

    if args.print_claude:
        print_claude_steps()
        return 0

    if args.list_targets:
        targets = detect_targets()
        if targets:
            for label, path in targets:
                print(f"{label}: {path}")
        else:
            print(f"No AI host detected — default: {Path.home() / FALLBACK_SKILLS_DIR}")
        return 0

    if args.check:
        roots: list[Path] = []
        if args.dest:
            roots.append(Path(args.dest).expanduser() / PACK_NAME)
        elif args.auto:
            targets = detect_targets()
            if not targets:
                targets = [("fallback", Path.home() / FALLBACK_SKILLS_DIR)]
            roots.extend(root / PACK_NAME for _, root in targets)
        else:
            try:
                roots.append(destination_root(None) / PACK_NAME)
            except SystemExit:
                roots.append(REPO_ROOT)

        failed = False
        for pack in roots:
            print(f"Checking: {pack}")
            problems = verify_install(pack) if pack != REPO_ROOT else []
            if pack == REPO_ROOT:
                for name in REQUIRED_FILES:
                    if not (pack / name).is_file():
                        problems.append(f"missing file: {name}")
                for name in REQUIRED_DIRS:
                    if not (pack / name).is_dir():
                        problems.append(f"missing directory: {name}")
            if problems:
                failed = True
                for problem in problems:
                    print(f"  FAIL: {problem}")
                continue
            print("  files OK")
            if (pack / "tests" / "Scorecard.md").is_file():
                code = run_validate(pack)
                if code != 0:
                    failed = True
                else:
                    print("  validate OK")
            else:
                print("  validate skipped (tests/ not installed; reinstall with --with-tests)")
        return 1 if failed else 0

    if args.auto:
        targets = detect_targets()
        if not targets:
            fallback = Path.home() / FALLBACK_SKILLS_DIR
            print(f"No AI host detected — installing to shared location: {fallback}")
            targets = [("AGENTS.md compatible (fallback)", fallback)]
        summaries: list[str] = []
        for label, root in targets:
            dest = install_pack(root, with_tests=args.with_tests, dry_run=args.dry_run)
            action = "Would install" if args.dry_run else "Installed"
            line = f"{action}: {dest}  ({label})"
            print(line)
            summaries.append(line)
            if not args.dry_run:
                problems = verify_install(dest)
                if problems:
                    print("  problems: " + "; ".join(problems), file=sys.stderr)
                    return 1
        print()
        print("Summary:")
        for line in summaries:
            print(f"  {line}")
        print()
        print("Next steps:")
        print("  Claude Code → open the git clone as workspace (loads CLAUDE.md), or use the installed pack.")
        print("  Claude Projects → python scripts/install_pack.py --print-claude")
        print("  Verify  → python scripts/install_pack.py --check --auto")
        return 0

    root = destination_root(args.dest)
    dest = install_pack(root, with_tests=args.with_tests, dry_run=args.dry_run)
    action = "Would install" if args.dry_run else "Installed"
    print(f"{action}: {dest}")
    if not args.dry_run:
        problems = verify_install(dest)
        if problems:
            print("Installation incomplete:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
