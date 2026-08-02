import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_skills_ab


def make_arm_root(root: Path) -> None:
    (root / "kernel").mkdir(parents=True)
    (root / "CLAUDE.md").write_text("# entry\n", encoding="utf-8")
    fixture_rel = run_skills_ab.fixture_rel("012")
    dest = root / fixture_rel
    shutil.copytree(ROOT / fixture_rel, dest, ignore=shutil.ignore_patterns("__pycache__"))
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "t@t.t"],
                ["git", "config", "user.name", "T"], ["git", "add", "-A"],
                ["git", "commit", "-qm", "init"]):
        subprocess.run(cmd, cwd=root, check=True, capture_output=True)


class SkillsAbHelperTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.mkdtemp(prefix="skills-ab-test-")
        self.tmp = Path(self._tmp)
        self.arm_root = self.tmp / "arm"
        make_arm_root(self.arm_root)
        self.results_dir = self.tmp / "results"
        self.local_dir = self.tmp / "local"
        self.patches = (
            patch.object(run_skills_ab, "RESULTS_DIR", self.results_dir),
            patch.object(run_skills_ab, "LOCAL_DIR", self.local_dir),
        )
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def run_cli(self, argv):
        return run_skills_ab.main(argv)

    def edit_fixture(self, apply_answer: bool):
        target = self.arm_root / run_skills_ab.fixture_rel("012") / "money.py"
        if apply_answer:
            answer = ROOT / "tests" / "fixtures" / "GT012-code" / "answers" / "money.py"
            target.write_text(answer.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            target.write_text(target.read_text(encoding="utf-8-sig") + "\n# noop\n", encoding="utf-8")

    def test_prepare_resets_fixture_and_prints_prompt(self):
        self.edit_fixture(apply_answer=True)
        code = self.run_cli(["prepare", "--arm", "A", "--arm-root", str(self.arm_root), "--test", "012"])
        self.assertEqual(code, 0)
        restored = (self.arm_root / run_skills_ab.fixture_rel("012") / "money.py").read_text(encoding="utf-8-sig")
        self.assertNotIn("replace", restored)  # buggy pristine restored

    def test_collect_scores_answer_run_as_pass_and_records(self):
        self.edit_fixture(apply_answer=True)
        code = self.run_cli(["collect", "--arm", "B", "--arm-root", str(self.arm_root),
                             "--test", "012", "--run", "1", "--batch", "T1",
                             "--model", "test-model", "--skill-triggered", "yes"])
        self.assertEqual(code, 0)
        batch = json.loads((self.results_dir / "T1.json").read_text(encoding="utf-8"))
        rec = batch["records"][0]
        self.assertEqual(rec["exit_code"], 0)
        self.assertEqual(rec["mechanical_score_cap"], 100)
        self.assertEqual(rec["skill_triggered"], "yes")

    def test_collect_refuses_duplicate_run(self):
        self.edit_fixture(apply_answer=True)
        base = ["collect", "--arm", "B", "--arm-root", str(self.arm_root),
                "--test", "012", "--run", "1", "--batch", "T2"]
        self.assertEqual(self.run_cli(base), 0)
        with self.assertRaises(SystemExit):
            self.run_cli(base)

    def test_report_applies_decision_rule(self):
        self.edit_fixture(apply_answer=True)
        self.run_cli(["collect", "--arm", "A", "--arm-root", str(self.arm_root),
                      "--test", "012", "--run", "1", "--batch", "T3"])
        self.run_cli(["prepare", "--arm", "B", "--arm-root", str(self.arm_root), "--test", "012"])
        self.edit_fixture(apply_answer=True)
        self.run_cli(["collect", "--arm", "B", "--arm-root", str(self.arm_root),
                      "--test", "012", "--run", "1", "--batch", "T3"])
        self.assertEqual(self.run_cli(["report", "--batch", "T3"]), 0)
        batch = json.loads((self.results_dir / "T3.json").read_text(encoding="utf-8"))
        self.assertEqual(len(batch["records"]), 2)

    def test_refuses_arm_root_equal_to_helper_root(self):
        with self.assertRaises(SystemExit):
            self.run_cli(["prepare", "--arm", "A", "--arm-root", str(ROOT), "--test", "012"])

    def test_report_insufficient_when_one_arm_empty(self):
        self.edit_fixture(apply_answer=True)
        self.run_cli(["collect", "--arm", "A", "--arm-root", str(self.arm_root),
                      "--test", "012", "--run", "1", "--batch", "T4"])
        self.assertEqual(self.run_cli(["report", "--batch", "T4"]), 0)


if __name__ == "__main__":
    unittest.main()
