"""Unit tests for scripts/install_pack.py (detect_targets, dry-run, temp-home install)."""
from __future__ import annotations

import importlib.util
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
            }
        }
        env["HOME"] = env["USERPROFILE"] = str(home or self.home)
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

    def test_with_tests_copies_tests_dir(self):
        dest = self.home / "skills"
        proc = self._run("--dest", str(dest), "--with-tests")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((dest / "fef-claude" / "tests" / "Scorecard.md").is_file())

    def test_idempotent_overwrite(self):
        dest = self.home / "skills"
        first = self._run("--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        marker = dest / "fef-claude" / "EXTRA_SHOULD_GO.txt"
        marker.write_text("stale", encoding="utf-8")
        second = self._run("--dest", str(dest))
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue((dest / "fef-claude" / "CLAUDE.md").is_file())

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
        self.assertIn(".cursor/skills", proc.stdout)
        self.assertFalse((self.home / ".cursor/skills").exists())

    def test_destination_root_requires_config(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaises(SystemExit):
            install_pack.destination_root(None)

    def test_destination_root_explicit_wins(self):
        with patch.dict(os.environ, {"AI_PACK_DIR": "ignored"}, clear=True):
            self.assertEqual(
                install_pack.destination_root(str(self.home / "x")),
                self.home / "x",
            )

    def test_verify_reports_gutted_install(self):
        dest_root = self.home / "skills"
        pack = install_pack.install_pack(dest_root)
        self.assertEqual(install_pack.verify_install(pack), [])
        (pack / "scripts" / "validate_framework.py").unlink()
        problems = install_pack.verify_install(pack)
        self.assertTrue(any("validate_framework.py" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
