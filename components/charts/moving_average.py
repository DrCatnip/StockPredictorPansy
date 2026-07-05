"""
============================================================
StockPredictor AI
components/charts/moving_average.py
============================================================

Moving Averages Chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import DEFAULT_CHART_HEIGHT
from utils.indicators import calculate_indicators


def render_moving_averages(
    df: pd.DataFrame,
    symbol: str,
) -> None:
    """
    Render moving averages chart.
    """

    if df.empty:
        st.warning("No market data available.")
        return

    df = calculate_indicators(df.copy())

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines",
            name="Close",
            line=dict(
                color="#FFFFFF",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA20"],
            mode="lines",
            name="SMA 20",
            line=dict(
                color="#3B82F6",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA50"],
            mode="lines",
            name="SMA 50",
            line=dict(
                color="#F59E0B",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["SMA200"],
            mode="lines",
            name="SMA 200",
            line=dict(
                color="#EF4444",
                width=2,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA20"],
            mode="lines",
            name="EMA 20",
            line=dict(
                color="#8B5CF6",
                width=2,
                dash="dot",
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["EMA50"],
            mode="lines",
            name="EMA 50",
            line=dict(
                color="#06B6D4",
                width=2,
                dash="dot",
            ),
        )
    )

    apply_chart_theme(
        fig,
        f"{symbol} Moving Averages",
        height=DEFAULT_CHART_HEIGHT,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )