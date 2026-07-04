"""
============================================================
StockPredictor AI
services/data_loader.py
============================================================

Responsible for:
- Downloading stock history
- Company information
- Latest price
- Financial data
- Validation

Author : Panshul Agarwal
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import streamlit as st
import yfinance as yf


@dataclass
class StockDataLoader:
    """
    Handles all Yahoo Finance communication.

    Example
    -------
    >>> loader = StockDataLoader("AAPL")
    >>> history = loader.history()
    >>> info = loader.company_info()
    """

    symbol: str

    def __post_init__(self):

        self.symbol = self.symbol.upper().strip()

        self.ticker = yf.Ticker(self.symbol)

    # =====================================================
    # HISTORICAL DATA
    # =====================================================

    @st.cache_data(show_spinner=False)
    def history(
        _self,
        period: str = "5y",
        interval: str = "1d"
    ) -> pd.DataFrame:

        try:

            df = yf.download(

                tickers=_self.symbol,

                period=period,

                interval=interval,

                auto_adjust=True,

                progress=False

            )

            if df.empty:

                return pd.DataFrame()

            df.dropna(inplace=True)

            df.index = pd.to_datetime(df.index)

            return df

        except Exception:

            return pd.DataFrame()

    # =====================================================
    # COMPANY INFORMATION
    # =====================================================

    @st.cache_data(show_spinner=False)
    def company_info(_self) -> dict:

        try:

            return _self.ticker.info

        except Exception:

            return {}

    # =====================================================
    # CURRENT PRICE
    # =====================================================

    @st.cache_data(show_spinner=False)
    def current_price(_self) -> Optional[float]:

        try:

            history = _self.ticker.history(period="2d")

            if history.empty:

                return None

            return float(history["Close"].iloc[-1])

        except Exception:

            return None

    # =====================================================
    # DIVIDENDS
    # =====================================================

    @st.cache_data(show_spinner=False)
    def dividends(_self) -> pd.Series:

        try:

            return _self.ticker.dividends

        except Exception:

            return pd.Series(dtype=float)

    # =====================================================
    # SPLITS
    # =====================================================

    @st.cache_data(show_spinner=False)
    def splits(_self) -> pd.Series:

        try:

            return _self.ticker.splits

        except Exception:

            return pd.Series(dtype=float)

    # =====================================================
    # FINANCIALS
    # =====================================================

    @st.cache_data(show_spinner=False)
    def financials(_self):

        try:

            return _self.ticker.financials

        except Exception:

            return pd.DataFrame()

    # =====================================================
    # BALANCE SHEET
    # =====================================================

    @st.cache_data(show_spinner=False)
    def balance_sheet(_self):

        try:

            return _self.ticker.balance_sheet

        except Exception:

            return pd.DataFrame()

    # =====================================================
    # CASH FLOW
    # =====================================================

    @st.cache_data(show_spinner=False)
    def cashflow(_self):

        try:

            return _self.ticker.cashflow

        except Exception:

            return pd.DataFrame()

    # =====================================================
    # VALID SYMBOL
    # =====================================================

    def is_valid(self) -> bool:

        df = self.history(period="5d")

        return not df.empty