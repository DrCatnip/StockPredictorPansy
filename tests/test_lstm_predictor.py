import unittest
from unittest.mock import patch

import numpy as np

from services.lstm_predictor import backtest_walk_forward, validate_close_prices


class ValidateClosePricesTests(unittest.TestCase):
    def test_accepts_more_than_lookback(self):
        prices = validate_close_prices(np.arange(61, dtype=float))

        self.assertEqual(prices.shape, (61, 1))

    def test_rejects_insufficient_history(self):
        with self.assertRaisesRegex(ValueError, "Need more than 60 data points"):
            validate_close_prices(np.arange(60, dtype=float))

    def test_rejects_non_finite_values(self):
        prices = np.arange(61, dtype=float)
        prices[10] = np.nan

        with self.assertRaisesRegex(ValueError, "missing or infinite"):
            validate_close_prices(prices)

    @patch("services.lstm_predictor.predict_stock")
    def test_walk_forward_uses_chronological_windows(self, predict_stock):
        prices = np.arange(1, 122, dtype=float)
        predict_stock.side_effect = [
            np.arange(107, 112, dtype=float).reshape(-1, 1),
            np.arange(112, 117, dtype=float).reshape(-1, 1),
            np.arange(117, 122, dtype=float).reshape(-1, 1),
        ]

        result = backtest_walk_forward(prices, horizon=5, windows=3)

        self.assertEqual(result["starting_training_bars"], 106)
        self.assertEqual(result["windows"], 3)
        self.assertEqual(result["lstm"]["mae"], 0)
        self.assertEqual(result["baseline"]["mae"], 3)
        self.assertEqual(len(result["window_results"]), 3)
        self.assertEqual(predict_stock.call_count, 3)
        np.testing.assert_array_equal(
            predict_stock.call_args_list[0].args[0][:, 0],
            np.arange(1, 107, dtype=float),
        )
        np.testing.assert_array_equal(
            predict_stock.call_args_list[1].args[0][:, 0],
            np.arange(1, 112, dtype=float),
        )
        np.testing.assert_array_equal(
            predict_stock.call_args_list[2].args[0][:, 0],
            np.arange(1, 117, dtype=float),
        )
        self.assertEqual(predict_stock.call_args.kwargs["future_days"], 5)

    def test_walk_forward_rejects_insufficient_training_data(self):
        with self.assertRaisesRegex(ValueError, "needs at least 76 total bars"):
            backtest_walk_forward(np.arange(75, dtype=float), horizon=5, windows=3)


if __name__ == "__main__":
    unittest.main()