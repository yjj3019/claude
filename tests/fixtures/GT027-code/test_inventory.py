import unittest

import inventory
from audit import audit_report


class InventoryAliasTest(unittest.TestCase):
    def test_audit_report_is_sorted_and_marked(self):
        self.assertEqual(audit_report(), ["battery", "cable", "charger", "AUDITED"])

    def test_audit_does_not_mutate_live_inventory(self):
        audit_report()
        self.assertEqual(inventory.list_items(), ["battery", "cable", "charger"])
        self.assertEqual(inventory.item_count(), 3)


if __name__ == "__main__":
    unittest.main()
