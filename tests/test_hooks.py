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

    def record(self, code=0, session="session-A", command="python -m unittest discover", response=None, tool="Bash"):
        return run_hook(RECORD, {"session_id": session, "tool_name": tool,
                                "tool_input": {"command": command},
                                "tool_response": {"returncode": code} if response is None else response}, self.root)

    def stop(self, session="session-A", **payload):
        return run_hook(STOP, {"session_id": session, **payload}, self.root)

    def assert_blocked(self, session="session-A"):
        result = self.stop(session)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout, result.stderr or "Stop returned no blocking decision")
        self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_clean_session_needs_no_verification(self):
        self.assertEqual(self.stop().stdout, "")

    def test_plugin_start_delivers_kernel_and_preserves_baseline(self):
        from sync_kernel import rendered_kernel
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(ROOT)}):
            result = run_hook(START, {"session_id": "plugin", "source": "startup"}, self.root)
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(output["hookEventName"], "SessionStart")
        self.assertIn(rendered_kernel(), output["additionalContext"])
        self.assertIn((ROOT / "docs/loading-map.md").as_posix(), output["additionalContext"])
        self.assertIsNotNone(load_state(self.root, "plugin"))

    def test_plugin_start_delivers_kernel_outside_git(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(ROOT)}):
                result = run_hook(START, {}, Path(folder), native=True)
        self.assertIn("# Core Kernel", json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])
        self.assertIn("reminder unavailable", result.stderr)

    def test_missing_plugin_kernel_does_not_skip_baseline(self):
        module = HOOK_MODULES[START]
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(ROOT)}), \
                patch.object(module, "rendered_kernel", side_effect=FileNotFoundError):
            result = run_hook(START, {"session_id": "missing-kernel"}, self.root)
        self.assertEqual(result.stdout, "")
        self.assertIn("reminder unavailable", result.stderr)
        self.assertIsNotNone(load_state(self.root, "missing-kernel"))

    def test_plugin_rename_resume_preserves_verification_and_custom_data(self):
        from lib.verification_state import state_path
        old_data = self.root / "old-plugin-data"
        new_data = self.root / "new-plugin-data"
        for directory in (old_data, new_data):
            directory.mkdir()
            (directory / "keep.txt").write_text(directory.name, encoding="utf-8")
        session = "rename-resume"
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(ROOT / "fef-claude"),
                                     "CLAUDE_PLUGIN_DATA": str(old_data)}):
            self.start(session)
            self.change()
            self.record(session=session)
        path = state_path(self.root, session)
        before = path.read_bytes()
        with patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": str(ROOT / "fef-engineering"),
                                     "CLAUDE_PLUGIN_DATA": str(new_data)}):
            self.start(session, source="resume")
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(self.stop(session).stdout, "")
            self.change("x = 3\n")
            self.assert_blocked(session)
        for directory in (old_data, new_data):
            self.assertEqual((directory / "keep.txt").read_text(encoding="utf-8"), directory.name)

    def test_preexisting_dirty_read_only_session_does_not_block(self):
        self.change()
        self.start("read-only")
        self.assertEqual(self.stop("read-only").stdout, "")

    def test_changed_file_requires_verification(self):
        self.change()
        self.assert_blocked()

    def test_submodule_edits_invalidate_verification_even_when_status_ignored(self):
        child = self.root / "dep"
        child.mkdir()
        git(child, "init", "-q")
        target = child / "library.py"
        target.write_text("value = 1\n", encoding="utf-8")
        git(child, "add", "library.py")
        git(child, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
            "commit", "-qm", "child baseline")
        oid = git(child, "rev-parse", "HEAD").stdout.decode().strip()
        (self.root / ".gitmodules").write_text(
            '[submodule "dep"]\n\tpath = dep\n\turl = ./unused-local-source\n', encoding="utf-8")
        git(self.root, "add", ".gitmodules")
        git(self.root, "update-index", "--add", "--cacheinfo", "160000", oid, "dep")
        git(self.root, "commit", "-qm", "register test gitlink")
        self.start()
        target.write_text("value = 2\n", encoding="utf-8")
        recorded = self.record()
        self.assertEqual(recorded.stderr, "")
        stopped = self.stop()
        self.assertEqual(stopped.stderr, "")
        self.assertEqual(stopped.stdout, "")
        previous = digest(snapshot(self.root))
        target.write_text("value = 3\n", encoding="utf-8")
        self.assertNotEqual(previous, digest(snapshot(self.root)))
        self.assert_blocked()

        git(self.root, "config", "submodule.dep.ignore", "all")
        self.assertEqual(git(self.root, "status", "--porcelain").stdout, b"")
        recorded = self.record()
        self.assertEqual(recorded.stderr, "")
        stopped = self.stop()
        self.assertEqual(stopped.stderr, "")
        self.assertEqual(stopped.stdout, "")
        (child / "new.py").write_text("new = True\n", encoding="utf-8")
        self.assert_blocked()

    def test_successful_explicit_exit_verifies_current_snapshot(self):
        self.change()
        self.record()
        self.assertEqual(self.stop().stdout, "")

    def test_failed_test_cannot_verify(self):
        self.change()
        self.record(code=1)
        self.assert_blocked()

    def test_powershell_exit_metadata_and_unsafe_syntax(self):
        self.change()
        self.record(tool="PowerShell")
        self.assertEqual(self.stop().stdout, "")
        for response in ({"returncode": 1}, {"returncode": False}, {},
                         {"returncode": 0, "interrupted": True}):
            self.record(tool="PowerShell", response=response)
            self.assert_blocked()
        for command in ("pytest; Write-Output ok", "pytest | Select-Object -First 1",
                        "pytest && Write-Output ok", "pytest $args", "pytest `n",
                        "pytest # comment", "pytest (Get-Item .)", "pytest --% hidden",
                        "pytest 'a''b'", 'pytest "a""b"'):
            self.record(tool="PowerShell")
            self.record(tool="PowerShell", command=command)
            self.assert_blocked()

    def test_powershell_wrapper_literal_paths_and_footer_guards(self):
        self.change()
        current = digest(snapshot(self.root))
        record = {"argv_digest": digest(["pytest"]), "returncode": 0,
                  "snapshot_before": current, "snapshot": current}
        for quote in ('"', "'"):
            command = 'python ' + quote + str(WRAPPER) + quote + ' -- pytest'
            self.record(tool="PowerShell", command=command,
                        response={"stdout": RESULT_PREFIX + json.dumps(record)})
            self.assertEqual(self.stop().stdout, "")
            for footer in ("invalid JSON", "[]", json.dumps({**record, "argv_digest": "wrong"}),
                           json.dumps({**record, "snapshot": "stale"}),
                           json.dumps({**record, "snapshot_before": "changed"}),
                           json.dumps({**record, "returncode": False})):
                self.record(tool="PowerShell", command=command, response={"stdout": RESULT_PREFIX + footer})
                self.assert_blocked()

    def test_powershell_later_edit_invalidates_success(self):
        self.change()
        self.record(tool="PowerShell")
        self.change("x = 3\n")
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
        for tool in ("Bash", "PowerShell"):
            self.record(tool=tool, command=command, response={"stdout": result.stdout, "stderr": result.stderr,
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
        for tool in ("Bash", "PowerShell"):
            self.record(tool=tool, command=command, response={"stdout": result.stdout, "interrupted": False})
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

    def test_snapshot_error_invalidates_previous_pass(self):
        self.change()
        self.record()
        self.assertEqual(self.stop().stdout, "")
        error = subprocess.TimeoutExpired(
            ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], 15,
            output="CANARY_PRIVATE_OUTPUT", stderr="CANARY_PRIVATE_ERROR")
        with patch.object(HOOK_MODULES[RECORD], "snapshot", side_effect=error):
            result = self.record()
        self.assertIn("TimeoutExpired", result.stderr)
        self.assertNotIn("CANARY_PRIVATE", result.stderr)
        self.assertIsNone(load_state(self.root, "session-A")["verification"])
        self.assert_blocked()

    def test_result_error_invalidates_previous_pass(self):
        self.change()
        self.record()
        with patch.object(HOOK_MODULES[RECORD], "verification_result",
                          side_effect=TypeError("CANARY_PRIVATE_ERROR")):
            result = self.record()
        self.assertIn("TypeError", result.stderr)
        self.assertNotIn("CANARY_PRIVATE", result.stderr)
        self.assertIsNone(load_state(self.root, "session-A")["verification"])
        self.assert_blocked()

    def test_final_state_write_error_invalidates_previous_pass(self):
        self.change()
        self.record()
        module = HOOK_MODULES[RECORD]
        real_save = module.save_state

        def save_without_verification(root, session, state):
            if state.get("verification") is not None:
                raise OSError("CANARY_PRIVATE_ERROR")
            return real_save(root, session, state)

        with patch.object(module, "save_state", side_effect=save_without_verification):
            result = self.record()
        self.assertIn("OSError", result.stderr)
        self.assertNotIn("CANARY_PRIVATE", result.stderr)
        self.assertIsNone(load_state(self.root, "session-A")["verification"])
        self.assert_blocked()

    def test_initial_state_write_error_blocks_previous_pass(self):
        from lib.verification_state import state_path
        self.change()
        self.record()
        self.start("session-B")
        path = state_path(self.root, "session-A")
        before = path.read_bytes()
        with patch("lib.verification_state.os.replace", side_effect=PermissionError("CANARY_PRIVATE")):
            result = self.record(code=1)
        self.assertIn("PermissionError", result.stderr)
        self.assertNotIn("CANARY_PRIVATE", result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assert_blocked()
        self.assertEqual(self.stop(stop_hook_active=True).stdout, "")
        self.assertEqual(self.stop("session-B").stdout, "")
        self.start(source="resume")
        self.assert_blocked()
        self.record(code=1)
        self.assertFalse(path.with_suffix(".failed").exists())
        self.assert_blocked()
        self.record()
        self.assertFalse(path.with_suffix(".failed").exists())
        self.assertEqual(self.stop().stdout, "")

    def test_initial_baseline_write_error_is_visible_at_stop(self):
        from lib.verification_state import state_path
        with patch("lib.verification_state.os.replace", side_effect=PermissionError("CANARY_PRIVATE")):
            result = run_hook(START, {"session_id": "new-session"}, self.root)
        self.assertIn("PermissionError", result.stderr)
        self.assertNotIn("CANARY_PRIVATE", result.stderr)
        self.assertIsNone(load_state(self.root, "new-session"))
        self.assert_blocked("new-session")
        self.start("new-session", source="clear")
        self.assertFalse(state_path(self.root, "new-session").with_suffix(".failed").exists())
        self.assertEqual(self.stop("new-session").stdout, "")

    @unittest.skipUnless(os.name == "nt", "Windows file sharing regression")
    def test_windows_locked_state_does_not_credit_previous_pass(self):
        import ctypes
        from ctypes import wintypes
        from lib.verification_state import state_path
        self.change()
        self.record()
        path = state_path(self.root, "session-A")
        before = path.read_bytes()
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                      wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel.CreateFileW.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel.CloseHandle.restype = wintypes.BOOL
        # Allow reads/writes, but deny replacement while this handle is open.
        handle = kernel.CreateFileW(str(path), 0x80000000, 0x1 | 0x2, None, 3, 0x80, None)
        self.assertNotEqual(handle, wintypes.HANDLE(-1).value)
        try:
            result = self.record(code=1)
        finally:
            self.assertTrue(kernel.CloseHandle(handle))
        self.assertIn("PermissionError", result.stderr)
        self.assertEqual(path.read_bytes(), before)
        self.assert_blocked()
        self.record()
        self.assertEqual(self.stop().stdout, "")

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


class StateStorageFailureTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.state = {"version": 1, "baseline": {}, "verification": None}

    def test_serialization_error_survives_cleanup_error(self):
        from lib.verification_state import save_state, state_path
        error = TypeError("CANARY_PRIVATE")
        stderr = io.StringIO()
        with patch("lib.verification_state.json.dump", side_effect=error), \
                patch.object(Path, "unlink", side_effect=PermissionError("CANARY_PRIVATE")), \
                redirect_stderr(stderr), self.assertRaises(TypeError) as raised:
            save_state(self.root, "session", self.state)
        self.assertIs(raised.exception, error)
        self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())
        self.assertTrue(state_path(self.root, "session").with_suffix(".failed").exists())

    def test_marker_write_failure_preserves_original_error(self):
        from lib.verification_state import save_state
        error = OSError("CANARY_PRIVATE")
        stderr = io.StringIO()
        with patch("lib.verification_state.os.replace", side_effect=error), \
                patch.object(Path, "touch", side_effect=PermissionError("CANARY_PRIVATE")), \
                redirect_stderr(stderr), self.assertRaises(OSError) as raised:
            save_state(self.root, "session", self.state)
        self.assertIs(raised.exception, error)
        self.assertIn("could not be persisted", stderr.getvalue())
        self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())

    def test_marker_clear_failure_keeps_unverified(self):
        from lib.verification_state import save_state, state_path
        marker = state_path(self.root, "session").with_suffix(".failed")
        marker.parent.mkdir(parents=True)
        marker.touch()
        real_unlink = Path.unlink

        def unlink(path, *args, **kwargs):
            if path == marker:
                raise PermissionError("CANARY_PRIVATE")
            return real_unlink(path, *args, **kwargs)

        with patch.object(Path, "unlink", unlink), self.assertRaises(PermissionError):
            save_state(self.root, "session", self.state)
        self.assertTrue(marker.exists())
        self.assertEqual(load_state(self.root, "session"), self.state)


class GitExecutableTest(unittest.TestCase):
    def test_unset_and_empty_keep_path_lookup(self):
        from lib.verification_state import git_executable, run_git
        for value in (None, ""):
            with patch.dict(os.environ):
                os.environ.pop("FEF_GIT_EXECUTABLE", None)
                if value is not None:
                    os.environ["FEF_GIT_EXECUTABLE"] = value
                self.assertEqual(git_executable(), "git")
                with patch("lib.verification_state.subprocess.run") as run:
                    run_git(ROOT, "status")
                self.assertEqual(run.call_args.args[0], ["git", "status"])

    def test_explicit_path_with_spaces_is_a_single_argument(self):
        from lib.verification_state import git_executable, run_git
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "custom Git ü.exe"
            path.write_bytes(b"fixture")
            with patch.dict(os.environ, {"FEF_GIT_EXECUTABLE": str(path)}):
                self.assertEqual(git_executable(), str(path))
                with patch("lib.verification_state.subprocess.run") as run:
                    run_git(ROOT, "status")
                run.assert_called_once_with([str(path), "status"], cwd=ROOT,
                                            check=True, capture_output=True, timeout=15)

    def test_invalid_explicit_path_never_falls_back(self):
        from lib.verification_state import run_git
        with tempfile.TemporaryDirectory() as folder:
            for value in ("relative/git.exe", str(Path(folder) / "missing.exe"), folder):
                with self.subTest(value=value), patch.dict(os.environ, {"FEF_GIT_EXECUTABLE": value}), \
                        patch("lib.verification_state.subprocess.run") as run:
                    with self.assertRaises(OSError):
                        run_git(ROOT, "status")
                    run.assert_not_called()

    def test_head_nonzero_remains_unborn_without_retry(self):
        from lib.verification_state import snapshot
        with patch("lib.verification_state.git_executable", return_value="CANARY_PRIVATE.exe"), \
                patch("lib.verification_state.subprocess.run", side_effect=[
                    subprocess.CompletedProcess([], 0, stdout=b""),
                    subprocess.CompletedProcess([], 128, stdout=b""),
                    subprocess.CompletedProcess([], 0, stdout=b"")]) as run:
            self.assertEqual(snapshot(ROOT), {"head": None, "files": {}})
        self.assertEqual(run.call_count, 3)
        self.assertTrue(all(call.args[0][0] == "CANARY_PRIVATE.exe" for call in run.call_args_list))
        self.assertEqual([call.kwargs["check"] for call in run.call_args_list], [True, False, True])

    def test_windows_batch_path_is_rejected(self):
        from lib.verification_state import git_executable
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "git.cmd"
            path.write_bytes(b"fixture")
            with patch.dict(os.environ, {"FEF_GIT_EXECUTABLE": str(path)}), \
                    patch("lib.verification_state.sys.platform", "win32"):
                with self.assertRaises(OSError):
                    git_executable()

    def test_invalid_selection_prevents_wrapper_child_and_footer(self):
        spec = importlib.util.spec_from_file_location("fef_wrapper_invalid_git", WRAPPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, {"FEF_GIT_EXECUTABLE": "relative/git.exe"}), \
                patch.object(module.subprocess, "run") as run, \
                redirect_stdout(stdout), redirect_stderr(stderr):
            code = module.main(["--", "python", "-m", "unittest"])
        self.assertEqual(code, 2)
        self.assertNotIn(RESULT_PREFIX, stdout.getvalue())
        self.assertIn("Verification could not complete", stderr.getvalue())
        run.assert_not_called()

    def test_command_failure_is_not_retried(self):
        from lib.verification_state import git
        error = subprocess.CalledProcessError(1, ["CANARY_PRIVATE.exe", "status"])
        with patch("lib.verification_state.git_executable", return_value="CANARY_PRIVATE.exe"), \
                patch("lib.verification_state.subprocess.run", side_effect=error) as run:
            with self.assertRaises(subprocess.CalledProcessError) as caught:
                git(ROOT, "status")
        self.assertIs(caught.exception, error)
        self.assertEqual(run.call_count, 1)

    def test_explicit_git_timeout_retains_sanitized_operations(self):
        from lib.verification_state import hook_error, run_git
        for args, operation in ((["rev-parse", "--show-toplevel"], "repository"),
                                (["status", "--porcelain=v1", "-z", "--untracked-files=all"], "status"),
                                (["rev-parse", "--verify", "HEAD"], "head"),
                                (["ls-files", "--stage", "-z"], "index")):
            error = subprocess.TimeoutExpired(["CANARY_PRIVATE.exe", *args], 15,
                                             stderr="CANARY_PRIVATE_STDERR")
            with patch("lib.verification_state.git_executable", return_value="CANARY_PRIVATE.exe"), \
                    patch("lib.verification_state.subprocess.run", side_effect=error) as run:
                with self.assertRaises(subprocess.TimeoutExpired) as caught:
                    run_git(ROOT, *args)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                hook_error(caught.exception)
            self.assertIn("git_operation=" + operation, stderr.getvalue())
            self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())
            self.assertEqual(run.call_count, 1)


class ExtractExitCodeTest(unittest.TestCase):
    def test_sanitized_git_timeout_diagnostics(self):
        from lib.verification_state import hook_error
        operations = [
            (["git", "rev-parse", "--show-toplevel"], "repository"),
            (["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], "status"),
            (["git", "rev-parse", "--verify", "HEAD"], "head"),
            (["git", "ls-files", "--stage", "-z"], "index"),
        ]
        for args, operation in operations:
            with self.subTest(operation=operation):
                error = subprocess.TimeoutExpired(args, 15, output="CANARY_PRIVATE_OUTPUT",
                                                stderr="CANARY_PRIVATE_ERROR")
                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    hook_error(error)
                self.assertIn("git_operation=" + operation, stderr.getvalue())
                self.assertIn("TimeoutExpired", stderr.getvalue())
                self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())
                self.assertNotIn("--", stderr.getvalue())
        for args in (["git", "-c", "CANARY_PRIVATE_ARGUMENT", "status"],
                     "CANARY_PRIVATE_COMMAND", ["git", ["CANARY_PRIVATE_ARGUMENT"]]):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                hook_error(subprocess.TimeoutExpired(args, 15))
            self.assertIn("TimeoutExpired", stderr.getvalue())
            self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())
            self.assertNotIn("git_operation=", stderr.getvalue())

    def test_wrapper_reports_sanitized_git_timeout(self):
        spec = importlib.util.spec_from_file_location("fef_wrapper_timeout", WRAPPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stderr = io.StringIO()
        error = subprocess.TimeoutExpired(["git", "rev-parse", "--show-toplevel"], 15,
                                         stderr="CANARY_PRIVATE_ERROR")
        with patch.object(module, "repository", side_effect=error), redirect_stderr(stderr):
            code = module.main(["--", "python", "-m", "unittest"])
        self.assertEqual(code, 2)
        self.assertIn("Verification could not complete", stderr.getvalue())
        self.assertIn("git_operation=repository", stderr.getvalue())
        self.assertNotIn("CANARY_PRIVATE", stderr.getvalue())

    def test_hook_exec_arguments_and_shell_matchers(self):
        config = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
        for event, groups in config["hooks"].items():
            for group in groups:
                if event in ("PostToolUse", "PostToolUseFailure"):
                    self.assertEqual(group["matcher"], "Bash|PowerShell")
                for hook in group["hooks"]:
                    self.assertEqual(hook["command"], "python")
                    self.assertEqual(len(hook["args"]), 1)
                    self.assertTrue(hook["args"][0].startswith("${CLAUDE_PROJECT_DIR}/scripts/hooks/"))
                    self.assertTrue((ROOT / hook["args"][0].replace("${CLAUDE_PROJECT_DIR}/", "")).is_file())
                    self.assertNotIn("shell", hook)

    def test_ordinary_bash_skips_git_and_session_state(self):
        with tempfile.TemporaryDirectory() as directory:
            script = RECORD
            if script not in HOOK_MODULES:
                spec = importlib.util.spec_from_file_location("fef_hook_record", script)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                HOOK_MODULES[script] = module
            with patch.object(HOOK_MODULES[script], "repository", side_effect=AssertionError("unneeded Git")):
                result = run_hook(script, {"tool_name": "Bash", "tool_input": {"command": "echo hello"}}, Path(directory))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_defensive_host_exit_metadata(self):
        from lib.verification_commands import extract_exit_code
        self.assertEqual(extract_exit_code({"tool_result": {"exit_code": 0}}), 0)
        self.assertEqual(extract_exit_code({"exit_code": 1}), 1)
        self.assertIsNone(extract_exit_code({"tool_input": {"command": "true"}}))


if __name__ == "__main__":
    unittest.main()
