import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scripts.validate_framework as validator


class FrameworkReferenceScopeTest(unittest.TestCase):
    def test_model_floor_does_not_require_removed_model(self):
        self.assertEqual(self._validate_model_floor("## Model-Invariant Floor\nOpus Sonnet Haiku\nescalate the model"), [])

    def test_model_floor_still_requires_integrity_guidance(self):
        errors = self._validate_model_floor("Opus Sonnet Haiku\nescalate the model")
        self.assertTrue(any("## Model-Invariant Floor" in error for error in errors))

    def _validate_model_floor(self, guide):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docs").mkdir()
            (root / "scripts").mkdir()
            (root / "docs" / "model-usage.md").write_text(guide, encoding="utf-8")
            (root / "CLAUDE.md").write_text("## Context Budget\nModel-Invariant Floor loading-map", encoding="utf-8")
            (root / "AGENTS.md").write_text("CLAUDE.md Guidance Layout", encoding="utf-8")
            (root / "scripts" / "install_pack.py").touch()
            errors = []
            with patch.object(validator, "ROOT", root):
                validator.validate_context_and_model_floor(errors)
            return errors

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
            original = target.read_bytes()
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
                target.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
