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
            "Optimize this SQL query",
            "이 함수에 에러가 있으니 고쳐줘",
            "이 SQL 쿼리를 최적화해줘"
        )
        for task in tasks:
            with self.subTest(task=task):
                self.assertEqual(detect(task, self.config)["task_type"], "coding")

    def test_generic_fix_words_do_not_override_specific_routes(self):
        cases = {
            "장애 원인을 분석하고 오류를 수정해줘": "rca",
            "RCA 보고서의 오류를 수정해줘": "rca",
            "제안서 오류를 수정해줘": "proposal",
            "아키텍처 검토하고 문제를 수정해줘": "architecture_review",
            "이 프롬프트 검토하고 오류 수정해줘": "prompt_review",
            "Fix the error in this incident report": "rca"
        }
        for task, expected in cases.items():
            with self.subTest(task=task):
                self.assertEqual(detect(task, self.config)["task_type"], expected)

    def test_specific_domains_replace_their_parent_domains(self):
        result = detect(
            "Red Hat Enterprise Linux OpenShift Kubernetes Linux 커널 장애 분석",
            self.config
        )
        self.assertEqual(result["domains"], ["domains/RHEL.md", "domains/OpenShift.md"])
        self.assertEqual(validate_selection(result, self.config), [])

    def test_domain_overflow_keeps_top2_with_explicit_warning(self):
        """R2-P1-DOMAIN-OVERFLOW: top-2 + warning naming drops (not silent trim)."""
        result = detect("RHEL OpenShift Ansible 버그를 수정해줘", self.config)
        self.assertEqual(validate_selection(result, self.config), [])
        self.assertEqual(len(result["domains"]), 2)
        self.assertIn("domains/RHEL.md", result["domains"])
        self.assertIn("domains/OpenShift.md", result["domains"])
        self.assertTrue(any("dropped: domains/Ansible.md" in w for w in result["warnings"]))
        # Integrity policies on coding route retained
        self.assertIn("policies/FileHandling.md", result["policies"])
        self.assertIn("policies/ToolExecution.md", result["policies"])

    def test_coding_fallback_does_not_overfire_on_qa_or_typo(self):
        """R2-P1-FALLBACK-OVERFIRE"""
        for task in (
            "what is the error budget concept?",
            "이 문서의 오탈자 수정해",
        ):
            with self.subTest(task=task):
                result = detect(task, self.config)
                self.assertNotEqual(result["task_type"], "coding")
                self.assertIsNone(result.get("workflow"))

    def test_unmapped_high_risk_gets_minimal_safety(self):
        """R2-P0-UNMAPPED-HIGHRISK"""
        result = detect(
            "운영 환경에서 고객 데이터 마이그레이션 계획 검토",
            self.config,
        )
        self.assertTrue(result["unmapped"])
        self.assertEqual(result["risk_level"], "high")
        self.assertFalse(result["kernel_only_safe"])
        self.assertIn("policies/Evidence.md", result["policies"])
        self.assertTrue(any("High-risk unmapped" in w for w in result["warnings"]))


    def test_high_risk_requires_action_signal(self):
        """S3-06: keyword-only trivia/definition asks stay low."""
        for task in (
            "고객센터 전화번호 좀 알려줘",
            "production 이라는 단어 뜻이 뭐야?",
            "보안 그룹 이름 규칙이 뭐야?",
        ):
            with self.subTest(task=task):
                result = detect(task, self.config)
                self.assertNotEqual(result["risk_level"], "high")
                self.assertTrue(result.get("kernel_only_safe", True) or result["risk_level"] != "high")

    def test_genuine_high_risk_migration_plan_stays_high(self):
        """S3-06: action+keyword genuine ask stays high with Evidence."""
        result = detect(
            "운영 환경에서 고객 데이터 마이그레이션 계획 검토",
            self.config,
        )
        self.assertEqual(result["risk_level"], "high")
        self.assertFalse(result["kernel_only_safe"])
        self.assertIn("policies/Evidence.md", result["policies"])

    def test_also_matched_exposes_dropped_high_risk_route(self):
        """S3-05: also_matched + warning when a dropped route is high-risk."""
        # rca (high) + security_review (high) both match; one is selected
        result = detect(
            "security review and root cause analysis of the outage",
            self.config,
        )
        self.assertIn("also_matched", result)
        self.assertTrue(isinstance(result["also_matched"], list))
        if result["also_matched"]:
            high_dropped = [m for m in result["also_matched"] if m.get("risk_level") == "high"]
            if high_dropped:
                self.assertTrue(
                    any("Multi-intent" in w and "high-risk" in w for w in result["warnings"])
                )

    def test_golden_metadata(self):
        result = validate_golden_tests()
        self.assertTrue(result["valid"], result["errors"])
        self.assertEqual(result["test_count"], 31)
        self.assertEqual(result["model_runs_executed"], 0)


if __name__ == "__main__":
    unittest.main()
