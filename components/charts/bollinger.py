"""
============================================================
StockPredictor AI
components/charts/bollinger.py
============================================================

Bollinger Bands Chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import DEFAULT_CHART_HEIGHT
from utils.indicators import calculate_indicators


def render_bollinger(
    df: pd.DataFrame,
    symbol: str,
) -> None:
    """
    Render Bollinger Bands chart.
    """

    if df.empty:
        st.warning("No market data available.")
        return

    df = calculate_indicators(df.copy())

    fig = go.Figure()

    # ======================================================
    # CLOSE PRICE
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name="Close",
            line=dict(
                color="white",
                width=2,
            ),
        )
    )

    # ======================================================
    # UPPER BAND
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Upper"],
            mode="lines",
            name="Upper Band",
            line=dict(
                color="#EF4444",
                width=1.5,
            ),
        )
    )

    # ======================================================
    # LOWER BAND
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Lower"],
            mode="lines",
            name="Lower Band",
            fill="tonexty",
            fillcolor="rgba(59,130,246,0.15)",
            line=dict(
                color="#22C55E",
                width=1.5,
            ),
        )
    )

    # ======================================================
    # MIDDLE BAND
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_Middle"],
            mode="lines",
            name="Middle Band",
            line=dict(
                color="#F59E0B",
                width=2,
                dash="dash",
            ),
        )
    )

    apply_chart_theme(
        fig,
        f"{symbol} Bollinger Bands",
        height=DEFAULT_CHART_HEIGHT,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )