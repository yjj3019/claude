"""Plugin entry points must work from a consuming project, not just this repo."""
import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginRuntimeTest(unittest.TestCase):
    def test_plugin_rename_preserves_marketplace_migration(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "taskforge-for-claude")
        self.assertEqual(manifest["displayName"], "TaskForge for Claude")
        self.assertEqual(market["name"], "taskforge-marketplace")
        self.assertEqual(market["renames"]["fef-claude"], "fef-engineering")
        self.assertEqual(market["renames"]["fef-engineering"], manifest["name"])
        self.assertEqual([entry["name"] for entry in market["plugins"]], [manifest["name"]])
        self.assertEqual(market["plugins"][0]["source"], "./plugins/taskforge-for-claude")
        shipped = json.loads((ROOT / "plugins/taskforge-for-claude/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(shipped, manifest)

    def test_unresolved_license_is_not_advertised_as_mit(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("license", manifest)
        self.assertTrue(all("license" not in plugin for plugin in market["plugins"]))

    def test_plugin_skill_names_and_standalone_entry_remain_distinct(self):
        # Native skill names follow the approved public rename; the independently
        # installed pack keeps its persisted directory and entry contract.
        for name in ("coding", "rca", "ai-delegation-loop"):
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name: {re.escape(name)}\s*$")
            if name in ("coding", "rca"):
                self.assertIn('version: "2.0.0"', text)
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            import install_pack
            self.assertEqual(install_pack.PACK_NAME, "fef-claude")
        finally:
            sys.path.pop(0)

    def test_marketplace_version_cannot_disagree_with_plugin_manifest(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        entry = next(plugin for plugin in market["plugins"] if plugin["name"] == manifest["name"])
        # The entry can omit version and defer to the manifest; a duplicate
        # version must not advertise a different release to users.
        self.assertEqual(entry.get("version", manifest["version"]), manifest["version"])

    def test_readme_install_commands_match_marketplace_identity(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        expected = f"{market['plugins'][0]['name']}@{market['name']}"
        found = []
        for path in ROOT.glob("README*.md"):
            ids = re.findall(r"/plugin install ([\w@.-]+)", path.read_text(encoding="utf-8"))
            found.extend(ids)
            for plugin_id in ids:
                self.assertEqual(plugin_id, expected, path.name)
        self.assertTrue(found)

    def test_coding_skill_routes_from_unrelated_project(self):
        text = (ROOT / "skills/coding/SKILL.md").read_text(encoding="utf-8")
        command = re.search(r"`(python [^`]*detect_task\.py[^`]*)`", text).group(1)
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/scripts/detect_task.py"', command)
        # Use a path containing spaces, as real plugin caches can have them.
        with tempfile.TemporaryDirectory(prefix="fef plugin ") as folder:
            install = Path(folder) / "installed plugin"
            for name in ("scripts", "config", "modules", "policies", "domains", "workflows", "reviewers"):
                shutil.copytree(ROOT / name, install / name, ignore=shutil.ignore_patterns("__pycache__"))
            project = Path(folder) / "project"
            (project / "scripts").mkdir(parents=True)
            (project / "scripts/detect_task.py").write_text("raise RuntimeError('wrong project script')\n", encoding="utf-8")
            argv = shlex.split(command.replace("${CLAUDE_PLUGIN_ROOT}", install.as_posix()))
            argv[-1] = "fix code in app.py"
            result = subprocess.run([sys.executable, "-X", "utf8", *argv[1:]], cwd=project,
                                    capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["task_type"], "coding")

    def test_coding_skill_verification_wrapper_from_unrelated_project(self):
        text = (ROOT / "skills/coding/SKILL.md").read_text(encoding="utf-8")
        command = re.search(r"`(python [^`]*run_verification\.py[^`]*)`", text).group(1)
        with tempfile.TemporaryDirectory(prefix="fef verification ") as folder:
            install = Path(folder) / "installed plugin"
            shutil.copytree(ROOT / "scripts", install / "scripts",
                            ignore=shutil.ignore_patterns("__pycache__"))
            project = Path(folder) / "project"
            (project / "scripts").mkdir(parents=True)
            (project / "scripts/run_verification.py").write_text(
                "raise RuntimeError('wrong project wrapper')\n", encoding="utf-8")
            (project / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
            (project / "test_example.py").write_text(
                "import unittest\nclass Example(unittest.TestCase):\n"
                "    def test_sum(self): self.assertEqual(1 + 2, 3)\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=project, check=True,
                           capture_output=True, timeout=30)
            payload = {"session_id": "wrapper-path-test", "cwd": str(project)}
            start = subprocess.run(
                [sys.executable, str(install / "scripts/hooks/session_start.py")],
                input=json.dumps(payload), cwd=project, capture_output=True,
                text=True, encoding="utf-8", timeout=60)
            self.assertEqual(start.returncode, 0, start.stderr)
            self.assertEqual(start.stderr, "")
            command = command.replace("${CLAUDE_PLUGIN_ROOT}", install.as_posix())
            command = command.replace("<verification argv>", "python -m unittest discover -v")
            argv = shlex.split(command)
            argv[0] = sys.executable
            result = subprocess.run(argv, cwd=project, capture_output=True,
                                    text=True, encoding="utf-8", timeout=60)
            recorded = subprocess.run(
                [sys.executable, str(install / "scripts/hooks/record_test_run.py")],
                input=json.dumps({**payload, "tool_name": "Bash",
                                  "tool_input": {"command": shlex.join(argv)},
                                  "tool_response": {"stdout": result.stdout}}),
                cwd=project, capture_output=True, text=True, encoding="utf-8", timeout=60)
            self.assertEqual(recorded.returncode, 0, recorded.stderr)
            self.assertEqual(recorded.stderr, "")
            states = list((project / ".claude/.verification").glob("*.json"))
            self.assertEqual(len(states), 1)
            state = json.loads(states[0].read_text(encoding="utf-8"))
            self.assertEqual(state["verification"]["returncode"], 0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        footer = result.stdout.splitlines()[-1]
        self.assertTrue(footer.startswith("FEF_VERIFY_RESULT="), result.stdout)
        record = json.loads(footer.split("=", 1)[1])
        self.assertEqual(record["returncode"], 0)
        self.assertEqual(record["snapshot_before"], record["snapshot"])
