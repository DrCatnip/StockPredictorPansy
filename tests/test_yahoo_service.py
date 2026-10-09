import unittest
from unittest.mock import Mock, patch

import pandas as pd

from services.yahoo_service import _fetch_market_quote


class FetchMarketQuoteTests(unittest.TestCase):
    @patch("services.yahoo_service.yf.Ticker")
    def test_returns_latest_price_and_change_from_previous_close(self, ticker_factory):
        ticker = Mock()
        ticker.history.return_value = pd.DataFrame(
            {"Close": [100.0, 110.0]},
            index=pd.to_datetime(["2026-10-08", "2026-10-09"]),
        )
        ticker_factory.return_value = ticker

        quote = _fetch_market_quote(("S&P 500", "^GSPC", "USD"))

        self.assertEqual(quote["price"], 110.0)
        self.assertAlmostEqual(quote["change_percent"], 10.0)
        ticker.history.assert_called_once_with(
            period="5d",
            interval="1d",
            auto_adjust=True,
        )

    @patch("services.yahoo_service.yf.Ticker")
    def test_unavailable_quote_does_not_raise(self, ticker_factory):
        ticker_factory.side_effect = RuntimeError("network unavailable")

        quote = _fetch_market_quote(("Gold", "GC=F", "USD"))

        self.assertIsNone(quote["price"])
        self.assertIsNone(quote["change_percent"])
        self.assertEqual(quote["name"], "Gold")


if __name__ == "__main__":
    unittest.main()