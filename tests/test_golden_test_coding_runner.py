import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_golden_test_coding as runner


def overlay_answers(edited_dir, test_id):
    answers = runner.ROOT / "tests" / "fixtures" / runner.TEST_CONFIG[test_id]["fixture"] / "answers"
    for py in sorted(answers.glob("*.py")):
        shutil.copy(py, edited_dir / py.name)


class CodingRunnerScoreTest(unittest.TestCase):
    def setUp(self):
        self._dirs = []

    def tearDown(self):
        for d in self._dirs:
            shutil.rmtree(d, ignore_errors=True)

    def fresh_pair(self, test_id):
        pristine = runner.copy_fixture(test_id)
        edited = Path(tempfile.mkdtemp(prefix="gt" + test_id + "-test-edited-"))
        shutil.copytree(pristine, edited, dirs_exist_ok=True)
        self._dirs.extend([pristine, edited])
        return pristine, edited

    def test_answer_files_reach_full_mechanical_cap(self):
        for test_id in sorted(runner.TEST_CONFIG):
            with self.subTest(test=test_id):
                pristine, edited = self.fresh_pair(test_id)
                overlay_answers(edited, test_id)
                result = runner.score(test_id, pristine, edited)
                self.assertEqual(result["mechanical_score_cap"], 100, result["cap_reasons"])
                self.assertTrue(result["mechanical_checks"]["unit_tests_pass"])
                self.assertTrue(result["mechanical_checks"]["fix_files_touched"])
                self.assertFalse(result["mechanical_checks"]["caller_only_fix"])

    def test_gt013_caller_dedup_answer_is_not_penalized_as_caller_only(self):
        # Regression: the correct GT013 patch changes only refunds.py/revenue.py
        # (the duplication sites). The old config treated amounts.py as the
        # root-cause file and capped this correct patch at 55.
        pristine, edited = self.fresh_pair("013")
        overlay_answers(edited, "013")
        result = runner.score("013", pristine, edited)
        self.assertFalse(result["mechanical_checks"]["caller_only_fix"])
        self.assertEqual(result["mechanical_score_cap"], 100)

    def test_pristine_copy_caps_at_40(self):
        pristine, edited = self.fresh_pair("012")
        result = runner.score("012", pristine, edited)
        self.assertEqual(result["mechanical_score_cap"], 40)
        self.assertIn("no code change detected in fixture directory", result["cap_reasons"])

    def test_sibling_only_change_flags_caller_only_fix(self):
        pristine, edited = self.fresh_pair("012")
        target = edited / "orders.py"
        target.write_text(target.read_text(encoding="utf-8-sig") + "\n# workaround\n", encoding="utf-8")
        result = runner.score("012", pristine, edited)
        self.assertTrue(result["mechanical_checks"]["caller_only_fix"])
        self.assertLessEqual(result["mechanical_score_cap"], 55)

    def test_test_file_modification_is_flagged(self):
        pristine, edited = self.fresh_pair("012")
        overlay_answers(edited, "012")
        target = edited / "test_money.py"
        target.write_text(target.read_text(encoding="utf-8-sig") + "\n# tweak\n", encoding="utf-8")
        result = runner.score("012", pristine, edited)
        self.assertTrue(result["mechanical_checks"]["test_file_modified"])
        self.assertLessEqual(result["mechanical_score_cap"], 50)

    def test_new_third_party_import_is_flagged(self):
        pristine, edited = self.fresh_pair("012")
        overlay_answers(edited, "012")
        target = edited / "money.py"
        target.write_text(
            target.read_text(encoding="utf-8") + "\nif False:\n    import totally_fake_pkg\n",
            encoding="utf-8",
        )
        result = runner.score("012", pristine, edited)
        self.assertIn("totally_fake_pkg", result["mechanical_checks"]["new_dependency_candidates"])
        self.assertLessEqual(result["mechanical_score_cap"], 70)

    def test_copy_fixture_excludes_answers_directory(self):
        pristine = runner.copy_fixture("012")
        self._dirs.append(pristine)
        self.assertFalse((pristine / "answers").exists())


if __name__ == "__main__":
    unittest.main()
