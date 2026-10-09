"""Tests for scripts/install.py and scripts/validate_skill.py.

Each validator guard is exercised by breaking it in a throwaway copy of the
repository and checking that the matching check fails.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import importlib.util

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[1]
VALIDATE = SCRIPTS / "validate_skill.py"
SKILL = "ai-delegation-loop"
SKILL_DIR = Path("skills") / SKILL


def run(script, *args, env=None, flags=()):
    full = dict(os.environ)
    if env:
        full.update(env)
    proc = subprocess.run([sys.executable] + list(flags) + [str(script)] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=full)
    return proc.returncode, proc.stdout + proc.stderr


def copy_repo(dest):
    dest.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(REPO / SKILL_DIR, dest / SKILL_DIR, ignore=ignore)
    shutil.copytree(SCRIPTS, dest / "scripts" / "delegation", ignore=ignore)
    for name in ("AGENTS.md", "CLAUDE.md"):
        shutil.copy2(REPO / name, dest / name)
    return Path(dest)


def edit(path, func):
    path.write_bytes(func(path.read_bytes().decode("utf-8")).encode("utf-8"))


def tree(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = copy_repo(Path(self._tmp.name) / "repo")
        self.skill = self.root / SKILL_DIR

    def validate(self, *extra):
        # -S hides site-packages, so PyYAML cannot mask a missing guard in the built-in parser.
        return run(VALIDATE, "--root", str(self.root), *extra, flags=("-S",))

    def assert_fails(self, check):
        code, out = self.validate()
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL " + check, out)

    def test_repository_passes(self):
        code, out = run(VALIDATE)
        self.assertEqual(code, 0, out)
        self.assertIn("validation passed", out)

    def test_pyyaml_cross_check_agrees_on_real_files(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")
        code, out = run(VALIDATE)
        self.assertEqual(code, 0, out)

    def test_unsupported_frontmatter_key(self):
        edit(self.skill / "SKILL.md", lambda t: t.replace("metadata:", 'x-custom: "value"\nmetadata:', 1))
        self.assert_fails("frontmatter")
        self.assertIn("unsupported frontmatter keys x-custom", self.validate()[1])

    def test_name_must_match_folder(self):
        edit(self.skill / "SKILL.md", lambda t: t.replace("name: ai-delegation-loop", "name: other-name", 1))
        self.assert_fails("frontmatter")

    def test_description_over_limit(self):
        edit(self.skill / "SKILL.md", lambda t: t.replace("description: ", "description: " + "a" * 1100 + " ", 1))
        self.assert_fails("frontmatter")

    def test_unquoted_colon_breaks_yaml(self):
        edit(self.skill / "SKILL.md", lambda t: t.replace("description: Build", "description: Build: x", 1))
        self.assert_fails("frontmatter")

    def test_template_description_must_be_a_string(self):
        path = self.skill / "templates" / "job-playbook" / "SKILL.template.md"
        edit(path, lambda t: t.replace('description: "[', "description: [", 1).replace(']"\n', "]\n", 1))
        self.assert_fails("frontmatter")
        self.assertIn("unsupported YAML construct", self.validate()[1])

    def test_broken_anchor_and_missing_file(self):
        edit(self.skill / "README.md", lambda t: t.replace("#1-어떤-일을-고를까", "#no-such-heading", 1))
        self.assert_fails("links")
        edit(self.skill / "README.md", lambda t: t.replace("installation.ko.md", "missing.ko.md", 1))
        code, out = self.validate()
        self.assertIn("broken link", out)

    def test_stale_evidence_fails_and_can_be_downgraded(self):
        edit(self.skill / "SKILL.md", lambda t: t + "\n추가 문장.\n")
        self.assert_fails("evidence")
        code, out = self.validate("--allow-stale-evidence")
        self.assertEqual(code, 0, out)
        self.assertIn("WARN evidence", out)

    def test_crlf_checkout_does_not_trip_evidence(self):
        for path in list((self.skill / "prompts").glob("*.md")) + [self.skill / "manual.ko.md"]:
            edit(path, lambda t: t.replace("\n", "\r\n"))
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def test_version_mismatch(self):
        edit(self.skill / "README.md", lambda t: t.replace("v1.2", "v9.9"))
        self.assert_fails("version")

    def test_leak_patterns(self):
        samples = ["C:" + "\\Users\\" + "alice\\notes",
                   "ghp_" + "a" * 36,
                   "alice" + "@" + "example.com",
                   "/" + "home" + "/alice/work"]
        for sample in samples:
            note = self.skill / "leak.md"
            note.write_bytes(("# note\n" + sample + "\n").encode("utf-8"))
            code, out = self.validate()
            self.assertEqual(code, 1, sample)
            self.assertIn("FAIL leaks", out)
        note.unlink()
        code, out = self.validate()
        self.assertEqual(code, 0, out)

    def test_openai_yaml_unknown_keys(self):
        path = self.skill / "agents" / "openai.yaml"
        edit(path, lambda t: t.rstrip("\n") + "\n  bogus: \"x\"\n")
        self.assert_fails("openai-yaml")

    def test_root_entry_must_exist_but_keeps_fef_contract(self):
        (self.root / "CLAUDE.md").unlink()
        self.assert_fails("agent-files")

    def test_invalid_json(self):
        (self.skill / "tests" / "simulation-cases.json").write_bytes(b"[{")
        self.assert_fails("json")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.env = {"HOME": str(self.home), "USERPROFILE": str(self.home)}
        self.source = REPO / SKILL_DIR

    def install(self, *args):
        return run(SCRIPTS / "install.py", "install", *args, env=self.env)

    def test_install_is_idempotent_and_exact(self):
        code, out = self.install("--target", "claude", "codex", "grok", "--scope", "user")
        self.assertEqual(code, 0, out)
        expected = {k: v for k, v in tree(self.source).items() if "__pycache__" not in k}
        for folder in (".claude", ".agents", ".grok"):
            dest = self.home / folder / "skills" / SKILL
            self.assertEqual(tree(dest), expected, folder)
            self.assertFalse((self.home / folder / ".staging").exists(), folder)
        self.assertIn("Grok Build also scans", out)
        code, out = self.install("--target", "claude", "codex", "grok", "--scope", "user")
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("up to date"), 3, out)

    def test_divergent_install_needs_force_and_is_backed_up(self):
        self.install("--target", "claude", "--scope", "user")
        dest = self.home / ".claude" / "skills" / SKILL
        (dest / "SKILL.md").write_bytes(b"local edit\n")
        code, out = self.install("--target", "claude", "--scope", "user")
        self.assertEqual(code, 2, out)
        self.assertIn("REFUSED", out)
        self.assertEqual((dest / "SKILL.md").read_bytes(), b"local edit\n")
        code, out = self.install("--target", "claude", "--scope", "user", "--force")
        self.assertEqual(code, 0, out)
        self.assertEqual((dest / "SKILL.md").read_bytes(), (self.source / "SKILL.md").read_bytes())
        backups = list((self.home / ".claude" / ".backups").glob(SKILL + "-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "SKILL.md").read_bytes(), b"local edit\n")
        self.assertFalse(any(p.name == "SKILL.md" for p in (self.home / ".claude" / "skills").iterdir()))

    def test_dry_run_writes_nothing(self):
        code, out = self.install("--target", "claude", "--scope", "user", "--dry-run")
        self.assertEqual(code, 0, out)
        self.assertIn("DRY RUN", out)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_scope_and_project_dir_rules(self):
        project = self.tmp / "project"
        project.mkdir()
        self.assertEqual(self.install("--target", "codex", "--scope", "project")[0], 2)
        self.assertEqual(self.install("--target", "codex", "--scope", "user", "--project-dir", str(project))[0], 2)
        self.assertEqual(self.install("--target", "codex", "--scope", "project", "--project-dir", str(REPO))[0], 2)
        self.assertFalse((REPO / ".agents").exists())
        self.assertEqual(self.install("--target", "codex", "--scope", "project", "--project-dir", str(self.tmp / "nope"))[0], 2)
        code, out = self.install("--target", "codex", "--scope", "project", "--project-dir", str(project))
        self.assertEqual(code, 0, out)
        self.assertTrue((project / ".agents" / "skills" / SKILL / "SKILL.md").is_file())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_symlink_destination_refused(self):
        target = self.tmp / "elsewhere"
        target.mkdir()
        link = self.home / ".claude" / "skills" / SKILL
        link.parent.mkdir(parents=True)
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        code, out = self.install("--target", "claude", "--scope", "user", "--force")
        self.assertEqual(code, 2, out)
        self.assertEqual(list(target.iterdir()), [])

    def test_parent_and_nested_symlinks_refused(self):
        target = self.tmp / "elsewhere"
        target.mkdir()
        link = self.home / ".claude"
        try:
            os.symlink(str(target), str(link), target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        code, out = self.install("--target", "claude", "--scope", "user", "--force")
        self.assertEqual(code, 2, out)
        self.assertEqual(list(target.iterdir()), [])
        link.unlink()
        self.install("--target", "claude", "--scope", "user")
        dest = self.home / ".claude" / "skills" / SKILL
        os.symlink(str(target), str(dest / "linked"), target_is_directory=True)
        self.assertEqual(self.install("--target", "claude", "--scope", "user", "--force")[0], 2)

    def test_link_guard_without_os_symlink_privilege(self):
        spec = importlib.util.spec_from_file_location("installer_guard", SCRIPTS / "install.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ancestor = self.home / ".claude"
        ancestor.mkdir()
        with patch.object(module, "is_link", side_effect=lambda p: p == ancestor):
            self.assertFalse(module.install_to(ancestor / "skills", force=True))
        self.assertEqual(list(ancestor.iterdir()), [])

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_windows_junction_parent_refused(self):
        target = self.tmp / "elsewhere"
        target.mkdir()
        link = self.home / ".claude"
        env = dict(os.environ, DELEGATION_TEST_LINK=str(link), DELEGATION_TEST_TARGET=str(target))
        result = subprocess.run(["powershell", "-NoProfile", "-Command",
                                 "New-Item -ItemType Junction -Path $env:DELEGATION_TEST_LINK -Target $env:DELEGATION_TEST_TARGET | Out-Null"],
                                env=env, capture_output=True)
        self.assertEqual(result.returncode, 0)
        try:
            code, out = self.install("--target", "claude", "--scope", "user", "--force")
            self.assertEqual(code, 2, out)
            self.assertEqual(list(target.iterdir()), [])
        finally:
            link.rmdir()

    def test_explicit_pack_installs_beside_fef_and_preserves_it(self):
        skills = self.home / "skills"
        fef = skills / "fef-claude"
        fef.mkdir(parents=True)
        (fef / "user-edit.md").write_bytes(b"keep me")
        script = REPO / "scripts" / "install_pack.py"
        before = tree(self.home)
        code, out = run(script, "--pack", SKILL, "--dest", str(skills), "--dry-run", env=self.env)
        self.assertEqual(code, 0, out)
        self.assertEqual(tree(self.home), before)
        code, out = run(script, "--pack", SKILL, "--dest", str(skills), env=self.env)
        self.assertEqual(code, 0, out)
        self.assertEqual(tree(fef), {"user-edit.md": b"keep me"})
        self.assertEqual(run(script, "--pack", SKILL, "--dest", str(skills), "--check", env=self.env)[0], 0)
        changed = skills / SKILL / "SKILL.md"
        changed.write_bytes(b"local edit")
        self.assertEqual(run(script, "--pack", SKILL, "--dest", str(skills), "--check", env=self.env)[0], 1)
        self.assertEqual(run(script, "--pack", SKILL, "--dest", str(skills), env=self.env)[0], 2)
        self.assertEqual(changed.read_bytes(), b"local edit")
        self.assertEqual(run(script, "--pack", SKILL, "--dest", str(skills), "--force", env=self.env)[0], 0)
        self.assertEqual(list((skills.parent / ".backups").glob(SKILL + "-*"))[0].joinpath("SKILL.md").read_bytes(), b"local edit")
        self.assertEqual(run(script, "--pack", SKILL, "--auto", env=self.env)[0], 2)
        self.assertEqual(run(script, "--pack", SKILL, "--dest", str(skills), "--siblings", str(self.tmp), env=self.env)[0], 2)

    def test_package_layout_and_reproducibility(self):
        work = copy_repo(self.tmp / "repo")
        junk = work / SKILL_DIR / "tests" / "__pycache__"
        junk.mkdir()
        (junk / "note.txt").write_bytes(b"junk")  # only the directory rule can exclude this
        (work / SKILL_DIR / "tests" / "stray.pyc").write_bytes(b"junk")  # only the suffix rule can
        script = work / "scripts" / "delegation" / "install.py"
        first, second = self.tmp / "a.zip", self.tmp / "b.zip"
        self.assertEqual(run(script, "package", "--output", str(first))[0], 0)
        self.assertEqual(run(script, "package", "--output", str(second))[0], 0)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(str(first)) as archive:
            names = archive.namelist()
            stamps = {info.date_time for info in archive.infolist()}
            systems = {info.create_system for info in archive.infolist()}
            compression = {info.compress_type for info in archive.infolist()}
        self.assertEqual(stamps, {(1980, 1, 1, 0, 0, 0)})
        self.assertEqual(systems, {3})
        self.assertEqual(compression, {zipfile.ZIP_STORED})
        self.assertTrue(all(n.startswith(SKILL + "/") for n in names))
        self.assertFalse(any("\\" in n or n.endswith(".pyc") or "__pycache__" in n for n in names))
        for needed in ("SKILL.md", "agents/openai.yaml", "prompts/01-interview.md"):
            self.assertIn(SKILL + "/" + needed, names)
        code, out = run(script, "package", "--output", str(first))
        self.assertEqual(code, 2, out)
        self.assertEqual(run(script, "package", "--output", str(first), "--force")[0], 0)


if __name__ == "__main__":
    unittest.main()
