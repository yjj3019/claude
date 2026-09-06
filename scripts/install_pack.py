#!/usr/bin/env python3
"""Install the FEF Claude framework pack for local AI hosts.

Python 3.11+, standard library only. Intended entry after:
  git clone https://github.com/yjj3019/claude.git && cd claude
  python3 scripts/install_pack.py --auto

Preferred Claude Code usage is opening this clone as the workspace so CLAUDE.md
loads. Skill-style hosts get a copy under <skills-root>/fef-claude/.

Sibling install is opt-in only (--siblings PATH, FEF_SIBLING_ROOTS,
--siblings-only, or --scan-sibling-parent). Default --auto installs host skills only.
Works when cwd is a sibling: python3 /path/to/claude/scripts/install_pack.py --siblings PATH
(REPO_ROOT is derived from this script's location). Existing fef-claude/ is preserved
unless --force (identical pack hash is skipped).

Claude Projects (web) cannot be fully automated; use --print-claude.
AI bootstrap one-liner: python3 scripts/install_pack.py --print-bootstrap
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_NAME = "fef-claude"
REQUIRED_FILES = ("CLAUDE.md", "AGENTS.md", "README.md")
REQUIRED_VERIFY_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "docs/adaptive-effort.md",
    "scripts/measure_load.py",
    "scripts/lib/adaptive_effort.py",
)
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

# S3-09: default install keeps runtime docs only (history/dev docs stay in clone).
RUNTIME_DOCS = frozenset(
    {
        "loading-map.md",
        "adaptive-effort.md",
        "model-usage.md",
        "context-protocol.md",
        "knowledge-governance.md",
        "Installation.md",
        "FAQ.md",
    }
)
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

# Env: os.pathsep-separated absolute (or ~) paths of extra sibling project roots.
SIBLING_ROOTS_ENV = "FEF_SIBLING_ROOTS"


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


def _is_git_repo(path: Path) -> bool:
    """True if path looks like a git work tree (dir or file .git)."""
    git = path / ".git"
    return git.is_dir() or git.is_file()


def discover_sibling_repos(
    repo_root: Path | None = None,
    *,
    extra_roots: list[Path] | None = None,
    parent: Path | None = None,
    scan_sibling_parent: bool = False,
) -> list[Path]:
    """Discover sibling git repos for opt-in install (S4-09).

    Parent-directory scan is OFF by default. Enable via:
      - parent=... (explicit), or
      - scan_sibling_parent=True (uses repo_root.parent), or
      - FEF_SIBLING_PARENT set to a non-empty path.

    Always honors FEF_SIBLING_ROOTS (os.pathsep-separated) and extra_roots
    (--siblings). Excludes self. Returns sorted unique resolved paths.
    """
    repo_root = (repo_root or REPO_ROOT).resolve()
    found: list[Path] = []
    seen: set[Path] = set()

    def _add(candidate: Path) -> None:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            return
        if resolved == repo_root or resolved in seen:
            return
        if not resolved.is_dir():
            return
        if not _is_git_repo(resolved):
            return
        seen.add(resolved)
        found.append(resolved)

    # Parent scan is opt-in only (S4-09). Never default to repo_root.parent.
    scan_parent: Path | None = None
    if parent is not None:
        scan_parent = parent.resolve()
    elif "FEF_SIBLING_PARENT" in os.environ:
        raw_parent = os.environ.get("FEF_SIBLING_PARENT", "")
        if raw_parent.strip():
            scan_parent = Path(raw_parent).expanduser().resolve()
    elif scan_sibling_parent:
        scan_parent = repo_root.parent.resolve()

    if scan_parent is not None and scan_parent.is_dir():
        try:
            children = list(scan_parent.iterdir())
        except OSError:
            children = []
        for child in children:
            if child.is_dir():
                _add(child)

    raw_env = os.environ.get(SIBLING_ROOTS_ENV, "")
    if raw_env.strip():
        for part in raw_env.split(os.pathsep):
            part = part.strip()
            if part:
                _add(Path(part))

    for root in extra_roots or []:
        _add(root)

    return sorted(found, key=lambda p: str(p))


def sibling_skill_roots(sibling: Path) -> list[tuple[str, Path]]:
    """Non-destructive skill install roots under a sibling project.

    Prefer existing .claude/skills or .agents/skills. Otherwise create skills
    dirs under .claude / .agents when markers exist (.claude/, .cursor/,
    AGENTS.md, .git). Claude/Cursor projects get .claude/skills; AGENTS.md or
    .agents/ also get .agents/skills. Bare git siblings default to .claude/skills.
    """
    sibling = sibling.resolve()
    roots: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def _add(label: str, skills: Path) -> None:
        try:
            resolved = skills.expanduser().absolute()
        except OSError:
            return
        if resolved in seen:
            return
        seen.add(resolved)
        roots.append((label, resolved))

    has_claude = (sibling / ".claude").is_dir()
    has_cursor = (sibling / ".cursor").is_dir()
    has_agents_dir = (sibling / ".agents").is_dir()
    has_agents_md = (sibling / "AGENTS.md").is_file()
    has_git = _is_git_repo(sibling)
    claude_skills = sibling / ".claude" / "skills"
    agents_skills = sibling / ".agents" / "skills"

    if claude_skills.is_dir() or has_claude or has_cursor:
        _add("sibling .claude/skills", claude_skills)
    if agents_skills.is_dir() or has_agents_dir or has_agents_md:
        _add("sibling .agents/skills", agents_skills)

    # Bare git (or only .git marker): still land a pack under .claude/skills.
    if not roots and has_git:
        _add("sibling .claude/skills", claude_skills)

    return roots


def parse_sibling_paths(values: list[str] | None) -> list[Path]:
    """Parse repeated --siblings PATH arguments into Paths."""
    if not values:
        return []
    return [Path(v) for v in values]


def print_bootstrap() -> None:
    """One-liner for host install; sibling install is opt-in."""
    script = REPO_ROOT / "scripts" / "install_pack.py"
    print("# FEF host skills bootstrap (default --auto = hosts only)")
    print(f"python3 {script} --auto")
    print("# Or from this clone's directory:")
    print("python3 scripts/install_pack.py --auto")
    print("# Sibling install is opt-in (does not run on bare --auto):")
    print("#   --siblings PATH   FEF_SIBLING_ROOTS=...   --siblings-only")
    print("#   --scan-sibling-parent  (explicit parent-dir git scan; default OFF)")
    print("# Existing fef-claude/: preserved unless --force (identical hash skipped)")
    print("# Dry-run: add --dry-run")


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
- `docs/loading-map.md` — task pack routing; `docs/adaptive-effort.md` — L0–L3 tiers; `docs/model-usage.md` — model floor
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


def _hash_file(path: Path) -> bytes:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.digest()


def pack_content_fingerprint(pack_dir: Path) -> str | None:
    """Fingerprint of key pack files (empty if required markers missing)."""
    if not pack_dir.is_dir():
        return None
    digest = hashlib.sha256()
    for name in REQUIRED_FILES:
        file_path = pack_dir / name
        if not file_path.is_file():
            return None
        digest.update(name.encode("utf-8"))
        digest.update(_hash_file(file_path))
    return digest.hexdigest()


def source_pack_fingerprint(*, with_tests: bool = False) -> str:
    """Fingerprint of the pack that install_pack would write (key entry files)."""
    digest = hashlib.sha256()
    for name in REQUIRED_FILES:
        file_path = REPO_ROOT / name
        digest.update(name.encode("utf-8"))
        digest.update(_hash_file(file_path))
    return digest.hexdigest()


def install_pack(
    skills_root: Path,
    *,
    with_tests: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> Path:
    """Copy the pack into skills_root/fef-claude/.

    S4-09: existing dest is preserved unless --force. Identical content hash
    (CLAUDE.md/AGENTS.md/README.md) is skipped without --force. No silent rmtree.
    """
    skills_root = skills_root.expanduser()
    if skills_root.exists() and not skills_root.is_dir():
        raise SystemExit(f"Destination is not a directory: {skills_root}")
    dest = skills_root / PACK_NAME
    items = pack_source_paths(with_tests=with_tests)

    if dry_run:
        return dest

    if dest.exists():
        dest_fp = pack_content_fingerprint(dest)
        src_fp = source_pack_fingerprint(with_tests=with_tests)
        if not force and dest_fp is not None and dest_fp == src_fp:
            # Identical entry files — skip (non-destructive) unless --force.
            return dest
        if not force:
            raise SystemExit(
                f"Refusing to overwrite existing pack at {dest}. "
                "Pass --force to replace, or remove the directory first."
            )
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    def _docs_ignore(directory: str, names: list[str]) -> set[str]:
        """Exclude history/dev docs and subtrees from default install (S3-09)."""
        ignored = set(COPY_IGNORE(directory, names))
        dir_path = Path(directory)
        # When copying the docs/ tree, keep only RUNTIME_DOCS files at top level
        # and drop nested history trees (releases/, reviews/, …).
        try:
            rel = dir_path.relative_to(REPO_ROOT)
        except ValueError:
            return ignored
        if rel == Path("docs"):
            for name in names:
                path = dir_path / name
                if path.is_dir():
                    ignored.add(name)
                elif path.is_file() and name not in RUNTIME_DOCS:
                    ignored.add(name)
        elif rel.parts and rel.parts[0] == "docs":
            # Any nested docs path should already be skipped via dir ignore;
            # belt-and-suspenders: ignore everything under unexpected subtrees.
            ignored.update(names)
        return ignored

    for relative, source in items:
        target = dest / relative
        if source.is_dir():
            ignore = _docs_ignore if relative == "docs" or relative.startswith("docs/") else COPY_IGNORE
            # copytree ignore is called for every directory; use _docs_ignore always
            # so nested docs filters apply, and COPY_IGNORE patterns still apply.
            def _combined(directory: str, names: list[str]) -> set[str]:
                ignored = set(COPY_IGNORE(directory, names))
                ignored |= _docs_ignore(directory, names)
                return ignored
            shutil.copytree(source, target, ignore=_combined)
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
    for name in REQUIRED_VERIFY_FILES:
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
                "measure_load.py",
            ):
                if not (dest_pack / "scripts" / script).is_file():
                    problems.append(f"missing scripts/{script}")
            if not (dest_pack / "scripts" / "lib" / "adaptive_effort.py").is_file():
                problems.append("missing scripts/lib/adaptive_effort.py")
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
            "  python scripts/install_pack.py --auto --dry-run\n"
            "  python scripts/install_pack.py --siblings /other/project\n"
            "  python scripts/install_pack.py --siblings-only --scan-sibling-parent\n"
            "  python scripts/install_pack.py --auto --siblings /other/project\n"
            "  python scripts/install_pack.py --dest ~/.agents/skills --force\n"
            "  python scripts/install_pack.py --print-bootstrap\n"
            "  python scripts/install_pack.py --print-claude\n"
            "  python scripts/install_pack.py --check --dest ~/.agents/skills\n"
            f"\nEnv: {SIBLING_ROOTS_ENV}=path1{os.pathsep}path2 for opt-in sibling roots.\n"
            "     FEF_SIBLING_PARENT=/parent to opt-in parent-dir scan.\n"
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
        f"(fallback: ~/{FALLBACK_SKILLS_DIR}). Sibling install is opt-in "
        "(see --siblings / --siblings-only / --scan-sibling-parent / "
        f"${SIBLING_ROOTS_ENV})",
    )
    parser.add_argument(
        "--siblings",
        action="append",
        metavar="PATH",
        help="Opt-in sibling project root to install into (repeatable; also "
        f"${SIBLING_ROOTS_ENV}). Does not enable parent-dir scan by itself",
    )
    parser.add_argument(
        "--siblings-only",
        action="store_true",
        help="Install only into sibling project skill roots (skip host detection). "
        "Requires --siblings, ${SIBLING_ROOTS_ENV}, and/or --scan-sibling-parent",
    )
    parser.add_argument(
        "--scan-sibling-parent",
        action="store_true",
        help="Opt-in: scan this clone's parent directory for sibling git repos "
        "(default OFF). Also set FEF_SIBLING_PARENT to a path",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow overwriting an existing fef-claude/ pack (default: refuse; "
        "identical entry-file hash is skipped without --force)",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="Print detected install targets (hosts + opt-in siblings) without installing",
    )
    parser.add_argument(
        "--print-claude",
        action="store_true",
        help="Print exact steps to paste CLAUDE.md into Claude Project Instructions",
    )
    parser.add_argument(
        "--print-bootstrap",
        action="store_true",
        help="Print host/sibling install one-liners (sibling install remains opt-in)",
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

    # --siblings without --auto/--siblings-only ⇒ siblings-only install
    if args.siblings and not args.auto and not args.siblings_only:
        args.siblings_only = True
    # --scan-sibling-parent alone ⇒ siblings-only
    if args.scan_sibling_parent and not args.auto and not args.siblings_only and not args.siblings:
        args.siblings_only = True

    if args.print_claude:
        print_claude_steps()
        return 0

    if args.print_bootstrap:
        print_bootstrap()
        return 0

    extra_siblings = parse_sibling_paths(args.siblings)
    want_siblings = bool(
        args.siblings
        or args.siblings_only
        or args.scan_sibling_parent
        or os.environ.get(SIBLING_ROOTS_ENV, "").strip()
        or (
            "FEF_SIBLING_PARENT" in os.environ
            and os.environ.get("FEF_SIBLING_PARENT", "").strip()
        )
    )

    def _sibling_install_targets() -> list[tuple[str, Path, Path]]:
        """Return (label, skills_root, sibling_repo) for opt-in siblings."""
        if not want_siblings:
            return []
        out: list[tuple[str, Path, Path]] = []
        for sibling in discover_sibling_repos(
            extra_roots=extra_siblings,
            scan_sibling_parent=args.scan_sibling_parent,
        ):
            for label, skills_root in sibling_skill_roots(sibling):
                out.append((f"{label} [{sibling.name}]", skills_root, sibling))
        return out

    if args.list_targets:
        if not args.siblings_only:
            targets = detect_targets()
            if targets:
                print("Hosts:")
                for label, tpath in targets:
                    print(f"  {label}: {tpath}")
            else:
                print(f"Hosts: (none) — default ~/{FALLBACK_SKILLS_DIR}")
        sibs = _sibling_install_targets()
        if sibs:
            print("Siblings:")
            for label, skills_root, sibling in sibs:
                print(f"  {label}: {skills_root}  (repo={sibling})")
        else:
            print("Siblings: (none)")
        return 0

    if args.check:
        roots: list[Path] = []
        if args.dest:
            roots.append(Path(args.dest).expanduser() / PACK_NAME)
        elif args.auto or args.siblings_only:
            if not args.siblings_only:
                targets = detect_targets()
                if not targets:
                    targets = [("fallback", Path.home() / FALLBACK_SKILLS_DIR)]
                roots.extend(root / PACK_NAME for _, root in targets)
            for _, skills_root, _ in _sibling_install_targets():
                roots.append(skills_root / PACK_NAME)
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

    if args.auto or args.siblings_only:
        host_summaries: list[str] = []
        sibling_summaries: list[str] = []
        action = "Would install" if args.dry_run else "Installed"

        if not args.siblings_only:
            targets = detect_targets()
            if not targets:
                fallback = Path.home() / FALLBACK_SKILLS_DIR
                print(f"No AI host detected — installing to shared location: {fallback}")
                targets = [("AGENTS.md compatible (fallback)", fallback)]
            for label, root in targets:
                dest = install_pack(
                    root,
                    with_tests=args.with_tests,
                    dry_run=args.dry_run,
                    force=args.force,
                )
                line = f"{action}: {dest}  ({label})"
                print(line)
                host_summaries.append(line)
                if not args.dry_run:
                    problems = verify_install(dest)
                    if problems:
                        print("  problems: " + "; ".join(problems), file=sys.stderr)
                        return 1

        sib_targets = _sibling_install_targets()
        if args.auto and not want_siblings:
            print(
                "Sibling install skipped (opt-in only). "
                f"Use --siblings PATH, ${SIBLING_ROOTS_ENV}, "
                "--siblings-only, or --scan-sibling-parent."
            )
        elif want_siblings and not sib_targets:
            print(
                "No sibling git repos found "
                f"({SIBLING_ROOTS_ENV} / --siblings / --scan-sibling-parent)."
            )
        for label, skills_root, sibling in sib_targets:
            dest = install_pack(
                skills_root,
                with_tests=args.with_tests,
                dry_run=args.dry_run,
                force=args.force,
            )
            line = f"{action}: {dest}  ({label})"
            print(line)
            sibling_summaries.append(line)
            if not args.dry_run:
                problems = verify_install(dest)
                if problems:
                    print("  problems: " + "; ".join(problems), file=sys.stderr)
                    return 1

        print()
        print("Summary:")
        print(f"  Hosts installed: {len(host_summaries)}")
        for line in host_summaries:
            print(f"    {line}")
        print(f"  Siblings installed: {len(sibling_summaries)}")
        for line in sibling_summaries:
            print(f"    {line}")
        print()
        print("Next steps:")
        print(
            "  Claude Code → open the git clone as workspace (loads CLAUDE.md), "
            "or use the installed pack."
        )
        if sibling_summaries:
            print(
                "  Multi-repo → sibling projects now have .claude/skills/fef-claude "
                "(and/or .agents/skills)."
            )
        else:
            print(
                "  Multi-repo → sibling install is opt-in "
                "(--siblings / FEF_SIBLING_ROOTS / --scan-sibling-parent)."
            )
        print("  Claude Projects → python scripts/install_pack.py --print-claude")
        print("  Verify  → python scripts/install_pack.py --check --auto")
        return 0

    root = destination_root(args.dest)
    dest = install_pack(
        root, with_tests=args.with_tests, dry_run=args.dry_run, force=args.force
    )
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
