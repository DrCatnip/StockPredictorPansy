import json
from typing import Any

import yfinance as yf

from services.lstm_predictor import backtest_walk_forward

SYMBOLS = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL"]
HORIZONS = [5, 10, 30]
WINDOWS = 2
EPOCHS = 5


def run_benchmark() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for symbol in SYMBOLS:
        history = yf.download(
            symbol,
            period="2y",
            interval="1d",
            auto_adjust=True,
            progress=False,
        )
        prices = history["Close"].dropna().to_numpy(dtype=float)

        if len(prices) < 200:
            print(f"{symbol}: insufficient data ({len(prices)})")
            continue

        for horizon in HORIZONS:
            try:
                result = backtest_walk_forward(
                    prices,
                    horizon=horizon,
                    windows=WINDOWS,
                    epochs=EPOCHS,
                )
                lstm_mae = float(result["lstm"]["mae"])
                baseline_mae = float(result["baseline"]["mae"])
                delta = baseline_mae - lstm_mae
                row = {
                    "symbol": symbol,
                    "horizon": horizon,
                    "lstm_mae": round(lstm_mae, 4),
                    "baseline_mae": round(baseline_mae, 4),
                    "delta_vs_baseline": round(delta, 4),
                    "winner": "LSTM" if lstm_mae < baseline_mae else "Baseline",
                }
                rows.append(row)
                print(
                    f"{symbol:6} horizon={horizon:2} | "
                    f"LSTM MAE={lstm_mae:.4f} | "
                    f"Baseline MAE={baseline_mae:.4f} | "
                    f"Δ={delta:+.4f} | Winner={row['winner']}"
                )
            except Exception as exc:  # pragma: no cover - diagnostic script
                print(f"{symbol:6} horizon={horizon:2} | ERROR: {type(exc).__name__}: {exc}")

    print("\nSUMMARY")
    print(json.dumps(rows, indent=2))
    return rows


if __name__ == "__main__":
    run_benchmark()
