import unittest
from unittest.mock import Mock, patch

import pandas as pd

from backend.app.services.yahoo_service import _download_chart, fetch_market_quote


class YahooChartTests(unittest.TestCase):
    @patch("backend.app.services.yahoo_service.requests.get")
    def test_download_chart_parses_adjusted_ohlcv_and_exchange_dates(self, get):
        response = Mock()
        response.json.return_value = {
            "chart": {
                "result": [
                    {
                        "meta": {"exchangeTimezoneName": "America/New_York", "longName": "Example Corp"},
                        "timestamp": [1791466200, 1791552600],
                        "indicators": {
                            "quote": [
                                {
                                    "open": [100, 110],
                                    "high": [105, 115],
                                    "low": [99, 109],
                                    "close": [102, 112],
                                    "volume": [1000, 2000],
                                }
                            ],
                            "adjclose": [{"adjclose": [51, 56]}],
                        },
                    }
                ],
                "error": None,
            }
        }
        get.return_value = response

        frame, metadata = _download_chart("AAPL", "5d", "1d")

        response.raise_for_status.assert_called_once_with()
        self.assertEqual(frame.index.strftime("%Y-%m-%d").tolist(), ["2026-10-08", "2026-10-09"])
        self.assertEqual(frame["Open"].tolist(), [50.0, 55.0])
        self.assertEqual(frame["Close"].tolist(), [51.0, 56.0])
        self.assertEqual(metadata["longName"], "Example Corp")

    @patch("backend.app.services.yahoo_service._download_chart")
    def test_market_quote_uses_last_two_closes(self, download_chart):
        download_chart.return_value = (
            pd.DataFrame({"Close": [100.0, 110.0]}),
            {},
        )

        quote = fetch_market_quote(("S&P 500", "^GSPC", "USD"))

        self.assertEqual(quote["price"], 110.0)
        self.assertAlmostEqual(quote["change_percent"], 10.0)


if __name__ == "__main__":
    unittest.main()