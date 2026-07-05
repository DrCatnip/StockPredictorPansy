"""
============================================================
StockPredictor AI
app.py
============================================================

Main Streamlit Application
"""

from __future__ import annotations

import streamlit as st

from components.cards import render_metrics
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
from utils import initialize_page


# ==========================================================
# INITIALIZE APPLICATION
# ==========================================================

initialize_page()


# ==========================================================
# HEADER
# ==========================================================

render_header()

render_hero()

render_project_status()

st.markdown("<br>", unsafe_allow_html=True)


# ==========================================================
# SIDEBAR
# ==========================================================

settings = render_sidebar()

symbol = settings.get("symbol", "AAPL").strip().upper()

period = settings.get("period", "5y")

if not symbol:
    symbol = "AAPL"


# ==========================================================
# LOAD DATA
# ==========================================================

loader = StockDataLoader(symbol)

if not loader.is_valid():

    st.error(
        f"Unable to load market data for '{symbol}'."
    )

    st.stop()

with st.spinner("Loading market data..."):

    history = loader.history(period=period)

    metrics = loader.dashboard_metrics()

if history.empty:

    st.error("No historical data found.")

    st.stop()


# ==========================================================
# METRICS
# ==========================================================

render_metrics(metrics)

st.divider()


# ==========================================================
# PRICE ANALYSIS
# ==========================================================

st.subheader("📈 Price Analysis")

render_candlestick(
    history,
    symbol,
)

render_volume(
    history,
)

st.divider()


# ==========================================================
# TECHNICAL INDICATORS
# ==========================================================

st.subheader("📊 Technical Indicators")

render_moving_averages(
    history,
    symbol,
)

render_bollinger(
    history,
    symbol,
)

col1, col2 = st.columns(2)

with col1:

    render_rsi(
        history,
    )

with col2:

    render_macd(
        history,
    )

st.divider()


# ==========================================================
# FOOTER
# ==========================================================

st.caption(
    "📈 StockPredictor AI | Built with Streamlit, Plotly & Yahoo Finance"
)