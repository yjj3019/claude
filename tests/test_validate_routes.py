import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_routes import (  # noqa: E402
    check_row_mandatory_packs,
    mandatory_paths_in_row,
    route_mandatory_paths,
)


class MandatoryPathsInRowTest(unittest.TestCase):
    def test_plain_backtick_path_is_mandatory(self):
        row = "| Coding | `modules/Coding.md` | None | `workflows/CodingWorkflow.md` | `reviewers/CodeChangeReviewer.md` | `policies/FileHandling.md` |"
        self.assertEqual(
            mandatory_paths_in_row(row),
            {"modules/Coding.md", "workflows/CodingWorkflow.md", "reviewers/CodeChangeReviewer.md", "policies/FileHandling.md"},
        )

    def test_optional_prefixed_path_is_excluded(self):
        row = "| Research | `modules/Research.md` | None | `workflows/ResearchWorkflow.md` | optional `reviewers/TechnicalReviewer.md` | `policies/Evidence.md` |"
        self.assertEqual(
            mandatory_paths_in_row(row),
            {"modules/Research.md", "workflows/ResearchWorkflow.md", "policies/Evidence.md"},
        )

    def test_domain_paths_are_ignored(self):
        row = "| Manual | `modules/Manual.md` | `domains/RHEL.md` | `workflows/ManualWorkflow.md` | `reviewers/DocumentationReviewer.md` | `policies/Writing.md` |"
        self.assertNotIn("domains/RHEL.md", mandatory_paths_in_row(row))


class CheckRowMandatoryPacksTest(unittest.TestCase):
    def make_route(self, **overrides):
        route = {
            "id": "coding",
            "module": "modules/Coding.md",
            "workflow": "workflows/CodingWorkflow.md",
            "reviewer": "reviewers/CodeChangeReviewer.md",
            "policies": ["policies/FileHandling.md"],
        }
        route.update(overrides)
        return route

    def test_matching_row_has_no_errors(self):
        route = self.make_route()
        row = "| Code modification | `modules/Coding.md` | None | `workflows/CodingWorkflow.md` | `reviewers/CodeChangeReviewer.md` | `policies/FileHandling.md` |"
        self.assertEqual(check_row_mandatory_packs(route, row), [])

    def test_row_missing_a_mandatory_pack_is_flagged(self):
        route = self.make_route()
        row = "| Code modification | `modules/Coding.md` | None | `workflows/CodingWorkflow.md` | optional `reviewers/CodeChangeReviewer.md` for big changes | `policies/FileHandling.md` |"
        errors = check_row_mandatory_packs(route, row)
        self.assertEqual(len(errors), 1)
        self.assertIn("reviewers/CodeChangeReviewer.md", errors[0])

    def test_route_mandatory_paths_omits_null_reviewer(self):
        route = self.make_route(reviewer=None)
        self.assertNotIn(None, route_mandatory_paths(route))


class DocumentFallbackTest(unittest.TestCase):
    def test_document_tasks_select_existing_guidance(self):
        from lib.routing import detect, load_config, validate_selection
        config = load_config()
        cases = (
            ("Translate this PDF paper into Korean", "pdf_translation", "policies/FileHandling.md"),
            ("이 PDF 논문을 한국어로 번역해줘", "pdf_translation", "policies/FileHandling.md"),
            ("Proofread this Korean paragraph", "korean_proofreading", "policies/Writing.md"),
            ("이 문장의 맞춤법을 교정해줘", "korean_proofreading", "policies/Writing.md"),
            ("Edit the table in existing HWPX document", "formatted_document_edit", "policies/FileHandling.md"),
            ("기존 HWPX 문서의 표를 수정해줘", "formatted_document_edit", "policies/FileHandling.md"),
            ("HWPX 파일의 표 편집해줘", "formatted_document_edit", "policies/FileHandling.md"),
        )
        for task, expected, policy in cases:
            with self.subTest(task=task):
                result = detect(task, config)
                self.assertEqual(result["task_type"], expected)
                self.assertIn(policy, result["policies"])
                self.assertEqual(validate_selection(result, config), [])

    def test_fallback_does_not_override_other_or_high_risk_tasks(self):
        from lib.routing import detect, load_config
        config = load_config()
        for task, expected in (("fix code in PDF parser", "coding"),
                               ("security review of HWPX document", "security_review"),
                               ("What is a PDF?", "unknown"),
                               ("Edit HWPX conversion code", "unknown"),
                               ("Edit HWPX document parser in app.py", "unknown")):
            with self.subTest(task=task):
                self.assertEqual(detect(task, config)["task_type"], expected)

    def test_document_fallback_handles_missing_code_path_patterns(self):
        from lib.routing import detect, load_config
        config = load_config()
        coding = next(route for route in config["routes"] if route["id"] == "coding")
        coding["fallback_requires_pattern"] = []
        result = detect("Translate this PDF paper into Korean", config)
        self.assertEqual(result["task_type"], "pdf_translation")

    def test_korean_table_keyword_does_not_match_standard(self):
        from lib.routing import detect, load_config
        result = detect("HWPX 표준을 수정해줘", load_config())
        self.assertEqual(result["task_type"], "unknown")

    def test_high_risk_and_ambiguous_requests_remain_unmapped(self):
        from lib.routing import detect, load_config
        config = load_config()
        proofread = detect("Proofread Korean README.md", config)
        self.assertIn("policies/FileHandling.md", proofread["policies"])
        high_risk = detect("고객 PDF 논문 번역해줘", config)
        self.assertEqual(high_risk["task_type"], "unknown")
        self.assertEqual(high_risk["risk_level"], "high")
        self.assertFalse(high_risk["kernel_only_safe"])
        ambiguous = detect("Translate PDF paper and edit HWPX document", config)
        self.assertEqual(ambiguous["task_type"], "unknown")



if __name__ == "__main__":
    unittest.main()
