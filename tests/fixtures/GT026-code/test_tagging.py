import unittest

from reports import tag_records
from tagging import add_tag


class TaggingTest(unittest.TestCase):
    def test_each_call_starts_fresh(self):
        self.assertEqual(add_tag("a"), ["a"])
        self.assertEqual(add_tag("b"), ["b"])

    def test_records_do_not_share_tag_lists(self):
        records = [{"tag": "x"}, {"tag": "y"}]
        self.assertEqual(tag_records(records), [["x"], ["y"]])

    def test_explicit_list_is_still_appended(self):
        self.assertEqual(add_tag("c", ["a", "b"]), ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
