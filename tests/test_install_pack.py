"""Unit tests for scripts/install_pack.py (detect_targets, siblings, dry-run, install)."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install_pack.py"


def load_install_pack():
    spec = importlib.util.spec_from_file_location("install_pack_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


install_pack = load_install_pack()


class DetectTargetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_detects_each_host(self):
        cases = (
            (".claude", ".claude/skills"),
            (".codex", ".agents/skills"),
            (".grok", ".grok/skills"),
            (".agents", ".agents/skills"),
            (".cursor", ".cursor/skills"),
        )
        for marker, expected in cases:
            with self.subTest(marker=marker):
                home = Path(tempfile.mkdtemp(dir=self.home))
                (home / marker).mkdir()
                with patch.dict(os.environ, {}, clear=True):
                    targets = install_pack.detect_targets(home)
                self.assertEqual([p for _, p in targets], [home / expected])

    def test_detects_nothing_on_bare_home(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(install_pack.detect_targets(self.home), [])

    def test_env_ai_pack_dir(self):
        pack = self.home / "custom-packs"
        pack.mkdir()
        with patch.dict(os.environ, {"AI_PACK_DIR": str(pack)}, clear=True):
            targets = install_pack.detect_targets(self.home)
        self.assertEqual([p for _, p in targets], [pack.resolve()])

    def test_env_codex_home(self):
        codex = self.home / "codex-home"
        codex.mkdir()
        with patch.dict(os.environ, {"CODEX_HOME": str(codex)}, clear=True):
            targets = install_pack.detect_targets(self.home)
        self.assertEqual([p for _, p in targets], [(codex / "skills").resolve()])

    def test_dedupes_codex_and_agents_marker(self):
        (self.home / ".codex").mkdir()
        (self.home / ".agents").mkdir()
        with patch.dict(os.environ, {}, clear=True):
            targets = install_pack.detect_targets(self.home)
        paths = [p for _, p in targets]
        self.assertEqual(paths, [(self.home / ".agents/skills").resolve()])


class InstallPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def _run(self, *args: str, home: Path | None = None, env_extra: dict | None = None):
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "AI_PACK_DIR",
                "AI_SKILLS_DIR",
                "CURSOR_PACK_DIR",
                "CURSOR_SKILLS_DIR",
                "CODEX_HOME",
                "FEF_SIBLING_ROOTS",
                "FEF_SIBLING_PARENT",
            }
        }
        env["HOME"] = env["USERPROFILE"] = str(home or self.home)
        env["FEF_SIBLING_PARENT"] = ""  # isolate from /workspace siblings
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
            env=env,
        )

    def test_dry_run_auto_does_not_create_files(self):
        (self.home / ".claude").mkdir()
        proc = self._run("--auto", "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Would install", proc.stdout)
        self.assertFalse((self.home / ".claude/skills/fef-claude").exists())

    def test_auto_installs_into_temp_home_hosts(self):
        (self.home / ".claude").mkdir()
        (self.home / ".grok").mkdir()
        proc = self._run("--auto")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        for host in (".claude/skills", ".grok/skills"):
            pack = self.home / host / "fef-claude"
            self.assertTrue((pack / "CLAUDE.md").is_file(), pack)
            self.assertTrue((pack / "AGENTS.md").is_file())
            self.assertTrue((pack / "docs").is_dir())
            self.assertTrue((pack / "kernel").is_dir())
            self.assertTrue((pack / "modules").is_dir())
            self.assertTrue((pack / "scripts" / "validate_framework.py").is_file())
            self.assertTrue((pack / "scripts" / "install_pack.py").is_file())
            self.assertTrue((pack / "SKILL.md").is_file())
            self.assertTrue((pack / "INSTALL_NOTE.md").is_file())
            self.assertFalse((pack / "tests").exists())

    def test_auto_fallback_when_no_host(self):
        proc = self._run("--auto")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("No AI host detected", proc.stdout)
        pack = self.home / ".agents/skills/fef-claude"
        self.assertTrue((pack / "CLAUDE.md").is_file())

    def test_installed_readme_language_links_and_integrity(self):
        dest = self.home / "skills"
        proc = self._run("--dest", str(dest))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        pack = dest / "fef-claude"
        for name in ("README.md", "README.en.md", "README.ko.md"):
            self.assertEqual((pack / name).read_bytes(), (ROOT / name).read_bytes())
        self.assertIn("[English](README.en.md)", (pack / "README.md").read_text(encoding="utf-8"))
        self.assertIn("[한국어](README.md)", (pack / "README.en.md").read_text(encoding="utf-8"))
        self.assertIn("[README.md](README.md)", (pack / "README.ko.md").read_text(encoding="utf-8"))
        self.assertEqual(install_pack.verify_install(pack), [])
        for missing in (False, True):
            with self.subTest(missing=missing):
                english = pack / "README.en.md"
                if missing:
                    english.unlink()
                else:
                    english.write_bytes(english.read_bytes() + b"\nlocal edit\n")
                problems = install_pack.verify_install(pack)
                self.assertTrue(any("README.en.md" in item for item in problems), problems)
                self.assertIsNone(install_pack.pack_content_fingerprint(pack))

    def test_with_tests_copies_tests_dir(self):
        dest = self.home / "skills"
        proc = self._run("--dest", str(dest), "--with-tests")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((dest / "fef-claude" / "tests" / "Scorecard.md").is_file())

    def test_refuse_overwrite_without_force(self):
        dest = self.home / "skills"
        first = self._run("--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = dest / "fef-claude" / "EXTRA_SHOULD_STAY.txt"
        marker.write_text("stale", encoding="utf-8")
        # Mutate an entry file so hash differs from source → must refuse.
        claude = dest / "fef-claude" / "CLAUDE.md"
        claude.write_text(claude.read_text(encoding="utf-8") + "\n# local tweak\n", encoding="utf-8")
        second = self._run("--dest", str(dest))
        self.assertNotEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Refusing to overwrite", second.stderr + second.stdout)
        self.assertTrue(marker.exists())

    def test_force_overwrite(self):
        dest = self.home / "skills"
        first = self._run("--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = dest / "fef-claude" / "EXTRA_SHOULD_GO.txt"
        marker.write_text("stale", encoding="utf-8")
        second = self._run("--dest", str(dest), "--force")
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue((dest / "fef-claude" / "CLAUDE.md").is_file())

    def test_identical_hash_skips_without_force(self):
        dest = self.home / "skills"
        first = self._run("--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        mtime = (dest / "fef-claude" / "CLAUDE.md").stat().st_mtime_ns
        second = self._run("--dest", str(dest))
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual((dest / "fef-claude" / "CLAUDE.md").stat().st_mtime_ns, mtime)

    def test_print_claude_mentions_entry(self):
        proc = self._run("--print-claude")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("CLAUDE.md", proc.stdout)
        self.assertIn("Project Instructions", proc.stdout)

    def test_check_source_tree(self):
        proc = self._run("--check")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("validate OK", proc.stdout)

    def test_check_installed_pack(self):
        dest = self.home / "skills"
        install = self._run("--dest", str(dest))
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        proc = self._run("--check", "--dest", str(dest))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("files OK", proc.stdout)
        self.assertIn("validate skipped", proc.stdout)

    def test_check_installed_pack_with_tests_runs_validate(self):
        dest = self.home / "skills"
        install = self._run("--dest", str(dest), "--with-tests")
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        proc = self._run("--check", "--dest", str(dest))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("files OK", proc.stdout)
        self.assertIn("validate OK", proc.stdout)

    def test_list_targets(self):
        (self.home / ".cursor").mkdir()
        proc = self._run("--list-targets")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        printed = proc.stdout.replace("\\", "/")
        self.assertIn(".cursor/skills", printed)
        self.assertFalse((self.home / ".cursor" / "skills").exists())

    def test_destination_root_requires_config(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit):
            install_pack.destination_root(None)

    def test_destination_root_explicit_wins(self):
        with patch.dict(os.environ, {"AI_PACK_DIR": "ignored"}, clear=True):
            self.assertEqual(
                install_pack.destination_root(str(self.home / "x")),
                self.home / "x",
            )


    def test_default_install_keeps_runtime_docs_only(self):
        dest = self.home / "skills"
        proc = self._run("--dest", str(dest))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        docs = dest / "fef-claude" / "docs"
        names = {p.name for p in docs.iterdir()}
        expected = {
            "loading-map.md",
            "adaptive-effort.md",
            "model-usage.md",
            "context-protocol.md",
            "knowledge-governance.md",
            "Installation.md",
            "FAQ.md",
        }
        self.assertEqual(names, expected)
        self.assertFalse((docs / "releases").exists())
        self.assertFalse((docs / "simulation-round2-2026-09-06.md").exists())

    def test_installed_tree_passes_validate_framework(self):
        dest = self.home / "skills"
        proc = self._run("--dest", str(dest))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        pack = dest / "fef-claude"
        code = install_pack.run_validate(pack)
        self.assertEqual(code, 0)

    def test_verify_reports_gutted_install(self):
        dest_root = self.home / "skills"
        pack = install_pack.install_pack(dest_root)
        self.assertEqual(install_pack.verify_install(pack), [])
        (pack / "scripts" / "validate_framework.py").unlink()
        problems = install_pack.verify_install(pack)
        self.assertTrue(any("validate_framework.py" in p for p in problems))



    def test_check_detects_modified_or_missing_shipped_file(self):
        for relative, missing in (("policies/Evidence.md", False), ("modules/Coding.md", True)):
            with self.subTest(relative=relative):
                dest = self.home / ("missing" if missing else "modified")
                pack = install_pack.install_pack(dest)
                path = pack / relative
                if missing:
                    path.unlink()
                else:
                    path.write_bytes(path.read_bytes() + b"\nlocal edit\n")
                proc = self._run("--check", "--dest", str(dest))
                self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                self.assertIn(relative, proc.stdout)
                self.assertIsNone(install_pack.pack_content_fingerprint(pack))

    def test_installed_script_checks_its_own_manifest(self):
        pack = install_pack.install_pack(self.home / "skills")
        (pack / "modules" / "Coding.md").unlink()
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", str(pack / "scripts" / "install_pack.py"), "--check"],
            cwd=str(pack), capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "AI_PACK_DIR": "", "AI_SKILLS_DIR": "",
                 "CURSOR_PACK_DIR": "", "CURSOR_SKILLS_DIR": "", "CODEX_HOME": ""},
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("modules/Coding.md", proc.stdout)


class PackIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / "source"
        self.source.mkdir()
        for name in install_pack.REQUIRED_DIRS:
            (self.source / name).mkdir()
        files = set(install_pack.REQUIRED_FILES + install_pack.REQUIRED_VERIFY_FILES)
        files.update(f"scripts/{name}" for name in (
            "validate_framework.py", "sync_kernel.py", "install_pack.py", "detect_task.py"
        ))
        files.update(("policies/Evidence.md", "modules/Coding.md", "config/routes.json",
                      ".claude/hooks/check.py", "docs/loading-map.md"))
        for name in files:
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"fixture: {name}\n", encoding="utf-8")
        patcher = patch.object(install_pack, "REPO_ROOT", self.source)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.skills = self.root / "skills"

    def test_policy_only_change_refuses_without_force_then_updates(self):
        pack = install_pack.install_pack(self.skills)
        old_fp = install_pack.source_pack_fingerprint()
        policy = self.source / "policies" / "Evidence.md"
        policy.write_bytes(policy.read_bytes() + b"changed\n")
        self.assertNotEqual(install_pack.source_pack_fingerprint(), old_fp)
        with patch("sys.stdout"):
            self.assertEqual(install_pack.main(["--check", "--dest", str(self.skills)]), 1)
        with self.assertRaisesRegex(SystemExit, "Refusing to overwrite"):
            install_pack.install_pack(self.skills)
        self.assertNotEqual((pack / "policies" / "Evidence.md").read_bytes(), policy.read_bytes())
        install_pack.install_pack(self.skills, force=True)
        self.assertEqual((pack / "policies" / "Evidence.md").read_bytes(), policy.read_bytes())
        self.assertEqual(install_pack.verify_install(pack), [])

    def test_hook_route_and_module_only_changes_affect_fingerprint(self):
        for relative in (".claude/hooks/check.py", "config/routes.json", "modules/Coding.md"):
            with self.subTest(relative=relative):
                before = install_pack.source_pack_fingerprint()
                path = self.source / relative
                path.write_bytes(path.read_bytes() + b"changed\n")
                self.assertNotEqual(install_pack.source_pack_fingerprint(), before)

    def test_unchanged_source_skips_and_unshipped_files_do_not_churn(self):
        pack = install_pack.install_pack(self.skills)
        fp = install_pack.source_pack_fingerprint()
        mtime = (pack / "CLAUDE.md").stat().st_mtime_ns
        for relative in ("PROGRESS.md", "docs/development.md", "scripts/__pycache__/cached.pyc",
                         "docs/reviews/history.md", "tests/dev.py",
                         ".claude/.verification/private-session.json", ".claude/.test-run-marker"):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"unshipped changes\n")
        self.assertEqual(install_pack.source_pack_fingerprint(), fp)
        self.assertEqual(install_pack.pack_content_fingerprint(pack), fp)
        self.assertEqual(install_pack.install_pack(self.skills), pack)
        self.assertEqual((pack / "CLAUDE.md").stat().st_mtime_ns, mtime)
        self.assertFalse((pack / "docs" / "development.md").exists())
        self.assertFalse((pack / ".claude" / ".verification").exists())

    def test_with_tests_option_is_part_of_fingerprint(self):
        pack = install_pack.install_pack(self.skills)
        (self.source / "tests").mkdir()
        (self.source / "tests" / "test_runtime.py").write_bytes(b"test content\n")
        self.assertNotEqual(install_pack.source_pack_fingerprint(with_tests=True),
                            install_pack.source_pack_fingerprint())
        with self.assertRaisesRegex(SystemExit, "Refusing to overwrite"):
            install_pack.install_pack(self.skills, with_tests=True)
        install_pack.install_pack(self.skills, with_tests=True, force=True)
        self.assertTrue((pack / "tests" / "test_runtime.py").is_file())
        self.assertEqual(install_pack.pack_content_fingerprint(pack),
                         install_pack.source_pack_fingerprint(with_tests=True))

    def test_legacy_install_requires_explicit_reinstall(self):
        pack = install_pack.install_pack(self.skills)
        (pack / install_pack.MANIFEST_FILE).unlink()
        marker = pack / "KEEP.txt"
        marker.write_bytes(b"keep\n")
        self.assertIn("legacy install", "; ".join(install_pack.verify_install(pack)))
        with self.assertRaisesRegex(SystemExit, "Refusing to overwrite"):
            install_pack.install_pack(self.skills)
        self.assertEqual(marker.read_bytes(), b"keep\n")
        install_pack.install_pack(self.skills, force=True)
        self.assertEqual(install_pack.verify_install(pack), [])

    def test_generated_files_are_verified(self):
        pack = install_pack.install_pack(self.skills)
        (pack / "SKILL.md").write_bytes(b"modified hint\n")
        self.assertIn("modified file: SKILL.md", install_pack.verify_install(pack))
        self.assertIsNone(install_pack.pack_content_fingerprint(pack))

    def test_directory_symlink_contents_match_copy_policy(self):
        linked = self.root / "linked"
        linked.mkdir()
        (linked / "policy.md").write_bytes(b"linked content\n")
        try:
            (self.source / "policies" / "linked").symlink_to(linked, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlinks unavailable: {exc}")
        pack = install_pack.install_pack(self.skills)
        self.assertEqual(install_pack.pack_content_fingerprint(pack),
                         install_pack.source_pack_fingerprint())
        self.assertFalse((pack / "policies" / "linked").is_symlink())
        (pack / "policies" / "linked" / "policy.md").write_bytes(b"modified\n")
        self.assertIn("modified file: policies/linked/policy.md", install_pack.verify_install(pack))

    def test_installed_symlink_cannot_reference_external_file(self):
        pack = install_pack.install_pack(self.skills)
        policy = pack / "policies" / "Evidence.md"
        outside = self.root / "outside.md"
        outside.write_bytes(policy.read_bytes())
        policy.unlink()
        try:
            policy.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"file symlinks unavailable: {exc}")
        self.assertIn("file escapes pack directory: policies/Evidence.md",
                      install_pack.verify_install(pack))
        self.assertIsNone(install_pack.pack_content_fingerprint(pack))

    def test_invalid_manifest_paths_and_versions_are_rejected(self):
        pack = install_pack.install_pack(self.skills)
        path = pack / install_pack.MANIFEST_FILE
        original = json.loads(path.read_text(encoding="utf-8"))
        for name in ("../outside", "/absolute", "C:/absolute", "bad\\path", "foo//bar",
                     "foo/./bar", "foo/../../bar"):
            with self.subTest(name=name):
                manifest = {**original, "files": {**original["files"], name: "0" * 64}}
                path.write_text(json.dumps(manifest), encoding="utf-8")
                self.assertIn("invalid integrity manifest", "; ".join(install_pack.verify_install(pack)))
                self.assertIsNone(install_pack.pack_content_fingerprint(pack))
        path.write_text(json.dumps({**original, "version": 2}), encoding="utf-8")
        self.assertIn("invalid integrity manifest", "; ".join(install_pack.verify_install(pack)))


class SiblingDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        # Fake this-clone + siblings under a shared parent
        self.parent = self.root / "workspace"
        self.parent.mkdir()
        self.claude = self.parent / "claude"
        self.claude.mkdir()
        (self.claude / ".git").mkdir()
        self.proj_a = self.parent / "proj-a"
        self.proj_a.mkdir()
        (self.proj_a / ".git").mkdir()
        self.proj_b = self.parent / "proj-b"
        self.proj_b.mkdir()
        (self.proj_b / ".git").mkdir()
        (self.proj_b / ".claude").mkdir()
        self.not_git = self.parent / "notes"
        self.not_git.mkdir()

    def test_discovers_sibling_git_repos_excludes_self(self):
        found = install_pack.discover_sibling_repos(
            repo_root=self.claude, parent=self.parent
        )
        self.assertEqual(found, [self.proj_a.resolve(), self.proj_b.resolve()])

    def test_default_does_not_scan_parent(self):
        """S4-09: parent-dir scan is OFF unless opted in."""
        found = install_pack.discover_sibling_repos(repo_root=self.claude)
        self.assertEqual(found, [])

    def test_scan_sibling_parent_flag(self):
        found = install_pack.discover_sibling_repos(
            repo_root=self.claude, scan_sibling_parent=True
        )
        self.assertEqual(found, [self.proj_a.resolve(), self.proj_b.resolve()])

    def test_no_siblings_does_not_crash(self):
        alone_parent = self.root / "alone-parent"
        alone_parent.mkdir()
        alone = alone_parent / "claude"
        alone.mkdir()
        (alone / ".git").mkdir()
        found = install_pack.discover_sibling_repos(repo_root=alone, parent=alone_parent)
        self.assertEqual(found, [])

    def test_env_fef_sibling_roots(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (elsewhere / ".git").mkdir()
        with patch.dict(
            os.environ,
            {"FEF_SIBLING_ROOTS": str(elsewhere)},
            clear=False,
        ):
            # Clear parent scan by using empty parent with only self
            empty = self.root / "empty-parent"
            empty.mkdir()
            only = empty / "claude"
            only.mkdir()
            (only / ".git").mkdir()
            found = install_pack.discover_sibling_repos(
                repo_root=only, parent=empty
            )
        self.assertEqual(found, [elsewhere.resolve()])

    def test_extra_roots_argument(self):
        extra = self.root / "extra-proj"
        extra.mkdir()
        (extra / ".git").mkdir()
        empty = self.root / "empty2"
        empty.mkdir()
        only = empty / "claude"
        only.mkdir()
        (only / ".git").mkdir()
        found = install_pack.discover_sibling_repos(
            repo_root=only, parent=empty, extra_roots=[extra]
        )
        self.assertEqual(found, [extra.resolve()])

    def test_file_git_counts_as_repo(self):
        linked = self.parent / "worktree-style"
        linked.mkdir()
        (linked / ".git").write_text("gitdir: /tmp/fake", encoding="utf-8")
        found = install_pack.discover_sibling_repos(
            repo_root=self.claude, parent=self.parent
        )
        self.assertIn(linked.resolve(), found)

    def test_sibling_skill_roots_markers(self):
        # bare git → .claude/skills
        roots = install_pack.sibling_skill_roots(self.proj_a)
        self.assertEqual(
            [p for _, p in roots],
            [(self.proj_a / ".claude" / "skills").absolute()],
        )
        # .claude present → .claude/skills
        roots_b = install_pack.sibling_skill_roots(self.proj_b)
        self.assertEqual(
            [p for _, p in roots_b],
            [(self.proj_b / ".claude" / "skills").absolute()],
        )
        # AGENTS.md → .agents/skills (+ bare git also .claude/skills via has_git fallback
        # only when no other roots — here AGENTS.md alone with .git → both)
        proj_c = self.parent / "proj-c"
        proj_c.mkdir()
        (proj_c / ".git").mkdir()
        (proj_c / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
        roots_c = install_pack.sibling_skill_roots(proj_c)
        paths = [p for _, p in roots_c]
        self.assertIn((proj_c / ".agents" / "skills").absolute(), paths)
        # With only AGENTS.md + .git, .claude is NOT auto-added because agents root exists
        self.assertEqual(len(paths), 1)

    def test_sibling_skill_roots_cursor(self):
        proj = self.parent / "cursor-app"
        proj.mkdir()
        (proj / ".git").mkdir()
        (proj / ".cursor").mkdir()
        roots = install_pack.sibling_skill_roots(proj)
        self.assertEqual(
            [p for _, p in roots],
            [(proj / ".claude" / "skills").absolute()],
        )


class SiblingInstallCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name) / "home"
        self.home.mkdir()
        self.parent = Path(self.temp.name) / "ws"
        self.parent.mkdir()
        self.addCleanup(self.temp.cleanup)
        # Place a fake clone layout: we invoke the REAL script (REPO_ROOT=actual),
        # so sibling discovery uses real REPO_ROOT.parent unless we pass --siblings.
        self.sib = self.parent / "app"
        self.sib.mkdir()
        (self.sib / ".git").mkdir()
        (self.sib / ".claude").mkdir()

    def _run(self, *args: str, env_extra: dict | None = None):
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "AI_PACK_DIR",
                "AI_SKILLS_DIR",
                "CURSOR_PACK_DIR",
                "CURSOR_SKILLS_DIR",
                "CODEX_HOME",
                "FEF_SIBLING_ROOTS",
                "FEF_SIBLING_PARENT",
            }
        }
        env["HOME"] = env["USERPROFILE"] = str(self.home)
        env["FEF_SIBLING_PARENT"] = ""  # isolate from /workspace siblings
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
            env=env,
        )

    def test_siblings_only_dry_run(self):
        proc = self._run("--siblings-only", "--siblings", str(self.sib), "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Would install", proc.stdout)
        self.assertIn("Siblings installed:", proc.stdout)
        self.assertIn("Hosts installed: 0", proc.stdout)
        self.assertFalse((self.sib / ".claude" / "skills" / "fef-claude").exists())

    def test_siblings_only_installs_pack(self):
        proc = self._run("--siblings-only", "--siblings", str(self.sib))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        pack = self.sib / ".claude" / "skills" / "fef-claude"
        self.assertTrue((pack / "CLAUDE.md").is_file(), proc.stdout)
        self.assertTrue((pack / "SKILL.md").is_file())
        self.assertIn("Siblings installed: 1", proc.stdout)

    def test_auto_with_explicit_sibling_dry_run(self):
        (self.home / ".claude").mkdir()
        proc = self._run("--auto", "--siblings", str(self.sib), "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Hosts installed:", proc.stdout)
        self.assertIn("Siblings installed:", proc.stdout)
        self.assertIn("Would install", proc.stdout)

    def test_print_bootstrap(self):
        proc = self._run("--print-bootstrap")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("install_pack.py --auto", proc.stdout)

    def test_list_targets_includes_siblings(self):
        proc = self._run("--list-targets", "--siblings", str(self.sib))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Siblings:", proc.stdout)
        self.assertIn(str(self.sib), proc.stdout)

    def test_agents_md_sibling_gets_agents_skills(self):
        agents_sib = self.parent / "agents-app"
        agents_sib.mkdir()
        (agents_sib / ".git").mkdir()
        (agents_sib / "AGENTS.md").write_text("# x\n", encoding="utf-8")
        proc = self._run("--siblings-only", "--siblings", str(agents_sib))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(
            (agents_sib / ".agents" / "skills" / "fef-claude" / "CLAUDE.md").is_file()
        )


class Round4InstallSafetyTests(unittest.TestCase):
    """S4-09: --auto hosts-only; no silent sibling write; refuse overwrite."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.home = self.root / "home"
        self.home.mkdir()
        (self.home / ".claude").mkdir()
        self.parent = self.root / "workspace"
        self.parent.mkdir()
        # Simulate multi-repo parent: claude + 3 unrelated git repos
        self.claude = self.parent / "claude"
        self.claude.mkdir()
        (self.claude / ".git").mkdir()
        self.unrelated = []
        for name in ("alpha", "beta", "gamma"):
            repo = self.parent / name
            repo.mkdir()
            (repo / ".git").mkdir()
            (repo / ".claude").mkdir()
            self.unrelated.append(repo)

    def _run(self, *args: str, env_extra: dict | None = None):
        env = {
            k: v
            for k, v in os.environ.items()
            if k
            not in {
                "AI_PACK_DIR",
                "AI_SKILLS_DIR",
                "CURSOR_PACK_DIR",
                "CURSOR_SKILLS_DIR",
                "CODEX_HOME",
                "FEF_SIBLING_ROOTS",
                "FEF_SIBLING_PARENT",
            }
        }
        env["HOME"] = env["USERPROFILE"] = str(self.home)
        # Isolate from /workspace; do not enable parent scan via env.
        if env_extra:
            env.update(env_extra)
        return subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(ROOT),
            env=env,
        )

    def test_auto_does_not_write_unrelated_siblings(self):
        proc = self._run("--auto")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((self.home / ".claude/skills/fef-claude/CLAUDE.md").is_file())
        for repo in self.unrelated:
            pack = repo / ".claude" / "skills" / "fef-claude"
            self.assertFalse(pack.exists(), f"--auto wrote sibling {repo}")
        self.assertIn("Sibling install skipped", proc.stdout)

    def test_siblings_path_installs_only_there(self):
        target = self.unrelated[0]
        others = self.unrelated[1:]
        proc = self._run("--siblings", str(target))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(
            (target / ".claude" / "skills" / "fef-claude" / "CLAUDE.md").is_file()
        )
        for repo in others:
            self.assertFalse(
                (repo / ".claude" / "skills" / "fef-claude").exists(),
                f"unexpected install into {repo}",
            )

    def test_existing_dest_unchanged_without_force(self):
        dest = self.home / "skills"
        first = self._run("--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = dest / "fef-claude" / "KEEP.txt"
        marker.write_text("keep-me", encoding="utf-8")
        claude = dest / "fef-claude" / "CLAUDE.md"
        claude.write_text(claude.read_text(encoding="utf-8") + "\nX\n", encoding="utf-8")
        before = marker.read_text(encoding="utf-8")
        second = self._run("--dest", str(dest))
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), before)



if __name__ == "__main__":
    unittest.main()
