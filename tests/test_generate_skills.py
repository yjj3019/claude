import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_skills


class GenerateSkillsTest(unittest.TestCase):
    def test_committed_skills_match_routes_json(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_skills.py"), "--check"],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_every_route_has_a_skill_with_trigger_keywords(self):
        config = generate_skills.load_config()
        expected = generate_skills.expected_skills(config)
        self.assertEqual(len(expected), len(config["routes"]))
        for route in config["routes"]:
            name = "fef-" + route["id"].replace("_", "-")
            self.assertIn(name, expected)
            content = expected[name]
            for keyword in route["keywords"]:
                self.assertIn(keyword, content)
            self.assertIn(route["module"], content)
            self.assertIn(route["workflow"], content)
            for policy in route["policies"]:
                self.assertIn(policy, content)

    def test_reviewer_once_rule_present_when_reviewer_exists(self):
        config = generate_skills.load_config()
        expected = generate_skills.expected_skills(config)
        for route in config["routes"]:
            name = "fef-" + route["id"].replace("_", "-")
            if route.get("reviewer"):
                self.assertIn("at most once per artifact", expected[name])
            else:
                self.assertIn("none for this route", expected[name])

    def test_check_mode_detects_stale_skill(self):
        target = ROOT / ".claude" / "skills" / "fef-rca" / "SKILL.md"
        original = target.read_text(encoding="utf-8")
        try:
            target.write_text(original + "\n# DRIFT\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_skills.py"), "--check"],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("stale skill: fef-rca", proc.stderr)
        finally:
            target.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
