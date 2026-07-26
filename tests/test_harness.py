import unittest

from scripts.lib.routing import detect, load_config, validate_selection
from scripts.run_golden_tests import validate as validate_golden_tests


class HarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()

    def test_representative_routes(self):
        cases = {
            "RHEL 커널 장애 원인을 분석하고 RCA를 작성해줘": ("rca", ["domains/RHEL.md"]),
            "OpenShift 신규 기능을 조사해 고객 제안서로 정리해줘": ("proposal", ["domains/OpenShift.md"]),
            "이 Python 코드의 버그를 최소 변경으로 수정하고 테스트해줘": ("coding", [])
        }
        for task, expected in cases.items():
            with self.subTest(task=task):
                result = detect(task, self.config)
                self.assertEqual((result["task_type"], result["domains"]), expected)
                self.assertEqual(validate_selection(result, self.config), [])

    def test_unmapped_fallback(self):
        result = detect("분류되지 않은 새로운 유형의 작업", self.config)
        self.assertTrue(result["unmapped"])
        self.assertTrue(result["kernel_only_safe"])
        self.assertIsNone(result["module"])

    def test_keyword_boundaries_prevent_substring_false_positives(self):
        for task in ("arcane", "Aesop", "dispatch", "sophisticated design"):
            with self.subTest(task=task):
                self.assertEqual(detect(task, self.config)["task_type"], "unknown")

    def test_common_coding_requests_are_detected(self):
        tasks = (
            "There's a bug in this function, please fix it",
            "Refactor this module",
            "Write unit tests for this module",
            "이 함수에 에러가 있으니 고쳐줘",
            "이 SQL 쿼리를 최적화해줘"
        )
        for task in tasks:
            with self.subTest(task=task):
                self.assertEqual(detect(task, self.config)["task_type"], "coding")

    def test_specific_domains_replace_their_parent_domains(self):
        result = detect(
            "Red Hat Enterprise Linux OpenShift Kubernetes Linux 커널 장애 분석",
            self.config
        )
        self.assertEqual(result["domains"], ["domains/RHEL.md", "domains/OpenShift.md"])
        self.assertEqual(validate_selection(result, self.config), [])

    def test_limit_violation_is_not_silently_trimmed(self):
        result = detect("RHEL OpenShift Ansible 버그를 수정해줘", self.config)
        self.assertIn("domains pack count exceeds limit: 3 > 2", validate_selection(result, self.config))

    def test_golden_metadata(self):
        result = validate_golden_tests()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["test_count"], 24)
        self.assertEqual(result["model_runs_executed"], 0)


if __name__ == "__main__":
    unittest.main()
