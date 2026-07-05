"""
============================================================
StockPredictor AI
utils/indicators.py
============================================================

Technical Indicator Calculations

This module calculates all technical indicators used
throughout the application.
"""

from __future__ import annotations

import pandas as pd


# ==========================================================
# MAIN FUNCTION
# ==========================================================

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all supported technical indicators.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    if df.empty:
        return df

    required_columns = {
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    }

    if not required_columns.issubset(df.columns):
        raise ValueError(
            "DataFrame is missing one or more required OHLCV columns."
        )

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # ======================================================
    # SIMPLE MOVING AVERAGES
    # ======================================================

    df["SMA20"] = close.rolling(window=20).mean()
    df["SMA50"] = close.rolling(window=50).mean()
    df["SMA200"] = close.rolling(window=200).mean()

    # ======================================================
    # EXPONENTIAL MOVING AVERAGES
    # ======================================================

    df["EMA20"] = close.ewm(
        span=20,
        adjust=False,
    ).mean()

    df["EMA50"] = close.ewm(
        span=50,
        adjust=False,
    ).mean()

    # ======================================================
    # RSI
    # ======================================================

    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    average_gain = gain.rolling(14).mean()

    average_loss = loss.rolling(14).mean()

    rs = average_gain / average_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    # ======================================================
    # MACD
    # ======================================================

    ema12 = close.ewm(
        span=12,
        adjust=False,
    ).mean()

    ema26 = close.ewm(
        span=26,
        adjust=False,
    ).mean()

    df["MACD"] = ema12 - ema26

    df["Signal"] = df["MACD"].ewm(
        span=9,
        adjust=False,
    ).mean()

    df["Histogram"] = (
        df["MACD"] - df["Signal"]
    )

    # ======================================================
    # BOLLINGER BANDS
    # ======================================================

    middle = close.rolling(20).mean()

    std = close.rolling(20).std()

    df["BB_Middle"] = middle

    df["BB_Upper"] = middle + (2 * std)

    df["BB_Lower"] = middle - (2 * std)

    # ======================================================
    # ATR
    # ======================================================

    tr1 = high - low

    tr2 = (high - close.shift()).abs()

    tr3 = (low - close.shift()).abs()

    true_range = pd.concat(
        [tr1, tr2, tr3],
        axis=1,
    ).max(axis=1)

    df["ATR"] = true_range.rolling(14).mean()

    # ======================================================
    # VWAP
    # ======================================================

    typical_price = (
        high + low + close
    ) / 3

    cumulative_price_volume = (
        typical_price * volume
    ).cumsum()

    cumulative_volume = volume.cumsum()

    df["VWAP"] = (
        cumulative_price_volume /
        cumulative_volume
    )

    # ======================================================
    # DAILY RETURNS
    # ======================================================

    df["Daily_Return"] = close.pct_change()

    # ======================================================
    # VOLATILITY
    # ======================================================

    df["Volatility"] = (
        df["Daily_Return"]
        .rolling(20)
        .std()
        * (252 ** 0.5)
    )

    return df