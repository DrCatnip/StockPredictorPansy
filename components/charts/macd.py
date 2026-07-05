"""
============================================================
StockPredictor AI
components/charts/macd.py
============================================================

MACD Chart

Displays:
- MACD Line
- Signal Line
- Histogram
============================================================
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import INDICATOR_CHART_HEIGHT
from utils.indicators import calculate_indicators


def render_macd(df: pd.DataFrame) -> None:
    """
    Render MACD chart.
    """

    if df.empty:
        st.warning("No MACD data available.")
        return

    df = calculate_indicators(df.copy())

    histogram_colors = [
        "#22C55E" if value >= 0 else "#EF4444"
        for value in df["Histogram"]
    ]

    fig = go.Figure()

    # ======================================================
    # HISTOGRAM
    # ======================================================

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Histogram"],
            name="Histogram",
            marker_color=histogram_colors,
            opacity=0.7,
        )
    )

    # ======================================================
    # MACD LINE
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["MACD"],
            mode="lines",
            name="MACD",
            line=dict(
                color="#3B82F6",
                width=2.5,
            ),
        )
    )

    # ======================================================
    # SIGNAL LINE
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Signal"],
            mode="lines",
            name="Signal",
            line=dict(
                color="#F59E0B",
                width=2,
            ),
        )
    )

    # ======================================================
    # ZERO LINE
    # ======================================================

    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="#6B7280",
    )

    apply_chart_theme(
        fig,
        "Moving Average Convergence Divergence (MACD)",
        height=INDICATOR_CHART_HEIGHT,
    )

    fig.update_yaxes(
        title="MACD",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )