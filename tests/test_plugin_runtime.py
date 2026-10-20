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
        self.assertEqual(manifest["name"], "fef-engineering")
        self.assertEqual(market["name"], "fef-marketplace")
        self.assertEqual(market["renames"]["fef-claude"], manifest["name"])
        self.assertEqual([entry["name"] for entry in market["plugins"]], [manifest["name"]])
        self.assertEqual(market["plugins"][0]["source"], "./plugins/fef-engineering")
        shipped = json.loads((ROOT / "plugins/fef-engineering/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(shipped, manifest)

    def test_unresolved_license_is_not_advertised_as_mit(self):
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("license", manifest)
        self.assertTrue(all("license" not in plugin for plugin in market["plugins"]))

    def test_plugin_skill_names_and_standalone_entry_remain_distinct(self):
        # Only the plugin namespace changes. Keep public skill names and the
        # independently installed pack entry stable for existing consumers.
        for name in ("fef-coding", "fef-rca", "ai-delegation-loop"):
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertRegex(text, rf"(?m)^name: {re.escape(name)}\s*$")
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
        text = (ROOT / "skills/fef-coding/SKILL.md").read_text(encoding="utf-8")
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
