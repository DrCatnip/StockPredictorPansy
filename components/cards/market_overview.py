"""
============================================================
StockPredictor AI
components/cards/market_overview.py
============================================================

Global Market Overview
"""

from __future__ import annotations

import streamlit as st


def render_market_overview() -> None:
    """
    Render a global market overview section.

    NOTE:
    These values are placeholders for now.
    In Phase 3 they will come from Yahoo Finance.
    """

    st.markdown("## 🌍 Global Market Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "S&P 500",
            "6,225.52",
            "+1.21%",
            border=True,
        )

        st.metric(
            "NASDAQ",
            "20,601.10",
            "+0.87%",
            border=True,
        )

    with col2:

        st.metric(
            "DOW JONES",
            "44,828.53",
            "-0.18%",
            border=True,
        )

        st.metric(
            "NIFTY 50",
            "25,461.30",
            "+0.42%",
            border=True,
        )

    with col3:

        st.metric(
            "BTC",
            "$108,300",
            "-2.34%",
            border=True,
        )

        st.metric(
            "ETH",
            "$2,570",
            "+0.95%",
            border=True,
        )

    with col4:

        st.metric(
            "Gold",
            "$3,340",
            "+0.28%",
            border=True,
        )

        st.metric(
            "Crude Oil",
            "$67.90",
            "-0.61%",
            border=True,
        )