"""
============================================================
StockPredictor AI
components/header.py
============================================================

Application Header

Responsible for:
- Main title
- Hero banner
- Project information
- Live date and time
============================================================
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
    Render application header.
    """

    now = datetime.now()

    current_date = now.strftime("%A, %d %B %Y")

    current_time = now.strftime("%I:%M %p")

    st.markdown(
        f"""
<h1 class="main-title">
📈 {APP_NAME}
</h1>

<p class="sub-title">
{APP_DESCRIPTION}
</p>
""",
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns([2, 1, 1])

    with left:
        st.success("🟢 Live Yahoo Finance Data")

    with middle:
        st.info(f"📅 {current_date}")

    with right:
        st.info(f"🕒 {current_time}")

    st.divider()


# ==========================================================
# HERO SECTION
# ==========================================================

def render_hero() -> None:
    """
    Render hero banner.
    """

    st.markdown(
        """
<div style="
background: linear-gradient(135deg,#2563EB,#1D4ED8);
padding:30px;
border-radius:18px;
margin-bottom:20px;
">

<h2 style="color:white;margin:0 0 12px 0;">

Analyze. Predict. Invest Smarter.

</h2>

<p style="
color:#DBEAFE;
font-size:17px;
line-height:1.6;
margin:0;
">

StockPredictor AI combines interactive stock charts,
technical indicators, historical analysis and artificial
intelligence to help investors make better decisions.

</p>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# PROJECT STATUS
# ==========================================================

def render_project_status() -> None:
    """
    Display application information.
    """

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Version",
            APP_VERSION,
        )

    with col2:
        st.metric(
            "Framework",
            "Streamlit",
        )

    with col3:
        st.metric(
            "Data Source",
            "Yahoo Finance",
        )

    with col4:
        st.metric(
            "Status",
            "Development",
        )