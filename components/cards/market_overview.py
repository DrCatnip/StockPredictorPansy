"""
============================================================
StockPredictor AI
components/cards/market_overview.py
============================================================

Global Market Overview
"""

from __future__ import annotations

import streamlit as st

from utils.formatting import format_percentage


def render_market_overview(quotes: list[dict]) -> None:
    """
    Render the latest available Yahoo Finance market snapshot.
    """

    st.markdown("## 🌍 Global Market Overview")
    st.caption("Yahoo Finance quotes may be delayed and are cached for 15 minutes.")

    columns = st.columns(4)
    for index, quote in enumerate(quotes):
        price = quote["price"]
        currency_symbol = "₹" if quote["currency"] == "INR" else "$"
        value = (
            f"{currency_symbol}{price:,.2f}"
            if price is not None
            else "Unavailable"
        )
        change = quote["change_percent"]
        delta = format_percentage(change) if change is not None else None

        with columns[index % len(columns)]:
            st.metric(
                quote["name"],
                value,
                delta=delta,
                border=True,
                help=f"Yahoo Finance symbol: {quote['symbol']}",
            )