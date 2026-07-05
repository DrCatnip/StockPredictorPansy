"""
============================================================
StockPredictor AI
utils/page_config.py
============================================================

Application page configuration and global styling.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

def configure_page() -> None:
    """
    Configure the Streamlit application.
    """

    st.set_page_config(
        page_title="StockPredictor AI",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ==========================================================
# LOAD CUSTOM CSS
# ==========================================================

def load_css() -> None:
    """
    Load the custom stylesheet.
    """

    css_file = Path("assets/styles.css")

    if not css_file.exists():
        return

    with css_file.open("r", encoding="utf-8") as file:

        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True,
        )


# ==========================================================
# INITIALIZE APPLICATION
# ==========================================================

def initialize_page() -> None:
    """
    Initialize the application.
    """

    configure_page()

    load_css()