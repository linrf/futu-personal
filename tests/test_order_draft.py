import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from order_draft import build_draft


class OrderDraftTests(unittest.TestCase):
    def make_draft(self, **overrides):
        data = dict(account_id="DEMO", symbol="US.AAPL", side="BUY", quantity="3", limit_price="0.1", currency="USD")
        data.update(overrides)
        return build_draft(**data)

    def test_decimal_amount_and_price_precision(self):
        draft = self.make_draft(limit_price="123.45678900", quantity="100")
        self.assertEqual(draft["limit_price"], "123.45678900")
        self.assertEqual(draft["estimated_notional_excluding_fees"], "12345.67890000")
        self.assertEqual(self.make_draft()["estimated_notional_excluding_fees"], "0.3")

    def test_large_amount_is_not_rounded_by_decimal_context(self):
        price = "123456789012345678901234567890.123456789"
        self.assertEqual(self.make_draft(limit_price=price, quantity="10")["estimated_notional_excluding_fees"], "1234567890123456789012345678901.234567890")

    def test_reject_invalid_or_nonpositive_numbers(self):
        for value in ["NaN", "Infinity", "1e9", "0", "-1", ".", " 1", "1" * 65]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.make_draft(limit_price=value)
        with self.assertRaises(ValueError):
            self.make_draft(quantity="0.5")

    def test_reject_ambiguous_fields(self):
        for override in [dict(account_id=""), dict(account_id="bad\nID"), dict(symbol="AAPL"), dict(side="SELL_SHORT"), dict(currency="usd"), dict(time_in_force="AUTO")]:
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.make_draft(**override)

    def test_cli_emits_an_unsubmitted_manual_draft(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/order_draft.py"), "--account-id", "DEMO", "--symbol", "HK.00700", "--side", "SELL", "--quantity", "100", "--limit-price", "300.125", "--currency", "HKD"], check=True, capture_output=True, text=True)
        draft = json.loads(result.stdout)
        self.assertEqual(draft["status"], "DRAFT_ONLY")
        self.assertEqual(draft["execution"], "manual_in_futu_client")
        self.assertFalse(draft["submitted"])
        self.assertEqual(draft["estimated_notional_excluding_fees"], "30012.500")


if __name__ == "__main__":
    unittest.main()
