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

    def test_limit_violation_is_not_silently_trimmed(self):
        result = detect("버그를 수정해줘", self.config)
        result["domains"] = ["domains/RHEL.md", "domains/Linux.md", "domains/OpenShift.md"]
        self.assertIn("domains pack count exceeds limit: 3 > 2", validate_selection(result, self.config))

    def test_golden_metadata(self):
        result = validate_golden_tests()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["test_count"], 23)
        self.assertEqual(result["model_runs_executed"], 0)


if __name__ == "__main__":
    unittest.main()
