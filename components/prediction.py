from __future__ import annotations

import pandas as pd
import streamlit as st

from components.charts.prediction_chart import render_prediction_chart


def render_prediction(
	history: pd.DataFrame,
	symbol: str,
	interval: str,
	prediction_days: int,
	predictions: list[float] | None,
	error: str | None = None,
) -> None:
	st.header("Price Forecast")

	if error:
		st.error(error)
		return

	if predictions is None:
		st.info(
			"Choose a prediction horizon and select Generate Prediction "
			"in the sidebar."
		)
		return

	interval_labels = {
		"1d": "daily bars",
		"1wk": "weekly bars",
		"1mo": "monthly bars",
	}
	period_label = interval_labels.get(interval, "data bars")
	st.caption(
		f"Experimental forecast for the next {prediction_days} {period_label}. "
		"Dates are approximate; this is not investment advice."
	)
	render_prediction_chart(history, predictions, symbol, interval)


def render_backtest(results: dict | None, error: str | None = None) -> None:
	if error:
		st.error(error)
		return

	if results is None:
		return

	st.subheader("Walk-Forward Backtest")
	st.caption(
		f"Expanding training across {results['windows']} chronological windows; "
		f"each window tests {results['horizon']} bars. The first window starts "
		f"with {results['starting_training_bars']} training bars. Lower errors "
		"are better. This historical evaluation does not guarantee future accuracy."
	)

	metric_columns = st.columns(3)
	for column, metric, label in zip(
		metric_columns,
		("mae", "rmse", "mape"),
		("MAE", "RMSE", "MAPE"),
	):
		lstm_value = results["lstm"][metric]
		baseline_value = results["baseline"][metric]
		if lstm_value is None or baseline_value is None:
			column.metric(label, "N/A", help="MAPE is undefined when actual prices contain zero.")
		else:
			column.metric(
				label,
				f"LSTM {lstm_value:.2f}",
				delta=f"{baseline_value - lstm_value:+.2f} vs baseline",
				help="A positive delta means the LSTM error is lower than the baseline.",
			)

	window_rows = [
		{
			"Window": result["window"],
			"Training bars": result["training_bars"],
			"LSTM MAE": result["lstm"]["mae"],
			"Baseline MAE": result["baseline"]["mae"],
		}
		for result in results["window_results"]
	]
	st.dataframe(pd.DataFrame(window_rows), hide_index=True, width="stretch")

	winner = (
		"LSTM"
		if results["lstm"]["mae"] < results["baseline"]["mae"]
		else "last-close baseline"
	)
	st.info(f"Lower aggregate MAE across these windows: {winner}.")
