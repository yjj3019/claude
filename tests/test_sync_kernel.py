import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync_kernel


def build_repo(root, kernel_body, inlined_body):
    kernel = root / "kernel"
    kernel.mkdir()
    (kernel / "CoreKernel.md").write_text(kernel_body, encoding="utf-8")
    (kernel / "MetaRules.md").write_text("# Meta", encoding="utf-8")
    (kernel / "Checklist.md").write_text("# Checklist", encoding="utf-8")
    (root / "CLAUDE.md").write_text(
        "# Entry\n\n" + sync_kernel.BEGIN + "\n" + inlined_body + "\n" + sync_kernel.END + "\n\n## Tail\n",
        encoding="utf-8",
    )


def patched(root):
    return (
        patch.object(sync_kernel, "ROOT", root),
        patch.object(sync_kernel, "CLAUDE", root / "CLAUDE.md"),
        patch.object(sync_kernel, "KERNEL_FILES",
                     [root / "kernel" / n for n in ("CoreKernel.md", "MetaRules.md", "Checklist.md")]),
    )


class SyncKernelCliTest(unittest.TestCase):
    def run_cli(self, root, argv):
        patches = patched(root)
        with patches[0], patches[1], patches[2]:
            return sync_kernel.main(argv)

    def test_check_mode_detects_drift_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "STALE")
            before = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertEqual(self.run_cli(root, ["--check"]), 1)
            self.assertEqual((root / "CLAUDE.md").read_text(encoding="utf-8"), before)

    def test_check_mode_passes_when_in_sync(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "# Core\n\n# Meta\n\n# Checklist")
            self.assertEqual(self.run_cli(root, ["--check"]), 0)

    def test_write_mode_synchronizes_drifted_block(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "STALE")
            self.assertEqual(self.run_cli(root, []), 0)
            text = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("# Core\n\n# Meta\n\n# Checklist", text)
            self.assertNotIn("STALE", text)
            self.assertEqual(self.run_cli(root, ["--check"]), 0)

    def test_write_mode_skips_write_when_already_in_sync(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "# Core\n\n# Meta\n\n# Checklist")
            claude = root / "CLAUDE.md"
            before = claude.stat().st_mtime_ns
            self.assertEqual(self.run_cli(root, []), 0)
            self.assertEqual(claude.stat().st_mtime_ns, before)

    def test_missing_kernel_file_reports_structured_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "# Core")
            (root / "kernel" / "MetaRules.md").unlink()
            self.assertEqual(self.run_cli(root, ["--check"]), 2)

    def test_malformed_markers_report_structured_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            build_repo(root, "# Core", "# Core")
            (root / "CLAUDE.md").write_text("no markers here", encoding="utf-8")
            self.assertEqual(self.run_cli(root, ["--check"]), 2)


if __name__ == "__main__":
    unittest.main()
