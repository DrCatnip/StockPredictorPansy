"""
============================================================
StockPredictor AI
components/charts/volume.py
============================================================

Volume Chart
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import VOLUME_CHART_HEIGHT


def render_volume(df: pd.DataFrame) -> None:
    """
    Render trading volume chart.
    """

    if df.empty:
        st.warning("No volume data available.")
        return

    colors = [
        "#22C55E" if close >= open_ else "#EF4444"
        for open_, close in zip(df["Open"], df["Close"])
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            marker_color=colors,
            name="Volume",
        )
    )

    apply_chart_theme(
        fig,
        "Trading Volume",
        height=VOLUME_CHART_HEIGHT,
        show_legend=False,
    )

    fig.update_yaxes(title="Shares")

    st.plotly_chart(
        fig,
        use_container_width=True,
    )