"""Generated payload integrity and execution without the source checkout."""
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_plugin


class PluginBuildTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.source = self.base / "source"
        for name, content in build_plugin.payload_files(ROOT).items():
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        (self.source / "CLAUDE.md").write_text("Retained clone entry.\n", encoding="utf-8")
        self.dest = self.source / build_plugin.DESTINATION

    def generate(self):
        self.assertTrue(build_plugin.build(self.source))

    def test_exact_idempotent_projection_preserves_clone_and_private_state(self):
        private = self.source / ".claude/.verification/private.json"
        private.parent.mkdir(parents=True)
        private.write_text("fixture state", encoding="utf-8")
        excluded = self.source / "skills/ai-delegation-loop/SKILL.md"
        excluded.parent.mkdir(parents=True, exist_ok=True)
        excluded.write_text("retained source fixture", encoding="utf-8")
        self.generate()
        self.assertEqual(excluded.read_text(), "retained source fixture")
        self.assertFalse((self.dest / "skills/ai-delegation-loop").exists())
        self.assertEqual((self.source / "CLAUDE.md").read_text(), "Retained clone entry.\n")
        for name in ("CLAUDE.md", ".claude-plugin/marketplace.json", ".claude/.verification/private.json",
                     "skills/ai-delegation-loop/tests/run_simulation.py"):
            self.assertFalse((self.dest / name).exists(), name)
        before = {rel: (self.dest / rel).stat().st_mtime_ns for rel in build_plugin.files_in(self.dest)}
        self.generate()
        self.assertTrue(build_plugin.build(self.source, check=True))
        self.assertEqual(before, {rel: (self.dest / rel).stat().st_mtime_ns for rel in before})

    def test_check_reports_missing_extra_changed_without_writing(self):
        self.assertFalse(build_plugin.build(self.source, check=True))
        self.assertFalse(self.dest.exists())
        self.generate()
        (self.dest / "kernel/CoreKernel.md").write_bytes(b"changed")
        (self.dest / "LICENSE").unlink()
        (self.dest / "KEEP.txt").write_bytes(b"user fixture")
        before = {rel: (self.dest / rel).read_bytes() for rel in build_plugin.files_in(self.dest)}
        self.assertFalse(build_plugin.build(self.source, check=True))
        self.assertEqual(before, {rel: (self.dest / rel).read_bytes() for rel in build_plugin.files_in(self.dest)})
        with self.assertRaisesRegex(ValueError, "Unexpected payload files"):
            build_plugin.build(self.source)
        self.assertEqual(before, {rel: (self.dest / rel).read_bytes() for rel in build_plugin.files_in(self.dest)})

    def test_archive_excludes_uncleared_material_without_removing_source(self):
        import io
        import tarfile
        (self.source / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
        blocked = ("skills/ai-delegation-loop", "scripts/delegation", "docs/delegation-loop",
                   "plugins/fef-engineering/skills/ai-delegation-loop")
        for folder in blocked:
            path = self.source / folder / "fixture.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("retained archive fixture", encoding="utf-8")
        for args in (("init", "-q"), ("add", "-A")):
            subprocess.run(["git", *args], cwd=self.source, check=True, capture_output=True, timeout=30)
        tree = subprocess.run(["git", "write-tree"], cwd=self.source, check=True,
                              capture_output=True, text=True, timeout=30).stdout.strip()
        archive = subprocess.run(["git", "archive", "--format=tar", "--worktree-attributes", tree],
                                 cwd=self.source, check=True, capture_output=True, timeout=30)
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as stream:
            names = stream.getnames()
        self.assertIn("skills/fef-coding/SKILL.md", names)
        for folder in blocked:
            self.assertFalse(any(name == folder or name.startswith(folder + "/") for name in names))
            self.assertTrue((self.source / folder / "fixture.txt").is_file())

    def test_source_change_is_detected_and_regenerated(self):
        self.generate()
        path = self.source / "kernel/CoreKernel.md"
        path.write_bytes(path.read_bytes() + b"\nFixture change.\n")
        self.assertFalse(build_plugin.build(self.source, check=True))
        self.generate()
        self.assertEqual(path.read_bytes(), (self.dest / "kernel/CoreKernel.md").read_bytes())
        self.assertTrue(build_plugin.build(self.source, check=True))

    def test_autocrlf_checkout_preserves_generated_payload(self):
        self.generate()
        (self.source / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
        checkout = self.base / "checkout"
        checkout.mkdir()
        for arguments in (
            ["init", "-q"],
            ["-c", "core.autocrlf=true", "-c", "core.safecrlf=false", "add", "-A"],
            ["-c", "core.autocrlf=true", "checkout-index", "--all",
             "--prefix=" + checkout.as_posix() + "/"],
        ):
            subprocess.run(["git", *arguments], cwd=self.source, check=True, capture_output=True)
        self.assertTrue(build_plugin.build(checkout, check=True))

    def test_missing_links_do_not_expand_payload_or_follow_outside_paths(self):
        private = self.source / "docs/private.md"
        private.write_bytes(b"not a runtime input")
        path = self.source / "docs/loading-map.md"
        path.write_bytes(path.read_bytes() + b"\n[private](private.md)\n")
        with self.assertRaisesRegex(ValueError, "Missing or external payload link"):
            build_plugin.build(self.source)
        self.assertFalse(self.dest.exists())
        with self.assertRaises(ValueError):
            build_plugin.validate_links({"README.md": b"[outside](../outside.md)"})

    def test_reparse_inputs_and_output_ancestors_are_refused_without_privileges(self):
        original = Path.lstat
        for suspect in (self.source / "kernel", self.source / "plugins", self.dest):
            with self.subTest(suspect=suspect):
                def lstat(path, *args, **kwargs):
                    if path == suspect:
                        return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                    return original(path, *args, **kwargs)
                with patch.object(Path, "lstat", lstat):
                    with self.assertRaisesRegex(ValueError, "Symlink or junction"):
                        build_plugin.build(self.source)
        self.assertFalse(self.dest.exists())

    def test_failed_replace_preserves_prior_file_and_cleans_temporary_file(self):
        self.generate()
        before = (self.dest / "kernel/CoreKernel.md").read_bytes()
        path = self.source / "kernel/CoreKernel.md"
        path.write_bytes(before + b"\nChanged source.\n")
        names = build_plugin.files_in(self.dest)
        with patch.object(build_plugin.os, "replace", side_effect=OSError("fixture failure")):
            with self.assertRaises(OSError):
                build_plugin.build(self.source)
        self.assertEqual((self.dest / "kernel/CoreKernel.md").read_bytes(), before)
        self.assertEqual(build_plugin.files_in(self.dest), names)

    def test_payload_alone_routes_and_supplies_kernel_and_baseline(self):
        self.generate()
        installed = self.base / "installed plugin"
        shutil.copytree(self.dest, installed)
        consumer = self.base / "consumer"
        consumer.mkdir()
        subprocess.run(["git", "init", "-q", str(consumer)], check=True, capture_output=True)
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(installed), PYTHONUTF8="1")
        env.pop("PYTHONPATH", None)
        route = subprocess.run([sys.executable, "-X", "utf8", str(installed / "scripts/detect_task.py"),
                                "--task", "fix code in app.py"], cwd=consumer, env=env,
                               capture_output=True, text=True, encoding="utf-8", timeout=45)
        self.assertEqual(route.returncode, 0, route.stderr)
        self.assertEqual(json.loads(route.stdout)["task_type"], "coding")
        hook = subprocess.run([sys.executable, "-I", "-X", "utf8", str(installed / "scripts/hooks/session_start.py")],
                              input=json.dumps({"session_id": "isolated", "cwd": str(consumer)}),
                              cwd=consumer, env=env, capture_output=True, text=True, encoding="utf-8", timeout=45)
        self.assertEqual(hook.returncode, 0, hook.stderr)
        self.assertEqual(hook.stderr, "")
        context = json.loads(hook.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("# Core Kernel", context)
        self.assertIn((installed / "docs/loading-map.md").resolve().as_posix(), context)
        self.assertNotIn(self.source.resolve().as_posix(), context)
        self.assertEqual(len(list((consumer / ".claude/.verification").glob("*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
