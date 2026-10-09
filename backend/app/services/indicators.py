from __future__ import annotations

import pandas as pd


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()
    required = {"Open", "High", "Low", "Close", "Volume"}
    if not required.issubset(df.columns):
        raise ValueError("DataFrame is missing one or more required OHLCV columns.")

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    df["SMA20"] = close.rolling(20).mean()
    df["SMA50"] = close.rolling(50).mean()
    df["SMA200"] = close.rolling(200).mean()
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()
    df["EMA50"] = close.ewm(span=50, adjust=False).mean()

    delta = close.diff()
    average_gain = delta.clip(lower=0).rolling(14).mean()
    average_loss = -delta.clip(upper=0).rolling(14).mean()
    relative_strength = average_gain / average_loss
    df["RSI"] = 100 - (100 / (1 + relative_strength))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Histogram"] = df["MACD"] - df["Signal"]

    middle = close.rolling(20).mean()
    standard_deviation = close.rolling(20).std()
    df["BB_Middle"] = middle
    df["BB_Upper"] = middle + 2 * standard_deviation
    df["BB_Lower"] = middle - 2 * standard_deviation

    true_range = pd.concat(
        [
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)
    df["ATR"] = true_range.rolling(14).mean()

    typical_price = (high + low + close) / 3
    cumulative_volume = volume.cumsum()
    df["VWAP"] = (typical_price * volume).cumsum() / cumulative_volume
    df["Daily_Return"] = close.pct_change()
    df["Volatility"] = df["Daily_Return"].rolling(20).std() * (252 ** 0.5)
    return df