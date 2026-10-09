#!/usr/bin/env python3
"""Install or package the ai-delegation-loop skill.

Standard library only, Python 3.9+. Writes only to the paths named on the
command line: no parent-directory scan, no other repositories. An existing
installation that differs from the source is never overwritten without --force,
and --force moves it to a backup folder outside the skill search path.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

SKILL = "ai-delegation-loop"
REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "skills" / SKILL
TARGET_DIRS = {"claude": ".claude", "codex": ".agents", "grok": ".grok"}
SKIP_DIRS = {"__pycache__", ".git", ".simulation"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
SKIP_SUFFIXES = {".pyc"}

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")


def say(message):
    print(message, flush=True)


def files_in(root):
    refuse_links(root)
    found = []
    for path in root.rglob("*"):
        if is_link(path):
            raise ValueError("REFUSED: symbolic link or reparse point in package")
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts) or path.is_dir():
            continue
        if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
            continue
        found.append(rel)
    return sorted(found, key=lambda rel: rel.as_posix())


def is_link(path):
    return path.is_symlink() or bool(getattr(path.lstat(), "st_file_attributes", 0)
                                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def refuse_links(path):
    for item in [path] + list(path.parents):
        if (item.exists() or item.is_symlink()) and is_link(item):
            raise ValueError("REFUSED: symbolic link or reparse point in destination ancestry")


def file_hashes(root):
    return {rel.as_posix(): hashlib.sha256((root / rel).read_bytes()).hexdigest()
            for rel in files_in(root)}


def digest(root):
    outer = hashlib.sha256()
    for name, value in sorted(file_hashes(root).items()):
        outer.update(name.encode("utf-8") + b"\0" + value.encode("ascii") + b"\n")
    return outer.hexdigest()


def diff_summary(src, dst):
    a, b = file_hashes(src), file_hashes(dst)
    added = sorted(set(a) - set(b))
    removed = sorted(set(b) - set(a))
    changed = sorted(name for name in a if name in b and a[name] != b[name])
    return added, removed, changed


def install_one(target, base, force, dry_run):
    root = base / TARGET_DIRS[target]
    dest = root / "skills" / SKILL
    say("[%s] %s" % (target, dest))
    return install_to(root / "skills", force, dry_run)


def install_to(skills_root, force=False, dry_run=False):
    if not (SOURCE / "SKILL.md").is_file():
        say("REFUSED: canonical skill source is missing")
        return False
    skills_root = Path(skills_root).expanduser().absolute()
    root = skills_root.parent
    dest = skills_root / SKILL
    try:
        refuse_links(dest)
        refuse_links(root / ".backups")
        refuse_links(root / ".staging")
        files_in(SOURCE)
    except ValueError as error:
        say(str(error))
        return False
    backup = None
    if dest.exists():
        if not dest.is_dir():
            say("  REFUSED: destination exists and is not a directory")
            return False
        try:
            installed_digest = digest(dest)
        except ValueError as error:
            say(str(error))
            return False
        if installed_digest == digest(SOURCE):
            say("  up to date, nothing written")
            return True
        added, removed, changed = diff_summary(SOURCE, dest)
        say("  differs from source: %d added, %d removed, %d changed"
            % (len(added), len(removed), len(changed)))
        if not force:
            say("  REFUSED: re-run with --force to replace it "
                "(the old copy is moved to a backup folder, not deleted)")
            return False
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = root / ".backups" / ("%s-%s" % (SKILL, stamp))
        if backup.exists() or backup.is_symlink():
            say("REFUSED: backup destination already exists")
            return False
    count = len(files_in(SOURCE))
    if dry_run:
        extra = " and move the old copy to %s" % backup if backup else ""
        say("  DRY RUN: would copy %d files%s" % (count, extra))
        return True
    staging_root = root / ".staging"
    staging_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=SKILL + "-", dir=staging_root))
    for rel in files_in(SOURCE):
        out = stage / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / rel, out)
    if digest(stage) != digest(SOURCE):
        shutil.rmtree(stage)
        say("  FAILED: staged copy does not match the source; nothing was changed")
        return False
    skills_root.mkdir(parents=True, exist_ok=True)
    if backup is not None:
        backup.parent.mkdir(parents=True, exist_ok=True)
        os.replace(str(dest), str(backup))
        say("  old copy moved to %s" % backup)
    os.replace(str(stage), str(dest))
    try:
        stage.parent.rmdir()
    except OSError:
        pass
    if digest(dest) != digest(SOURCE):
        say("  FAILED: installed copy does not match the source")
        return False
    say("  installed %d files" % count)
    return True


def install(args):
    if args.scope == "project":
        if not args.project_dir:
            say("error: --scope project needs --project-dir")
            return 2
        base = Path(args.project_dir).expanduser().absolute()
        if not base.is_dir():
            say("error: --project-dir is not a directory: %s" % base)
            return 2
        if base.resolve() == REPO:
            say("error: refusing to install into this repository itself")
            return 2
    else:
        if args.project_dir:
            say("error: --project-dir is only valid with --scope project")
            return 2
        base = Path.home()
    if not (SOURCE / "SKILL.md").is_file():
        say("error: skill source not found: %s" % SOURCE)
        return 2
    targets = list(dict.fromkeys(args.target))
    results = [install_one(t, base, args.force, args.dry_run) for t in targets]
    if args.scope == "user" and "grok" in targets and len(targets) > 1:
        say("note: Grok Build also scans ~/.agents/skills and Claude Code skills; "
            "check its '/' menu for a duplicate entry and drop the extra copy if it lists twice.")
    if args.scope == "project":
        say("note: the installed folder is untracked in that project; commit or ignore it deliberately.")
    say("done" if all(results) else "finished with refusals or failures")
    return 0 if all(results) else 2


def package(args):
    if not (SOURCE / "SKILL.md").is_file():
        say("REFUSED: canonical skill source is missing")
        return 2
    out = Path(args.output).expanduser().absolute()
    refuse_links(out)
    files_in(SOURCE)
    if out.exists() and not args.force:
        say("REFUSED: %s exists; re-run with --force to replace it" % out)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=out.name + ".", suffix=".tmp", dir=out.parent)
    os.close(fd)
    tmp = Path(tmp_name)
    with zipfile.ZipFile(str(tmp), "w", zipfile.ZIP_DEFLATED) as archive:
        for rel in files_in(SOURCE):
            info = zipfile.ZipInfo("%s/%s" % (SKILL, rel.as_posix()), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, (SOURCE / rel).read_bytes())
    with zipfile.ZipFile(str(tmp)) as archive:
        names = archive.namelist()
    if SKILL + "/SKILL.md" not in names or any(not n.startswith(SKILL + "/") for n in names):
        tmp.unlink()
        say("FAILED: archive layout is wrong; nothing was written")
        return 2
    os.replace(str(tmp), str(out))
    say("wrote %s (%d files, top-level folder %s/)" % (out, len(names), SKILL))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install or package the %s skill." % SKILL)
    sub = parser.add_subparsers(dest="command", required=True)
    inst = sub.add_parser("install", help="copy the skill into a tool's skill folder")
    inst.add_argument("--target", nargs="+", required=True, choices=sorted(TARGET_DIRS))
    inst.add_argument("--scope", required=True, choices=["user", "project"])
    inst.add_argument("--project-dir", help="work project root; required with --scope project")
    inst.add_argument("--force", action="store_true", help="replace a differing install after backing it up")
    inst.add_argument("--dry-run", action="store_true", help="print the plan and write nothing")
    inst.set_defaults(func=install)
    pack = sub.add_parser("package", help="build a ZIP for web/app skill upload")
    pack.add_argument("--output", default=str(REPO / "dist" / (SKILL + ".zip")))
    pack.add_argument("--force", action="store_true", help="replace an existing ZIP")
    pack.set_defaults(func=package)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValueError as error:
        say(str(error))
        sys.exit(2)
