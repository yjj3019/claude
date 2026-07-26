import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scripts.validate_framework as validator


class FrameworkReferenceScopeTest(unittest.TestCase):
    def test_ignores_scratch_markdown_but_checks_docs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "scratch.md").write_text("`docs/missing.md`", encoding="utf-8")
            (root / "docs" / "official.md").write_text("`docs/missing.md`", encoding="utf-8")
            errors = []
            with patch.object(validator, "ROOT", root):
                validator.validate_references(errors)
            self.assertEqual(errors, ["docs\\official.md:1 references missing file: docs/missing.md"])


if __name__ == "__main__":
    unittest.main()
