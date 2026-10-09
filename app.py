"""
============================================================
StockPredictor AI
app.py
============================================================

Main Streamlit Application
"""

from __future__ import annotations

import streamlit as st
import numpy as np

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
from components.prediction import render_backtest, render_prediction
from components.sidebar import render_sidebar
from services import StockDataLoader, fetch_market_overview
from services.lstm_predictor import backtest_walk_forward, predict_stock
from utils import (
    calculate_indicators,
    initialize_page,
)


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_prediction(
    symbol: str,
    period: str,
    interval: str,
    prediction_days: int,
    close_prices: tuple[float, ...],
) -> np.ndarray:
    prices = np.asarray(close_prices, dtype=float).reshape(-1, 1)
    return predict_stock(prices, future_days=prediction_days)


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_backtest(
    symbol: str,
    period: str,
    interval: str,
    horizon: int,
    close_prices: tuple[float, ...],
) -> dict:
    prices = np.asarray(close_prices, dtype=float).reshape(-1, 1)
    return backtest_walk_forward(prices, horizon=horizon)


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
interval = settings.get("interval", "1d")
prediction_days = settings.get("prediction_days", 30)

if not symbol:
    symbol = "AAPL"

prediction_signature = (symbol, period, interval, prediction_days)
if st.session_state.get("prediction_signature") != prediction_signature:
    st.session_state["prediction_signature"] = prediction_signature
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("prediction_error", None)
    st.session_state.pop("backtest_result", None)
    st.session_state.pop("backtest_error", None)

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

    history = loader.history(period=period, interval=interval)

if history.empty:

    st.error(f"No data found for '{symbol}'.")

    st.stop()

history = calculate_indicators(history)

metrics = loader.dashboard_metrics()

if settings.get("train"):
    st.session_state.pop("prediction_result", None)
    st.session_state.pop("prediction_error", None)

    try:
        with st.spinner("Training LSTM model and generating forecast..."):
            close_prices = tuple(
                float(price) for price in history["Close"].to_numpy()
            )
            predictions = _cached_prediction(
                symbol,
                period,
                interval,
                prediction_days=prediction_days,
                close_prices=close_prices,
            )
        st.session_state["prediction_result"] = predictions.reshape(-1).tolist()
    except ValueError as exc:
        st.session_state["prediction_error"] = str(exc)
    except Exception as exc:
        st.session_state["prediction_error"] = (
            f"Could not generate a forecast: {exc}"
        )

if settings.get("evaluate"):
    st.session_state.pop("backtest_result", None)
    st.session_state.pop("backtest_error", None)

    try:
        with st.spinner("Training walk-forward models and scoring the baseline..."):
            close_prices = tuple(
                float(price) for price in history["Close"].to_numpy()
            )
            st.session_state["backtest_result"] = _cached_backtest(
                symbol,
                period,
                interval,
                horizon=prediction_days,
                close_prices=close_prices,
            )
    except ValueError as exc:
        st.session_state["backtest_error"] = str(exc)
    except Exception as exc:
        st.session_state["backtest_error"] = f"Could not evaluate the forecast: {exc}"

# ==========================================================
# DASHBOARD
# ==========================================================

render_metrics(metrics)

st.markdown("")

with st.spinner("Loading global market snapshot..."):
    market_quotes = fetch_market_overview()

render_market_overview(market_quotes)

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

render_prediction(
    history,
    symbol,
    interval,
    prediction_days,
    st.session_state.get("prediction_result"),
    st.session_state.get("prediction_error"),
)

render_backtest(
    st.session_state.get("backtest_result"),
    st.session_state.get("backtest_error"),
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