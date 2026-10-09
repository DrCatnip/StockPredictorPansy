import unittest
from unittest.mock import AsyncMock, patch

import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app


class StockApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        index = pd.date_range("2025-01-01", periods=80, freq="D")
        close = pd.Series(range(100, 180), index=index, dtype=float)
        cls.history = pd.DataFrame(
            {
                "Open": close - 0.5,
                "High": close + 1,
                "Low": close - 1,
                "Close": close,
                "Volume": 1000,
            },
            index=index,
        )
        cls.metrics = {
            "company_name": "Example Corp",
            "current_price": 179.0,
            "current_price_formatted": "$179.00",
            "day_change": None,
            "market_cap": None,
            "market_cap_formatted": None,
            "pe_ratio": None,
            "volume": None,
            "volume_formatted": None,
            "fifty_two_week_high": None,
            "fifty_two_week_high_formatted": None,
            "fifty_two_week_low": None,
            "fifty_two_week_low_formatted": None,
        }

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_history_rejects_invalid_period(self):
        response = self.client.get("/api/stocks/AAPL/history?period=invalid")

        self.assertEqual(response.status_code, 400)

    @patch("backend.app.routers.stock.StockDataLoader.dashboard_metrics")
    @patch("backend.app.routers.stock._load_history")
    def test_history_returns_candles_and_indicators(self, load_history, dashboard_metrics):
        load_history.return_value = self.history
        dashboard_metrics.return_value = self.metrics

        response = self.client.get("/api/stocks/AAPL/history?period=1y&interval=1d")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["symbol"], "AAPL")
        self.assertEqual(len(payload["candles"]), 80)
        self.assertAlmostEqual(payload["candles"][-1]["sma20"], 169.5)
        self.assertEqual(payload["metrics"]["company_name"], "Example Corp")

    @patch("backend.app.routers.stock._prediction_history", new_callable=AsyncMock)
    @patch("backend.app.routers.stock.predict_stock")
    def test_prediction_returns_model_output(self, predict_stock, load_history):
        load_history.return_value = self.history
        predict_stock.return_value = {
            "symbol": "AAPL",
            "interval": "1d",
            "future_days": 5,
            "predictions": [
                {"date": "2025-03-22", "predicted_close": 181.25}
            ],
        }

        response = self.client.get("/api/stocks/AAPL/predict?future_days=5")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["predictions"][0]["predicted_close"], 181.25)
        predict_stock.assert_called_once()

    def test_prediction_rejects_unsupported_horizon(self):
        response = self.client.get("/api/stocks/AAPL/predict?future_days=7")

        self.assertEqual(response.status_code, 400)

    @patch("backend.app.routers.stock._prediction_history", new_callable=AsyncMock)
    @patch("backend.app.routers.stock.backtest_walk_forward")
    def test_backtest_returns_aggregate_and_window_metrics(self, backtest, load_history):
        load_history.return_value = self.history
        metrics = {"mae": 1.0, "rmse": 1.2, "mape": 0.8}
        backtest.return_value = {
            "symbol": "AAPL",
            "interval": "1d",
            "horizon": 5,
            "windows": 3,
            "starting_training_bars": 65,
            "lstm": metrics,
            "baseline": metrics,
            "window_results": [
                {
                    "window": 1,
                    "training_bars": 65,
                    "test_start_bar": 66,
                    "test_end_bar": 70,
                    "lstm": metrics,
                    "baseline": metrics,
                }
            ],
        }

        response = self.client.get("/api/stocks/AAPL/backtest?horizon=5")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["windows"], 3)
        self.assertEqual(len(response.json()["window_results"]), 1)

    @patch("backend.app.routers.stock.fetch_market_overview")
    def test_market_endpoint_returns_quote_snapshot(self, fetch_markets):
        fetch_markets.return_value = [
            {
                "name": "S&P 500",
                "symbol": "^GSPC",
                "currency": "USD",
                "price": 6000.0,
                "change_percent": 0.5,
            }
        ]

        response = self.client.get("/api/markets")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["quotes"][0]["price"], 6000.0)


if __name__ == "__main__":
    unittest.main()