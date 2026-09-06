"""Fence-aware ## section parsing."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location(
    "markdown_sections", SCRIPTS / "markdown_sections.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


SAMPLE = """# Doc

Intro.

## Real One

Body A.

```markdown
## Fake Inside Fence
Outline item
```

## Real Two

Body B.
"""


class FenceAwareSectionTests(unittest.TestCase):
    def test_ignores_headings_inside_fences(self):
        sections = mod.parse_sections(SAMPLE)
        titles = [t for t in sections if t != "__intro__"]
        self.assertEqual(titles, ["Real One", "Real Two"])
        self.assertNotIn("Fake Inside Fence", sections)

    def test_naive_split_would_invent_fake(self):
        # Contrast: naive line-start ## without fence masking invents a section.
        naive = [
            line[3:].strip()
            for line in SAMPLE.splitlines()
            if line.startswith("## ")
        ]
        self.assertIn("Fake Inside Fence", naive)
        self.assertIn("Real One", naive)


if __name__ == "__main__":
    unittest.main()
