import unittest

from validators import is_valid_email
from signup import register
from newsletter import subscribe


class EmailValidationTest(unittest.TestCase):
    def test_plain_email_is_valid(self):
        self.assertTrue(is_valid_email("user@example.com"))

    def test_plus_tag_email_is_valid(self):
        self.assertTrue(is_valid_email("user+promo@example.com"))

    def test_missing_at_is_invalid(self):
        self.assertFalse(is_valid_email("userexample.com"))

    def test_signup_accepts_plus_tag_email(self):
        result = register("user+promo@example.com")
        self.assertEqual(result["status"], "registered")

    def test_newsletter_accepts_plus_tag_email(self):
        result = subscribe("user+promo@example.com")
        self.assertTrue(result["subscribed"])


if __name__ == "__main__":
    unittest.main()
