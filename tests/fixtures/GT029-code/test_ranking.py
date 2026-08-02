import unittest

from leaderboard import top_entry
from ranking import order_by_id


class RankingTest(unittest.TestCase):
    def test_two_digit_ids_sort_numerically(self):
        entries = [{"id": "10"}, {"id": "9"}, {"id": "2"}]
        self.assertEqual([e["id"] for e in order_by_id(entries)], ["2", "9", "10"])

    def test_top_entry_uses_numeric_order(self):
        entries = [{"id": "10"}, {"id": "9"}]
        self.assertEqual(top_entry(entries)["id"], "9")


if __name__ == "__main__":
    unittest.main()
