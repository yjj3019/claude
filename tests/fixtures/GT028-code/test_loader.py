import unittest

from loader import RAW_EXPORT, parse_export
from summary import names


class LoaderBomTest(unittest.TestCase):
    def test_first_header_is_clean(self):
        rows = parse_export(RAW_EXPORT)
        self.assertIn("name", rows[0])

    def test_names_are_extracted(self):
        self.assertEqual(names(), ["alice", "bob"])

    def test_bom_free_input_still_works(self):
        rows = parse_export("name,score\ncarol,3\n")
        self.assertEqual(rows[0]["name"], "carol")


if __name__ == "__main__":
    unittest.main()
