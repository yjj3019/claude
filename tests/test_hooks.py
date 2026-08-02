import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "scripts" / "hooks" / "record_test_run.py"
VERIFY = ROOT / "scripts" / "hooks" / "verify_before_stop.py"


def run_hook(script, payload, cwd):
    return subprocess.run(
        [sys.executable, str(script)], input=json.dumps(payload),
        capture_output=True, text=True, cwd=cwd, timeout=30,
    )


def init_git_repo(root):
    env = os.environ.copy()
    for cmd in (["git", "init", "-q"],
                ["git", "config", "user.email", "t@t.t"],
                ["git", "config", "user.name", "T"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True, env=env)


class RecordTestRunHookTest(unittest.TestCase):
    def test_marker_written_for_test_command(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_hook(RECORD, {"tool_name": "Bash",
                                     "tool_input": {"command": "python3 -m unittest discover -s tests"}}, root)
            self.assertEqual(proc.returncode, 0)
            self.assertTrue((root / ".claude" / ".test-run-marker").exists())

    def test_marker_not_written_for_non_test_command(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = run_hook(RECORD, {"tool_name": "Bash", "tool_input": {"command": "ls -la"}}, root)
            self.assertEqual(proc.returncode, 0)
            self.assertFalse((root / ".claude" / ".test-run-marker").exists())

    def test_garbage_input_fails_open(self):
        with tempfile.TemporaryDirectory() as d:
            proc = subprocess.run([sys.executable, str(RECORD)], input="not json",
                                  capture_output=True, text=True, cwd=d, timeout=30)
            self.assertEqual(proc.returncode, 0)


class VerifyBeforeStopHookTest(unittest.TestCase):
    def make_dirty_repo(self, root):
        init_git_repo(root)
        target = root / "app.py"
        target.write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=root, check=True, capture_output=True)
        target.write_text("x = 2\n", encoding="utf-8")

    def test_blocks_when_python_changed_and_no_marker(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_dirty_repo(root)
            proc = run_hook(VERIFY, {"stop_hook_active": False}, root)
            self.assertEqual(proc.returncode, 0)
            out = json.loads(proc.stdout)
            self.assertEqual(out["decision"], "block")
            self.assertIn("app.py", out["reason"])

    def test_allows_when_marker_is_fresh(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_dirty_repo(root)
            time.sleep(0.05)
            marker = root / ".claude" / ".test-run-marker"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("unittest", encoding="utf-8")
            proc = run_hook(VERIFY, {"stop_hook_active": False}, root)
            self.assertEqual(proc.stdout.strip(), "")

    def test_blocks_when_change_is_newer_than_marker(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_dirty_repo(root)
            marker = root / ".claude" / ".test-run-marker"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("unittest", encoding="utf-8")
            time.sleep(0.05)
            (root / "app.py").write_text("x = 3\n", encoding="utf-8")
            proc = run_hook(VERIFY, {"stop_hook_active": False}, root)
            self.assertIn("block", proc.stdout)

    def test_never_loops_when_stop_hook_active(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.make_dirty_repo(root)
            proc = run_hook(VERIFY, {"stop_hook_active": True}, root)
            self.assertEqual(proc.stdout.strip(), "")

    def test_allows_clean_worktree(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init_git_repo(root)
            proc = run_hook(VERIFY, {"stop_hook_active": False}, root)
            self.assertEqual(proc.stdout.strip(), "")

    def test_fails_open_outside_git(self):
        with tempfile.TemporaryDirectory() as d:
            proc = run_hook(VERIFY, {"stop_hook_active": False}, Path(d))
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(proc.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
