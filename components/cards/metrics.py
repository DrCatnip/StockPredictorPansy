"""
============================================================
StockPredictor AI
components/cards/metrics.py
============================================================

Professional Metric Cards
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_metrics(metrics: dict[str, Any]) -> None:
    """
    Render dashboard metric cards.
    """

    st.markdown("## 📊 Market Snapshot")

    row1 = st.columns(4)

    metric_data = [
        (
            "💲 Current Price",
            metrics.get("current_price", "--"),
            metrics.get("day_change", "--"),
        ),
        (
            "🏢 Market Cap",
            metrics.get("market_cap", "--"),
            None,
        ),
        (
            "📈 P/E Ratio",
            metrics.get("pe_ratio", "--"),
            None,
        ),
        (
            "📦 Volume",
            metrics.get("volume", "--"),
            None,
        ),
    ]

    for column, (title, value, delta) in zip(row1, metric_data):

        with column:

            st.metric(
                label=title,
                value=value,
                delta=delta,
                border=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    row2 = st.columns(2)

    with row2[0]:

        st.metric(
            label="📈 52 Week High",
            value=metrics.get(
                "fifty_two_week_high",
                "--",
            ),
            border=True,
        )

    with row2[1]:

        st.metric(
            label="📉 52 Week Low",
            value=metrics.get(
                "fifty_two_week_low",
                "--",
            ),
            border=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "📌 All market data is provided by Yahoo Finance and may be delayed depending on the exchange."
    )