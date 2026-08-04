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


if __name__ == "__main__":
    unittest.main()
