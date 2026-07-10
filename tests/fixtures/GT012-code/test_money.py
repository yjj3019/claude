import unittest

from money import parse_money
from orders import total_orders
from refunds import total_refunds


class MoneyParsingTest(unittest.TestCase):
    def test_parse_plain_amount(self):
        self.assertEqual(parse_money("1200"), 1200)

    def test_parse_thousands_separator(self):
        self.assertEqual(parse_money("1,200"), 1200)

    def test_blank_amount_is_zero(self):
        self.assertEqual(parse_money(""), 0)
        self.assertEqual(parse_money(None), 0)

    def test_invalid_non_empty_amount_raises(self):
        with self.assertRaises(ValueError):
            parse_money("not-a-number")

    def test_order_total_uses_shared_parser(self):
        rows = [{"amount": "1,200"}, {"amount": "300"}]
        self.assertEqual(total_orders(rows), 1500)

    def test_refund_total_uses_shared_parser(self):
        rows = [{"refund_amount": "1,200"}, {"refund_amount": "50"}]
        self.assertEqual(total_refunds(rows), 1250)


if __name__ == "__main__":
    unittest.main()
