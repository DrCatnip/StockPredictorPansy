from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.chart_theme import apply_chart_theme
from utils.constants import DEFAULT_CHART_HEIGHT


def render_prediction_chart(
	history: pd.DataFrame,
	predictions: list[float],
	symbol: str,
	interval: str,
) -> None:
	historical_close = history["Close"].dropna()
	forecast = np.asarray(predictions, dtype=float).reshape(-1)

	if historical_close.empty or forecast.size == 0:
		st.warning("Not enough data to display a forecast.")
		return

	last_date = pd.Timestamp(historical_close.index[-1])
	if interval == "1wk":
		forecast_dates = [
			last_date + pd.Timedelta(weeks=step)
			for step in range(1, forecast.size + 1)
		]
	elif interval == "1mo":
		forecast_dates = [
			last_date + pd.DateOffset(months=step)
			for step in range(1, forecast.size + 1)
		]
	else:
		forecast_dates = [
			last_date + pd.offsets.BDay(step)
			for step in range(1, forecast.size + 1)
		]

	fig = go.Figure()
	fig.add_trace(
		go.Scatter(
			x=historical_close.index,
			y=historical_close,
			mode="lines",
			name="Historical close",
			line=dict(color="#3B82F6", width=2),
		)
	)
	fig.add_trace(
		go.Scatter(
			x=[last_date, *forecast_dates],
			y=[float(historical_close.iloc[-1]), *forecast.tolist()],
			mode="lines+markers",
			name="LSTM forecast",
			line=dict(color="#F59E0B", width=2, dash="dash"),
			marker=dict(size=6),
		)
	)

	apply_chart_theme(
		fig,
		f"{symbol} Price Forecast",
		height=DEFAULT_CHART_HEIGHT,
	)
	fig.update_layout(
		hovermode="x unified",
		xaxis_title="Date",
		yaxis_title="Price",
	)
	fig.add_vline(x=last_date, line_dash="dot", line_color="#94A3B8")

	st.plotly_chart(fig, width="stretch")
