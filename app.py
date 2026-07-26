"""
============================================================
StockPredictor AI
app.py
============================================================

Main Streamlit Application
"""

from __future__ import annotations

import streamlit as st

from components.cards import (
    render_market_overview,
    render_metrics,
)
from components.charts import (
    render_bollinger,
    render_candlestick,
    render_macd,
    render_moving_averages,
    render_rsi,
    render_volume,
)
from components.header import (
    render_header,
    render_hero,
    render_project_status,
)
from components.sidebar import render_sidebar
from services import StockDataLoader
from utils import (
    calculate_indicators,
    initialize_page,
)

# ==========================================================
# INITIALIZE APPLICATION
# ==========================================================

initialize_page()

# ==========================================================
# SIDEBAR
# ==========================================================

settings = render_sidebar()

symbol = settings.get("symbol", "AAPL").strip().upper()

period = settings.get("period", "5y")

if not symbol:
    symbol = "AAPL"

# ==========================================================
# HEADER
# ==========================================================

render_header()

render_hero()

render_project_status()

# ==========================================================
# LOAD DATA
# ==========================================================

loader = StockDataLoader(symbol)

with st.spinner("Loading market data..."):

    history = loader.history(period=period)

if history.empty:

    st.error(f"No data found for '{symbol}'.")

    st.stop()

history = calculate_indicators(history)

metrics = loader.dashboard_metrics()

# ==========================================================
# DASHBOARD
# ==========================================================

render_metrics(metrics)

st.markdown("")

render_market_overview()

st.divider()

# ==========================================================
# PRICE ANALYSIS
# ==========================================================

st.header("📈 Price Analysis")

render_candlestick(
    history,
    symbol,
)

render_volume(
    history,
)

st.divider()

# ==========================================================
# TECHNICAL ANALYSIS
# ==========================================================

st.header("📊 Technical Indicators")

render_moving_averages(
    history,
    symbol,
)

render_bollinger(
    history,
    symbol,
)

left, right = st.columns(2)

with left:

    render_rsi(
        history,
    )

with right:

    render_macd(
        history,
    )

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """
---
<center>

**StockPredictor AI**

Built with ❤️ using

Streamlit • Plotly • Yahoo Finance

Version 2.0

</center>
""",
    unsafe_allow_html=True,
)