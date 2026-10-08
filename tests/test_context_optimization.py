"""Default routes omit duplicate procedures without losing integrity policies."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lib.routing import detect, load_config


class CompactRouteTest(unittest.TestCase):
    def test_coding_keeps_execution_contract_without_duplicate_workflow(self):
        selection = detect("fix code in app.py", load_config())
        self.assertEqual(selection["module"], "modules/Coding.md")
        self.assertIsNone(selection["workflow"])
        self.assertIsNone(selection["reviewer"])
        self.assertFalse(selection["kernel_only_safe"])
        self.assertTrue({"policies/FileHandling.md", "policies/ToolExecution.md"}
                        <= set(selection["policies"]))

    def test_research_keeps_evidence_and_freshness_without_duplicate_workflow(self):
        selection = detect("current version research", load_config())
        self.assertEqual(selection["module"], "modules/Research.md")
        self.assertIsNone(selection["workflow"])
        self.assertTrue({"policies/Evidence.md", "policies/Freshness.md"}
                        <= set(selection["policies"]))

    def test_explicit_security_review_still_loads_security_reviewer(self):
        selection = detect("security review", load_config())
        self.assertEqual(selection["reviewer"], "reviewers/SecurityReviewer.md")
        self.assertFalse(selection["kernel_only_safe"])


if __name__ == "__main__":
    unittest.main()
