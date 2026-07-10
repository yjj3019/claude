import unittest

from billing import billable_events
from periods import is_within_period
from support import entitled_tickets


class PeriodBoundaryTest(unittest.TestCase):
    def test_start_date_is_included(self):
        self.assertTrue(is_within_period("2026-07-01", "2026-07-01", "2026-07-31"))

    def test_end_date_is_included(self):
        self.assertTrue(is_within_period("2026-07-31", "2026-07-01", "2026-07-31"))

    def test_day_after_end_is_excluded(self):
        self.assertFalse(is_within_period("2026-08-01", "2026-07-01", "2026-07-31"))

    def test_billing_includes_end_date_event(self):
        events = [{"day": "2026-07-30"}, {"day": "2026-07-31"}]
        self.assertEqual(len(billable_events(events, "2026-07-01", "2026-07-31")), 2)

    def test_support_includes_end_date_ticket(self):
        tickets = [{"day": "2026-07-31"}, {"day": "2026-08-01"}]
        self.assertEqual(len(entitled_tickets(tickets, "2026-07-01", "2026-07-31")), 1)


if __name__ == "__main__":
    unittest.main()
