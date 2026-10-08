"""Regression coverage for session-scoped verification and native Bash payloads."""
import json
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lib.verification_state import RESULT_PREFIX, digest, load_state, snapshot

START = SCRIPTS / "hooks" / "session_start.py"
RECORD = SCRIPTS / "hooks" / "record_test_run.py"
STOP = SCRIPTS / "hooks" / "verify_before_stop.py"
WRAPPER = SCRIPTS / "run_verification.py"


HOOK_MODULES = {}


def run_hook(script, payload, cwd, native=False):
    data = {"session_id": "session-A", "cwd": str(cwd), **payload}
    if native:
        return subprocess.run([sys.executable, str(script)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=cwd, timeout=30)
    # Exercise the public JSON entry point with real Git/filesystem operations.
    # Separate integration cases below also launch the scripts as subprocesses.
    if script not in HOOK_MODULES:
        spec = importlib.util.spec_from_file_location("fef_hook_" + script.stem, script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        HOOK_MODULES[script] = module
    stdout, stderr = io.StringIO(), io.StringIO()
    with patch("sys.stdin", io.StringIO(json.dumps(data))), redirect_stdout(stdout), redirect_stderr(stderr):
        code = HOOK_MODULES[script].main()
    return SimpleNamespace(returncode=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


class SessionVerificationTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "Test")
        (self.root / ".gitignore").write_text(".claude/.verification/\n__pycache__/\n", encoding="utf-8")
        (self.root / "app.py").write_text("x = 1\n", encoding="utf-8")
        git(self.root, "add", "-A")
        git(self.root, "commit", "-qm", "baseline")
        self.start()

    def start(self, session="session-A", source="startup"):
        result = run_hook(START, {"session_id": session, "source": source}, self.root)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def change(self, text="x = 2\n"):
        (self.root / "app.py").write_text(text, encoding="utf-8")

    def record(self, code=0, session="session-A", command="python -m unittest discover", response=None):
        return run_hook(RECORD, {"session_id": session, "tool_name": "Bash",
                                "tool_input": {"command": command},
                                "tool_response": {"returncode": code} if response is None else response}, self.root)

    def stop(self, session="session-A", **payload):
        return run_hook(STOP, {"session_id": session, **payload}, self.root)

    def assert_blocked(self, session="session-A"):
        result = self.stop(session)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_clean_session_needs_no_verification(self):
        self.assertEqual(self.stop().stdout, "")

    def test_preexisting_dirty_read_only_session_does_not_block(self):
        self.change()
        self.start("read-only")
        self.assertEqual(self.stop("read-only").stdout, "")

    def test_changed_file_requires_verification(self):
        self.change()
        self.assert_blocked()

    def test_successful_explicit_exit_verifies_current_snapshot(self):
        self.change()
        self.record()
        self.assertEqual(self.stop().stdout, "")

    def test_failed_test_cannot_verify(self):
        self.change()
        self.record(code=1)
        self.assert_blocked()

    def test_unknown_native_exit_invalidates_earlier_success(self):
        self.change()
        self.record()
        self.record(response={"stdout": "collected tests", "stderr": "", "interrupted": False})
        self.assert_blocked()

    def test_bool_exit_code_is_not_integer_success(self):
        self.change()
        self.record(code=False)
        self.assert_blocked()

    def test_interrupted_tool_cannot_verify(self):
        self.change()
        self.record(response={"returncode": 0, "interrupted": True})
        self.assert_blocked()

    def test_compound_pipeline_or_masked_exit_cannot_verify(self):
        self.change()
        for command in ("pytest | head", "pytest; true", "pytest || true", "echo ok; pytest"):
            self.record(command=command)
            self.assert_blocked()

    def test_later_edit_with_same_mtime_invalidates_success(self):
        self.change()
        self.record()
        stamp = (self.root / "app.py").stat().st_mtime_ns
        self.change("x = 3\n")
        os.utime(self.root / "app.py", ns=(stamp, stamp))
        self.assert_blocked()

    def test_verification_is_not_shared_across_sessions(self):
        self.start("session-B")
        self.change()
        self.record()
        self.assertEqual(self.stop().stdout, "")
        self.assert_blocked("session-B")

    def test_resume_and_compact_preserve_pending_changes(self):
        self.change()
        for source in ("resume", "compact"):
            self.start(source=source)
            self.assert_blocked()

    def test_clear_establishes_new_baseline(self):
        self.change()
        self.start(source="clear")
        self.assertEqual(self.stop().stdout, "")

    def test_nested_untracked_types_and_unicode_are_detected(self):
        nested = self.root / "새 폴더"
        nested.mkdir()
        (nested / "new file.ts").write_text("export const x = 1;", encoding="utf-8")
        self.assert_blocked()

    def test_deleted_file_is_detected(self):
        (self.root / "app.py").unlink()
        self.assert_blocked()

    def test_staged_rename_with_spaces_is_detected(self):
        git(self.root, "mv", "app.py", "renamed file.py")
        self.assert_blocked()
        self.record()
        self.assertEqual(self.stop().stdout, "")

    def test_new_commit_changes_snapshot_even_when_worktree_clean(self):
        self.change()
        git(self.root, "add", "app.py")
        git(self.root, "commit", "-qm", "edit")
        self.assert_blocked()

    def test_nested_cwd_uses_same_repository(self):
        child = self.root / "folder"
        child.mkdir()
        self.change()
        result = run_hook(RECORD, {"tool_name": "Bash", "tool_input": {"command": "pytest"},
                                  "tool_response": {"exit_code": 0}}, child)
        self.assertEqual(result.stderr, "")
        self.assertEqual(self.stop().stdout, "")

    def test_stop_hook_active_never_loops(self):
        self.change()
        self.assertEqual(self.stop(stop_hook_active=True).stdout, "")

    def test_missing_or_corrupt_state_is_visible_and_fails_open(self):
        result = self.stop("unknown")
        self.assertEqual(result.stdout, "")
        self.assertIn("unavailable", result.stderr)
        from lib.verification_state import state_path
        state_path(self.root, "session-A").write_text("not json", encoding="utf-8")
        result = self.stop()
        self.assertEqual(result.stdout, "")
        self.assertIn("unavailable", result.stderr)

    def test_non_verification_bash_does_not_credit(self):
        self.change()
        self.record(command="echo pytest")
        self.assert_blocked()

    def test_native_script_json_entrypoints(self):
        result = run_hook(START, {"session_id": "native"}, self.root, native=True)
        self.assertEqual(result.returncode, 0)
        self.change()
        result = run_hook(RECORD, {"session_id": "native", "tool_name": "Bash",
                                  "tool_input": {"command": "pytest"},
                                  "tool_response": {"exit_code": 0}}, self.root, native=True)
        self.assertEqual(result.stderr, "")
        result = run_hook(STOP, {"session_id": "native"}, self.root, native=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_state_contains_no_raw_command_arguments(self):
        self.change()
        self.record(command="pytest --password=CANARY_TEST_ONLY")
        state = json.dumps(load_state(self.root, "session-A"))
        self.assertNotIn("CANARY_TEST_ONLY", state)

    def test_real_wrapper_success_credits_native_payload_without_exit_code(self):
        self.change()
        (self.root / "test_app.py").write_text(
            "import unittest\nfrom app import x\nclass TestApp(unittest.TestCase):\n"
            "    def test_x(self): self.assertEqual(x, 2); print('partial', end='')\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(WRAPPER), "--", "python", "-m",
                                 "unittest", "discover", "-s", "."], cwd=self.root,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(RESULT_PREFIX, result.stdout)
        self.assertIn("OK", result.stderr)
        command = 'python "' + WRAPPER.as_posix() + '" -- python -m unittest discover -s .'
        self.record(command=command, response={"stdout": result.stdout, "stderr": result.stderr,
                                              "interrupted": False, "isImage": False})
        self.assertEqual(self.stop().stdout, "")

    def test_real_wrapper_failure_preserves_exit_and_stderr(self):
        (self.root / "test_failure.py").write_text(
            "import unittest\nclass Fail(unittest.TestCase):\n"
            "    def test_failure(self): self.fail('expected failure')\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(WRAPPER), "--", "python", "-m",
                                 "unittest", "discover", "-s", "."], cwd=self.root,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected failure", result.stderr)
        command = 'python "' + WRAPPER.as_posix() + '" -- python -m unittest discover -s .'
        self.record(command=command, response={"stdout": result.stdout, "interrupted": False})
        self.assert_blocked()

    def test_stale_or_wrong_wrapper_footer_cannot_verify(self):
        self.change()
        command = 'python "' + WRAPPER.as_posix() + '" -- pytest'
        record = {"argv_digest": digest(["pytest"]), "returncode": 0,
                  "snapshot": digest(snapshot(self.root))}
        self.change("x = 3\n")
        self.record(command=command, response={"stdout": RESULT_PREFIX + json.dumps(record)})
        self.assert_blocked()

    def test_malformed_wrapper_attempt_invalidates_previous_pass(self):
        self.change()
        command = 'python "' + WRAPPER.as_posix() + '" -- pytest'
        for footer in ("invalid JSON", "[]"):
            self.record()
            self.record(command=command, response={"stdout": RESULT_PREFIX + footer})
            self.assert_blocked()

    def test_wrapper_changed_during_run_cannot_verify(self):
        self.change()
        current = digest(snapshot(self.root))
        command = 'python "' + WRAPPER.as_posix() + '" -- pytest'
        record = {"argv_digest": digest(["pytest"]), "returncode": 0,
                  "snapshot_before": "different-state", "snapshot": current}
        self.record(command=command, response={"stdout": RESULT_PREFIX + json.dumps(record)})
        self.assert_blocked()

    def test_non_bash_and_garbage_input_fail_open(self):
        self.change()
        result = run_hook(RECORD, {"tool_name": "Read"}, self.root)
        self.assertEqual(result.returncode, 0)
        self.assert_blocked()
        result = subprocess.run([sys.executable, str(STOP)], input="not json",
                                cwd=self.root, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)
        self.assertIn("unavailable", result.stderr)


class ExtractExitCodeTest(unittest.TestCase):
    def test_defensive_host_exit_metadata(self):
        from lib.verification_commands import extract_exit_code
        self.assertEqual(extract_exit_code({"tool_result": {"exit_code": 0}}), 0)
        self.assertEqual(extract_exit_code({"exit_code": 1}), 1)
        self.assertIsNone(extract_exit_code({"tool_input": {"command": "true"}}))


if __name__ == "__main__":
    unittest.main()
