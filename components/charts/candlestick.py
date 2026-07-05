"""
============================================================
StockPredictor AI
components/charts/candlestick.py
============================================================

Interactive Candlestick Chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import DEFAULT_CHART_HEIGHT
from utils.indicators import calculate_indicators


def render_candlestick(
    df: pd.DataFrame,
    symbol: str,
) -> None:
    """
    Render the main candlestick chart.
    """

    if df.empty:
        st.warning("No market data available.")
        return

    df = calculate_indicators(df.copy())

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="#22C55E",
            decreasing_line_color="#EF4444",
            name="Price",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA20"],
            name="SMA 20",
            line=dict(color="#3B82F6", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA50"],
            name="SMA 50",
            line=dict(color="#F59E0B", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA20"],
            name="EMA 20",
            line=dict(color="#A855F7", width=2),
        )
    )

    apply_chart_theme(
        fig,
        f"{symbol} Price Chart",
        height=DEFAULT_CHART_HEIGHT,
    )

    fig.update_layout(
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )