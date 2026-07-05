"""
============================================================
StockPredictor AI
utils/constants.py
============================================================

Global application constants.

This module contains application-wide configuration
that should never be hardcoded elsewhere.
"""

from __future__ import annotations

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "StockPredictor AI"

APP_VERSION = "2.0.0"

APP_DESCRIPTION = (
    "AI Powered Stock Market Analysis Platform"
)

# ==========================================================
# DEFAULT STOCK SETTINGS
# ==========================================================

DEFAULT_SYMBOL = "AAPL"

DEFAULT_PERIOD = "5y"

DEFAULT_INTERVAL = "1d"

# ==========================================================
# DATA OPTIONS
# ==========================================================

AVAILABLE_PERIODS = [
    "1mo",
    "3mo",
    "6mo",
    "1y",
    "2y",
    "5y",
    "10y",
    "max",
]

AVAILABLE_INTERVALS = [
    "1d",
    "1wk",
    "1mo",
]

# ==========================================================
# AI PREDICTION
# ==========================================================

PREDICTION_DAYS = [
    5,
    10,
    15,
    30,
]

# ==========================================================
# CHART SETTINGS
# ==========================================================

DEFAULT_CHART_HEIGHT = 650

VOLUME_CHART_HEIGHT = 260

INDICATOR_CHART_HEIGHT = 320

# ==========================================================
# COLORS
# ==========================================================

PRIMARY_COLOR = "#2563EB"

SECONDARY_COLOR = "#1D4ED8"

SUCCESS_COLOR = "#22C55E"

WARNING_COLOR = "#F59E0B"

DANGER_COLOR = "#EF4444"

BACKGROUND_COLOR = "#0B1220"

GRID_COLOR = "#1F2937"

TEXT_COLOR = "#FFFFFF"

# ==========================================================
# CACHE
# ==========================================================

CACHE_TTL = 3600

# ==========================================================
# FUTURE FEATURES
# ==========================================================

ENABLE_AI = False

ENABLE_NEWS = False

ENABLE_PORTFOLIO = False

ENABLE_WATCHLIST = False

ENABLE_SENTIMENT = False