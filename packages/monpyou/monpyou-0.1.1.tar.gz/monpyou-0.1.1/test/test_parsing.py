import os
import unittest
from monpyou import MonpYou, Account

TEST_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(TEST_DIR, "test_data")
UEBERSICHT_PATH = os.path.join(TEST_DATA_DIR, "Uebersicht.html")


class TestParsing(unittest.TestCase):

    def test_parse_one_account(self):
        """Test parsing data from an fake account."""
        with open(UEBERSICHT_PATH) as f:
            html = f.read()
        accounts = MonpYou._parse_account_html(html)
        self.assertEqual(1, len(accounts))
        account = accounts[0]
        self.assertEqual('ACCOUNT_NAME', account.name)
        self.assertEqual('ACCOUNT_IBAN', account.iban)
        self.assertEqual('EUR', account.currency)
        self.assertAlmostEqual(12345.67, account.balance)
        self.assertAlmostEqual(12.34, account.interest_sum)
        self.assertAlmostEqual(0.35, account.interest_rate)

    def test_parse_float(self):
        """Test parsing of floats in German notation."""
        self.assertAlmostEqual(1, Account._parse_float('1'))
        self.assertAlmostEqual(1.23, Account._parse_float('1,23'))
        self.assertAlmostEqual(1234, Account._parse_float('1.234,00'))
