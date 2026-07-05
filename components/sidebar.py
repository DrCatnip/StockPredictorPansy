"""
============================================================
StockPredictor AI
components/sidebar.py
============================================================

Application Sidebar

Responsible for:
- Stock search
- Historical data settings
- Prediction settings
- Future application modules
============================================================
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
    Render the application sidebar.

    Returns
    -------
    dict
        User selected application settings.
    """

    with st.sidebar:

        st.markdown(
            """
            # 📈 StockPredictor AI
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "AI Powered Stock Market Analysis"
        )

        st.divider()

        # ==================================================
        # STOCK SETTINGS
        # ==================================================

        st.subheader("📊 Stock")

        symbol = st.text_input(
            "Ticker Symbol",
            value=DEFAULT_SYMBOL,
            placeholder="AAPL",
            help="Example: AAPL, MSFT, TSLA, NVDA",
        )

        symbol = symbol.strip().upper()

        if not symbol:
            symbol = DEFAULT_SYMBOL

        period = st.selectbox(
            "Historical Period",
            options=AVAILABLE_PERIODS,
            index=AVAILABLE_PERIODS.index(DEFAULT_PERIOD),
        )

        st.divider()

        # ==================================================
        # PREDICTION
        # ==================================================

        st.subheader("🤖 Prediction")

        prediction_days = st.selectbox(
            "Prediction Horizon",
            options=PREDICTION_DAYS,
            index=1,
        )

        generate_prediction = st.button(
            "🚀 Generate Prediction",
            use_container_width=True,
        )

        st.divider()

        # ==================================================
        # UPCOMING FEATURES
        # ==================================================

        with st.expander(
            "🚧 Upcoming Features",
            expanded=False,
        ):

            st.checkbox(
                "AI Stock Analyst",
                value=False,
                disabled=True,
            )

            st.checkbox(
                "Latest News",
                value=False,
                disabled=True,
            )

            st.checkbox(
                "Portfolio Tracker",
                value=False,
                disabled=True,
            )

            st.checkbox(
                "Watchlist",
                value=False,
                disabled=True,
            )

            st.checkbox(
                "Market Heatmap",
                value=False,
                disabled=True,
            )

            st.checkbox(
                "AI Chat",
                value=False,
                disabled=True,
            )

        st.divider()

        st.caption(
            f"Version {APP_VERSION}"
        )

    return {
        "symbol": symbol,
        "period": period,
        "prediction_days": prediction_days,
        "train": generate_prediction,
    }