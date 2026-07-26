"""
============================================================
StockPredictor AI
components/header.py
============================================================

Professional Dashboard Header
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from utils.constants import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
)


# ==========================================================
# HEADER
# ==========================================================

def render_header() -> None:
    """
    Render dashboard header.
    """

    now = datetime.now()

    current_date = now.strftime("%d %b %Y")
    current_time = now.strftime("%I:%M %p")

    left, right = st.columns([4, 1])

    with left:

        st.markdown(
            f"""
# 📈 {APP_NAME}

### {APP_DESCRIPTION}
"""
        )

    with right:

        st.metric(
            "Today",
            current_date,
        )

        st.metric(
            "Time",
            current_time,
        )

    st.divider()


# ==========================================================
# HERO
# ==========================================================

def render_hero() -> None:
    """
    Render hero section.
    """

    st.markdown(
        """
<div class="hero-card">

<h1 class="hero-title">
🚀 Analyze. Predict. Invest Smarter.
</h1>

<p class="hero-subtitle">

Professional AI-powered stock market analytics with
interactive charts, technical indicators,
live market data and future machine learning predictions.

</p>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# STATUS
# ==========================================================

def render_project_status() -> None:
    """
    Render project status cards.
    """

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.success("🟢 Live Data")

    with c2:
        st.info("📊 Yahoo Finance")

    with c3:
        st.info("⚡ Streamlit")

    with c4:
        st.success(f"Version {APP_VERSION}")