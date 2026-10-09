from __future__ import annotations

import hashlib
import os
from typing import Any

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
import pandas as pd
from keras.layers import LSTM, Dense, Input
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler

from backend.app.core.cache import model_cache
from backend.app.core.constants import MODEL_CACHE_TTL, TIME_STEP


def validate_close_prices(close_prices: Any) -> np.ndarray:
    try:
        prices = np.asarray(close_prices, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Close prices must contain numeric values.") from exc

    if prices.ndim == 1:
        prices = prices.reshape(-1, 1)
    if prices.ndim != 2 or prices.shape[1] != 1:
        raise ValueError("Close prices must be a one-dimensional series.")
    if not np.isfinite(prices).all():
        raise ValueError("Close prices must not contain missing or infinite values.")
    if len(prices) <= TIME_STEP:
        raise ValueError(
            f"Need more than {TIME_STEP} data points to train the model "
            f"(got {len(prices)}). Choose a longer period or a smaller interval."
        )
    return np.ascontiguousarray(prices)


def _prepare_data(close_prices: np.ndarray):
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(close_prices)
    x_train = np.asarray(
        [scaled_data[index - TIME_STEP:index] for index in range(TIME_STEP, len(scaled_data))]
    )
    y_train = scaled_data[TIME_STEP:]
    return x_train, y_train, scaler, scaled_data


def _build_model(input_shape: tuple[int, int]) -> Sequential:
    model = Sequential(
        [
            Input(shape=input_shape),
            LSTM(64, return_sequences=True),
            LSTM(64),
            Dense(32),
            Dense(1),
        ]
    )
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


def _predict_future(model, scaler, scaled_data: np.ndarray, days: int) -> np.ndarray:
    batch = scaled_data[-TIME_STEP:].reshape(1, TIME_STEP, 1)
    predictions = []
    for _ in range(days):
        prediction = model.predict(batch, verbose=0)[0][0]
        predictions.append(prediction)
        batch = np.concatenate((batch[:, 1:, :], [[[prediction]]]), axis=1)
    return scaler.inverse_transform(np.asarray(predictions).reshape(-1, 1))


def _market_dates(last_date: pd.Timestamp, count: int, interval: str) -> list[pd.Timestamp]:
    if interval == "1wk":
        return [last_date + pd.Timedelta(weeks=step) for step in range(1, count + 1)]
    if interval == "1mo":
        return [last_date + pd.DateOffset(months=step) for step in range(1, count + 1)]
    return [last_date + pd.offsets.BDay(step) for step in range(1, count + 1)]


def predict_stock(
    symbol: str,
    period: str,
    interval: str,
    history: pd.DataFrame,
    future_days: int,
    epochs: int,
) -> dict:
    prices = validate_close_prices(history["Close"].to_numpy())
    fingerprint = hashlib.sha256(prices.tobytes()).hexdigest()
    key = ("lstm", symbol, period, interval, epochs, fingerprint)

    def _train():
        x_train, y_train, scaler, scaled_data = _prepare_data(prices)
        model = _build_model((TIME_STEP, 1))
        model.fit(x_train, y_train, epochs=epochs, batch_size=32, verbose=0)
        return model, scaler, scaled_data

    model, scaler, scaled_data = model_cache.get_or_set(key, MODEL_CACHE_TTL, _train)
    values = _predict_future(model, scaler, scaled_data, future_days)
    last_date = pd.Timestamp(history.index[-1])
    dates = _market_dates(last_date, future_days, interval)
    return {
        "symbol": symbol,
        "interval": interval,
        "future_days": future_days,
        "predictions": [
            {"date": date.strftime("%Y-%m-%d"), "predicted_close": round(float(value[0]), 2)}
            for date, value in zip(dates, values)
        ],
    }


def _score(actual: np.ndarray, predicted: np.ndarray) -> dict:
    errors = predicted - actual
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(np.square(errors)))),
        "mape": (
            float(np.mean(np.abs(errors / actual)) * 100)
            if np.all(actual != 0)
            else None
        ),
    }


def backtest_walk_forward(
    symbol: str,
    period: str,
    interval: str,
    history: pd.DataFrame,
    horizon: int,
    windows: int = 3,
    epochs: int = 10,
) -> dict:
    prices = validate_close_prices(history["Close"].to_numpy())
    starting_training_bars = len(prices) - horizon * windows
    if starting_training_bars <= TIME_STEP:
        required = TIME_STEP + 1 + horizon * windows
        raise ValueError(
            f"A {windows}-window backtest with a {horizon}-bar horizon needs "
            f"at least {required} total bars. Choose a longer period or a shorter horizon."
        )

    actual_windows = []
    prediction_windows = []
    baseline_windows = []
    window_results = []
    for window_index in range(windows):
        training_end = starting_training_bars + window_index * horizon
        test_end = training_end + horizon
        training_history = history.iloc[:training_end]
        actual = prices[training_end:test_end, 0]

        result = predict_stock(
            symbol,
            period,
            interval,
            training_history,
            horizon,
            epochs,
        )
        predictions = np.asarray(
            [point["predicted_close"] for point in result["predictions"]],
            dtype=float,
        )
        if len(predictions) != horizon or not np.isfinite(predictions).all():
            raise ValueError(f"The model returned invalid predictions for window {window_index + 1}.")

        baseline = np.full(horizon, prices[training_end - 1, 0])
        actual_windows.append(actual)
        prediction_windows.append(predictions)
        baseline_windows.append(baseline)
        window_results.append(
            {
                "window": window_index + 1,
                "training_bars": training_end,
                "test_start_bar": training_end + 1,
                "test_end_bar": test_end,
                "lstm": _score(actual, predictions),
                "baseline": _score(actual, baseline),
            }
        )

    actual_all = np.concatenate(actual_windows)
    predictions_all = np.concatenate(prediction_windows)
    baseline_all = np.concatenate(baseline_windows)
    return {
        "symbol": symbol,
        "interval": interval,
        "horizon": horizon,
        "windows": windows,
        "starting_training_bars": starting_training_bars,
        "lstm": _score(actual_all, predictions_all),
        "baseline": _score(actual_all, baseline_all),
        "window_results": window_results,
    }