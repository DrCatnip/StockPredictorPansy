"""
============================================================
StockPredictor AI
components/charts/rsi.py
============================================================

Relative Strength Index (RSI) Chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import INDICATOR_CHART_HEIGHT
from utils.indicators import calculate_indicators


def render_rsi(df: pd.DataFrame) -> None:
    """
    Render Relative Strength Index (RSI).
    """

    if df.empty:
        st.warning("No RSI data available.")
        return

    df = calculate_indicators(df.copy())

    fig = go.Figure()

    # ======================================================
    # RSI LINE
    # ======================================================

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            mode="lines",
            name="RSI",
            line=dict(
                color="#8B5CF6",
                width=2.5,
            ),
        )
    )

    # ======================================================
    # OVERBOUGHT
    # ======================================================

    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="#EF4444",
        annotation_text="Overbought",
        annotation_position="top left",
    )

    # ======================================================
    # OVERSOLD
    # ======================================================

    fig.add_hline(
        y=30,
        line_dash="dash",
        line_color="#22C55E",
        annotation_text="Oversold",
        annotation_position="bottom left",
    )

    # ======================================================
    # NEUTRAL
    # ======================================================

    fig.add_hline(
        y=50,
        line_dash="dot",
        line_color="#6B7280",
    )

    apply_chart_theme(
        fig,
        "Relative Strength Index (RSI)",
        height=INDICATOR_CHART_HEIGHT,
    )

    fig.update_yaxes(
        range=[0, 100],
        title="RSI",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )