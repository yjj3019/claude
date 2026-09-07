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
            source = str(Path("docs") / "official.md")
            self.assertEqual(errors, [f"{source}:1 references missing file: docs/missing.md"])


class PackContentFloorTests(unittest.TestCase):
    """A pack reduced to its heading must fail validation."""

    def test_current_packs_clear_their_floors(self):
        errors: list[str] = []
        validator.validate_pack_content(errors)
        self.assertEqual(errors, [])

    def test_gutted_pack_is_rejected(self):
        for folder in validator.PACK_CONTENT_FLOORS:
            target = sorted((validator.ROOT / folder).glob("*.md"))[0]
            original = target.read_text(encoding="utf-8")
            try:
                target.write_text(f"# {target.stem}\n", encoding="utf-8")
                errors: list[str] = []
                validator.validate_pack_content(errors)
                rel = target.relative_to(validator.ROOT).as_posix()
                self.assertTrue(
                    any(rel in e for e in errors),
                    f"gutting {rel} produced no error: {errors}",
                )
            finally:
                target.write_text(original, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
