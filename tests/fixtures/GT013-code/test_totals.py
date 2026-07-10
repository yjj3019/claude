import unittest

from amounts import parse_amount
from refunds import total_refunds
from revenue import total_revenue


class TotalsTest(unittest.TestCase):
    def test_existing_helper_parses_commas(self):
        self.assertEqual(parse_amount("1,200"), 1200)

    def test_existing_helper_parses_accounting_negative(self):
        self.assertEqual(parse_amount("(1,200)"), -1200)

    def test_revenue_total_uses_existing_helper_behavior(self):
        rows = [{"amount": "1,200"}, {"amount": "300"}]
        self.assertEqual(total_revenue(rows), 1500)

    def test_refund_total_uses_existing_helper_behavior(self):
        rows = [{"refund_amount": "(1,200)"}, {"refund_amount": "50"}]
        self.assertEqual(total_refunds(rows), -1150)


if __name__ == "__main__":
    unittest.main()
