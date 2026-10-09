"""
============================================================
StockPredictor AI
components/sidebar.py
============================================================

Professional Dashboard Sidebar
"""

from __future__ import annotations

import streamlit as st

from utils.constants import (
    APP_VERSION,
    AVAILABLE_PERIODS,
    DEFAULT_PERIOD,
    DEFAULT_SYMBOL,
    PREDICTION_DAYS,
)


def render_sidebar() -> dict:
    """
    Render application sidebar.

    Returns
    -------
    dict
        Dashboard settings.
    """

    with st.sidebar:

        # =====================================================
        # BRAND
        # =====================================================

        st.markdown(
            """
# 📈 StockPredictor AI

Professional AI Stock Analytics
"""
        )

        st.caption(
            "Real-time market intelligence powered by Yahoo Finance"
        )

        st.divider()

        # =====================================================
        # SEARCH
        # =====================================================

        st.subheader("🔍 Search")

        symbol = st.text_input(
            "Ticker",
            value=DEFAULT_SYMBOL,
            placeholder="AAPL",
            help="Example: AAPL, NVDA, TSLA, MSFT, RELIANCE.NS",
        )

        symbol = symbol.strip().upper()

        if not symbol:
            symbol = DEFAULT_SYMBOL

        st.markdown("### ⭐ Quick Picks")

        quick_pick = st.radio(
            "Quick stock selection",
            [
                "Custom",
                "🍎 AAPL",
                "🟩 NVDA",
                "⚡ TSLA",
                "🪟 MSFT",
                "📦 AMZN",
                "🌐 GOOGL",
                "🎬 NFLX",
            ],
            label_visibility="collapsed",
        )

        quick_map = {
            "🍎 AAPL": "AAPL",
            "🟩 NVDA": "NVDA",
            "⚡ TSLA": "TSLA",
            "🪟 MSFT": "MSFT",
            "📦 AMZN": "AMZN",
            "🌐 GOOGL": "GOOGL",
            "🎬 NFLX": "NFLX",
        }

        if quick_pick in quick_map:
            symbol = quick_map[quick_pick]

        st.divider()

        # =====================================================
        # MARKET DATA
        # =====================================================

        st.subheader("📅 Market Data")

        period = st.selectbox(
            "Historical Period",
            AVAILABLE_PERIODS,
            index=AVAILABLE_PERIODS.index(DEFAULT_PERIOD),
        )

        interval = st.selectbox(
            "Interval",
            [
                "1d",
                "1wk",
                "1mo",
            ],
            index=0,
        )

        st.divider()

        # =====================================================
        # AI PREDICTION
        # =====================================================

        st.subheader("🤖 Prediction")

        prediction_days = st.slider(
            "Prediction Horizon",
            min_value=5,
            max_value=60,
            step=5,
            value=30,
        )

        train = st.button(
            "🚀 Generate Prediction",
            width="stretch",
        )

        evaluate = st.button(
            "Evaluate Forecast",
            width="stretch",
            help="Compare a chronological holdout forecast with a last-close baseline.",
        )

        st.divider()

        # =====================================================
        # MARKET SNAPSHOT
        # =====================================================

        st.subheader("🌍 Markets")
        st.caption("Current quotes are shown in the Global Market Overview.")

        st.divider()

        # =====================================================
        # UPCOMING FEATURES
        # =====================================================

        with st.expander(
            "🚧 Upcoming Features",
            expanded=False,
        ):

            st.checkbox(
                "AI Stock Analyst",
                disabled=True,
            )

            st.checkbox(
                "Latest Financial News",
                disabled=True,
            )

            st.checkbox(
                "Portfolio Tracker",
                disabled=True,
            )

            st.checkbox(
                "Watchlist",
                disabled=True,
            )

            st.checkbox(
                "Price Alerts",
                disabled=True,
            )

            st.checkbox(
                "PDF Reports",
                disabled=True,
            )

        st.divider()

        st.caption(f"Version {APP_VERSION}")

    return {
        "symbol": symbol,
        "period": period,
        "interval": interval,
        "prediction_days": prediction_days,
        "train": train,
        "evaluate": evaluate,
    }