"""
============================================================
StockPredictor AI
services/yahoo_service.py
============================================================

Yahoo Finance Service

Responsible for:
- Downloading historical stock data
- Fetching company information
- Dashboard metrics
- Financial statements
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import streamlit as st
import yfinance as yf

from utils.constants import (
    CACHE_TTL,
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    DEFAULT_SYMBOL,
)
from utils.formatting import (
    format_currency,
    format_market_cap,
    format_price_change,
    format_volume,
)


@dataclass
class StockDataLoader:
    """
    Yahoo Finance wrapper.
    """

    symbol: str = DEFAULT_SYMBOL

    def __post_init__(self) -> None:

        self.symbol = (self.symbol or DEFAULT_SYMBOL).strip().upper()

        if not self.symbol:
            self.symbol = DEFAULT_SYMBOL

        self.ticker = yf.Ticker(self.symbol)

    # ======================================================
    # HISTORY
    # ======================================================

    @st.cache_data(ttl=CACHE_TTL, show_spinner=False)
    def history(
        _self,
        period: str = DEFAULT_PERIOD,
        interval: str = DEFAULT_INTERVAL,
    ) -> pd.DataFrame:
        """
        Download historical stock data.
        """

        try:

            df = yf.download(
                _self.symbol,
                period=period,
                interval=interval,
                auto_adjust=True,
                progress=False,
                group_by="column",
            )

            if df.empty:
                return pd.DataFrame()

            # Handle MultiIndex if Yahoo returns one
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.dropna()

            return df

        except Exception:
            return pd.DataFrame()

    # ======================================================
    # COMPANY INFO
    # ======================================================

    @st.cache_data(ttl=CACHE_TTL, show_spinner=False)
    def company_info(_self) -> dict[str, Any]:
        """
        Fetch company metadata.
        """

        try:
            return _self.ticker.info
        except Exception:
            return {}

    # ======================================================
    # METRICS
    # ======================================================

    def dashboard_metrics(self) -> dict[str, Any]:
        """
        Build dashboard metrics.
        """

        info = self.company_info()

        current = info.get("currentPrice")

        previous = info.get("previousClose")

        return {

            "current_price":
                format_currency(current),

            "day_change":
                format_price_change(current, previous),

            "market_cap":
                format_market_cap(
                    info.get("marketCap")
                ),

            "pe_ratio":
                info.get("trailingPE", "--"),

            "volume":
                format_volume(
                    info.get("volume")
                ),

            "fifty_two_week_high":
                format_currency(
                    info.get("fiftyTwoWeekHigh")
                ),

            "fifty_two_week_low":
                format_currency(
                    info.get("fiftyTwoWeekLow")
                ),

        }

    # ======================================================
    # FINANCIALS
    # ======================================================

    @st.cache_data(ttl=CACHE_TTL)
    def financials(_self) -> pd.DataFrame:

        try:
            return _self.ticker.financials
        except Exception:
            return pd.DataFrame()

    @st.cache_data(ttl=CACHE_TTL)
    def balance_sheet(_self) -> pd.DataFrame:

        try:
            return _self.ticker.balance_sheet
        except Exception:
            return pd.DataFrame()

    @st.cache_data(ttl=CACHE_TTL)
    def cashflow(_self) -> pd.DataFrame:

        try:
            return _self.ticker.cashflow
        except Exception:
            return pd.DataFrame()

    # ======================================================
    # VALIDATION
    # ======================================================

    def is_valid(self) -> bool:
        """
        Check whether the ticker is valid.
        """

        history = self.history(period="5d")

        return not history.empty