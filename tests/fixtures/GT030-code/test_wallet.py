import unittest

from statements import statement_line
from wallet import charge_total


class WalletTest(unittest.TestCase):
    def test_cents_add_exactly(self):
        self.assertEqual(charge_total([0.10, 0.20]), 0.30)

    def test_repeated_cents_stay_exact(self):
        self.assertEqual(charge_total([0.10] * 3), 0.30)

    def test_statement_prints_exact_total(self):
        self.assertEqual(statement_line([0.10, 0.20]), "TOTAL: 0.3")


if __name__ == "__main__":
    unittest.main()
