"""
============================================================
StockPredictor AI
components/cards/metrics.py
============================================================

Dashboard Metric Cards

Displays key market statistics at the top of the dashboard.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_metrics(metrics: dict[str, Any]) -> None:
    """
    Render the dashboard metric cards.

    Parameters
    ----------
    metrics : dict
        Dictionary returned by
        StockDataLoader.dashboard_metrics()
    """

    col1, col2, col3, col4 = st.columns(4)

    # ======================================================
    # ROW 1
    # ======================================================

    with col1:
        st.metric(
            label="💲 Current Price",
            value=metrics.get("current_price", "--"),
            delta=metrics.get("day_change", "--"),
        )

    with col2:
        st.metric(
            label="🏢 Market Cap",
            value=metrics.get("market_cap", "--"),
        )

    with col3:
        st.metric(
            label="📊 P/E Ratio",
            value=str(metrics.get("pe_ratio", "--")),
        )

    with col4:
        st.metric(
            label="📈 Volume",
            value=metrics.get("volume", "--"),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ======================================================
    # ROW 2
    # ======================================================

    col5, col6 = st.columns(2)

    with col5:
        st.metric(
            label="📅 52 Week High",
            value=metrics.get(
                "fifty_two_week_high",
                "--",
            ),
        )

    with col6:
        st.metric(
            label="📉 52 Week Low",
            value=metrics.get(
                "fifty_two_week_low",
                "--",
            ),
        )