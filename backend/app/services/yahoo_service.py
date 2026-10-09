from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging
import math
from typing import Any
from urllib.parse import quote

import pandas as pd
import requests

from backend.app.core.cache import history_cache, info_cache, market_cache
from backend.app.core.constants import (
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    DEFAULT_SYMBOL,
    HISTORY_CACHE_TTL,
    INFO_CACHE_TTL,
    MARKET_CACHE_TTL,
)
from backend.app.services.formatting import (
    format_currency,
    format_market_cap,
    format_price_change,
    format_volume,
)

MARKET_INSTRUMENTS = (
    ("S&P 500", "^GSPC", "USD"),
    ("NASDAQ", "^IXIC", "USD"),
    ("DOW JONES", "^DJI", "USD"),
    ("NIFTY 50", "^NSEI", "INR"),
    ("BTC", "BTC-USD", "USD"),
    ("ETH", "ETH-USD", "USD"),
    ("Gold", "GC=F", "USD"),
    ("Crude Oil", "CL=F", "USD"),
)
LOGGER = logging.getLogger(__name__)


def _download_chart(
    symbol: str,
    period: str,
    interval: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{quote(symbol, safe='')}"
    response = requests.get(
        url,
        params={"range": period, "interval": interval},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=20,
    )
    response.raise_for_status()
    chart = response.json().get("chart", {})
    if chart.get("error"):
        raise ValueError(chart["error"].get("description") or "Yahoo Finance chart request failed.")

    results = chart.get("result") or []
    if not results:
        return pd.DataFrame(), {}

    result = results[0]
    metadata = result.get("meta", {})
    timestamps = result.get("timestamp") or []
    if not timestamps:
        return pd.DataFrame(), metadata

    dates = pd.to_datetime(timestamps, unit="s", utc=True)
    timezone = metadata.get("exchangeTimezoneName")
    if timezone:
        dates = dates.tz_convert(timezone)
    dates = dates.tz_localize(None)

    quote_data = result.get("indicators", {}).get("quote", [{}])[0]
    frame = pd.DataFrame(
        {
            column: pd.to_numeric(pd.Series(quote_data.get(key, []), index=dates), errors="coerce")
            for column, key in (
                ("Open", "open"),
                ("High", "high"),
                ("Low", "low"),
                ("Close", "close"),
                ("Volume", "volume"),
            )
        },
        index=dates,
    )

    adjusted_data = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose")
    if adjusted_data and len(adjusted_data) == len(frame):
        adjusted_close = pd.Series(adjusted_data, index=dates, dtype="float64")
        adjustment = adjusted_close.div(frame["Close"])
        for column in ("Open", "High", "Low"):
            frame[column] = frame[column].mul(adjustment)
        frame["Close"] = adjusted_close

    frame.index.name = "Date"
    return frame.dropna(subset=["Open", "High", "Low", "Close"]), metadata


def fetch_market_quote(instrument: tuple[str, str, str]) -> dict[str, Any]:
    name, symbol, currency = instrument
    quote: dict[str, Any] = {
        "name": name,
        "symbol": symbol,
        "currency": currency,
        "price": None,
        "change_percent": None,
    }
    try:
        history, _ = _download_chart(symbol, period="5d", interval="1d")
        closes = history["Close"].dropna()
        if closes.empty:
            return quote

        current = float(closes.iloc[-1])
        if not math.isfinite(current):
            return quote
        quote["price"] = current

        if len(closes) > 1:
            previous = float(closes.iloc[-2])
            if math.isfinite(previous) and previous != 0:
                quote["change_percent"] = (current - previous) / previous * 100
    except Exception:
        LOGGER.exception("Yahoo market quote fetch failed for %s (%s)", name, symbol)
    return quote


def fetch_market_overview() -> list[dict[str, Any]]:
    def _fetch_all() -> list[dict[str, Any]]:
        with ThreadPoolExecutor(max_workers=len(MARKET_INSTRUMENTS)) as executor:
            return list(executor.map(fetch_market_quote, MARKET_INSTRUMENTS))

    return market_cache.get_or_set("market_overview", MARKET_CACHE_TTL, _fetch_all)


@dataclass
class StockDataLoader:
    symbol: str = DEFAULT_SYMBOL

    def __post_init__(self) -> None:
        self.symbol = (self.symbol or DEFAULT_SYMBOL).strip().upper()
        if not self.symbol:
            self.symbol = DEFAULT_SYMBOL

    def history(
        self,
        period: str = DEFAULT_PERIOD,
        interval: str = DEFAULT_INTERVAL,
    ) -> pd.DataFrame:
        key = ("history", self.symbol, period, interval)

        def _download() -> pd.DataFrame:
            try:
                frame, _ = _download_chart(self.symbol, period, interval)
                if frame.empty:
                    return pd.DataFrame()
                return frame
            except Exception:
                LOGGER.exception("Yahoo history fetch failed for %s (%s, %s)", self.symbol, period, interval)
                return pd.DataFrame()

        return history_cache.get_or_set(key, HISTORY_CACHE_TTL, _download)

    def company_info(self) -> dict[str, Any]:
        key = ("info", self.symbol)

        def _fetch() -> dict[str, Any]:
            try:
                _, metadata = _download_chart(self.symbol, period="5d", interval="1d")
                return {
                    "longName": metadata.get("longName") or metadata.get("shortName"),
                    "shortName": metadata.get("shortName"),
                    "currentPrice": metadata.get("regularMarketPrice"),
                    "previousClose": metadata.get("chartPreviousClose"),
                    "marketCap": None,
                    "trailingPE": None,
                    "volume": metadata.get("regularMarketVolume"),
                    "fiftyTwoWeekHigh": metadata.get("fiftyTwoWeekHigh"),
                    "fiftyTwoWeekLow": metadata.get("fiftyTwoWeekLow"),
                }
            except Exception:
                LOGGER.exception("Yahoo metadata fetch failed for %s", self.symbol)
                return {}

        return info_cache.get_or_set(key, INFO_CACHE_TTL, _fetch)

    def dashboard_metrics(self) -> dict[str, Any]:
        info = self.company_info()
        current = info.get("currentPrice")
        previous = info.get("previousClose")
        return {
            "company_name": info.get("longName") or info.get("shortName") or self.symbol,
            "current_price": current,
            "current_price_formatted": format_currency(current),
            "day_change": format_price_change(current, previous),
            "market_cap": info.get("marketCap"),
            "market_cap_formatted": format_market_cap(info.get("marketCap")),
            "pe_ratio": info.get("trailingPE"),
            "volume": info.get("volume"),
            "volume_formatted": format_volume(info.get("volume")),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_high_formatted": format_currency(info.get("fiftyTwoWeekHigh")),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "fifty_two_week_low_formatted": format_currency(info.get("fiftyTwoWeekLow")),
        }