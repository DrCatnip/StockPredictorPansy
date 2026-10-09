from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import math
from typing import Any

import pandas as pd
import yfinance as yf

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
        history = yf.Ticker(symbol).history(
            period="5d",
            interval="1d",
            auto_adjust=True,
        )
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
        pass
    return quote


def fetch_market_overview() -> list[dict[str, Any]]:
    def _fetch_all() -> list[dict[str, Any]]:
        with ThreadPoolExecutor(max_workers=len(MARKET_INSTRUMENTS)) as executor:
            return list(executor.map(fetch_market_quote, MARKET_INSTRUMENTS))

    return market_cache.get_or_set("market_overview", MARKET_CACHE_TTL, _fetch_all)


@dataclass
class StockDataLoader:
    symbol: str = DEFAULT_SYMBOL
    ticker: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.symbol = (self.symbol or DEFAULT_SYMBOL).strip().upper()
        if not self.symbol:
            self.symbol = DEFAULT_SYMBOL
        self.ticker = yf.Ticker(self.symbol)

    def history(
        self,
        period: str = DEFAULT_PERIOD,
        interval: str = DEFAULT_INTERVAL,
    ) -> pd.DataFrame:
        key = ("history", self.symbol, period, interval)

        def _download() -> pd.DataFrame:
            try:
                frame = yf.download(
                    self.symbol,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    progress=False,
                    group_by="column",
                )
                if frame.empty:
                    return pd.DataFrame()
                if isinstance(frame.columns, pd.MultiIndex):
                    frame.columns = frame.columns.get_level_values(0)
                return frame.dropna()
            except Exception:
                return pd.DataFrame()

        return history_cache.get_or_set(key, HISTORY_CACHE_TTL, _download)

    def company_info(self) -> dict[str, Any]:
        key = ("info", self.symbol)

        def _fetch() -> dict[str, Any]:
            try:
                return self.ticker.info
            except Exception:
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