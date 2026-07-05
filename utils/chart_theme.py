"""
============================================================
StockPredictor AI
utils/chart_theme.py
============================================================

Common Plotly theme utilities.

Every chart in the application should use this module
to maintain a consistent appearance.
"""

from __future__ import annotations

import plotly.graph_objects as go

from utils.constants import (
    BACKGROUND_COLOR,
    GRID_COLOR,
    TEXT_COLOR,
)


# ==========================================================
# APPLY THEME
# ==========================================================

def apply_chart_theme(
    fig: go.Figure,
    title: str,
    *,
    height: int = 650,
    show_legend: bool = True,
) -> go.Figure:
    """
    Apply the standard StockPredictor AI chart theme.

    Parameters
    ----------
    fig : go.Figure
        Plotly figure.

    title : str
        Chart title.

    height : int
        Chart height.

    show_legend : bool
        Show or hide legend.

    Returns
    -------
    go.Figure
    """

    fig.update_layout(

        title=dict(
            text=title,
            x=0.01,
            xanchor="left",
        ),

        template="plotly_dark",

        paper_bgcolor=BACKGROUND_COLOR,

        plot_bgcolor=BACKGROUND_COLOR,

        font=dict(
            family="Inter, Arial, sans-serif",
            size=13,
            color=TEXT_COLOR,
        ),

        hovermode="x unified",

        hoverlabel=dict(
            bgcolor="#111827",
            font_size=13,
        ),

        legend=dict(
            orientation="h",
            y=1.02,
            x=0,
        ),

        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
        ),

        height=height,

        showlegend=show_legend,
    )

    fig.update_xaxes(

        showgrid=True,

        gridcolor=GRID_COLOR,

        zeroline=False,

        showspikes=True,

        spikecolor="#2563EB",

        spikethickness=1,

        spikemode="across",

        spikesnap="cursor",
    )

    fig.update_yaxes(

        showgrid=True,

        gridcolor=GRID_COLOR,

        zeroline=False,

        side="right",

        showspikes=True,

        spikecolor="#2563EB",

        spikethickness=1,

        spikemode="across",

        spikesnap="cursor",
    )

    return fig


# ==========================================================
# WATERMARK
# ==========================================================

def add_watermark(
    fig: go.Figure,
    text: str = "StockPredictor AI",
) -> go.Figure:
    """
    Add a subtle watermark to a chart.
    """

    fig.add_annotation(

        text=text,

        xref="paper",

        yref="paper",

        x=0.5,

        y=0.5,

        showarrow=False,

        opacity=0.05,

        font=dict(
            size=40,
            color="white",
        ),
    )

    return fig