"""
============================================================
StockPredictor AI
utils/formatting.py
============================================================

Formatting utilities used throughout the application.
"""

from __future__ import annotations

from typing import Optional


# ==========================================================
# CURRENCY
# ==========================================================

def format_currency(value: Optional[float]) -> str:
    """
    Format a number as USD currency.
    """

    if value is None:
        return "--"

    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "--"


# ==========================================================
# PERCENTAGE
# ==========================================================

def format_percentage(value: Optional[float]) -> str:
    """
    Format a percentage value.
    """

    if value is None:
        return "--"

    try:
        value = float(value)

        if value > 0:
            return f"+{value:.2f}%"

        return f"{value:.2f}%"

    except (TypeError, ValueError):
        return "--"


# ==========================================================
# DECIMAL
# ==========================================================

def format_decimal(
    value: Optional[float],
    decimals: int = 2,
) -> str:
    """
    Format a decimal number.
    """

    if value is None:
        return "--"

    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "--"


# ==========================================================
# LARGE NUMBERS
# ==========================================================

def format_large_number(value: Optional[float]) -> str:
    """
    Format large numeric values.
    """

    if value is None:
        return "--"

    try:

        value = float(value)

        abs_value = abs(value)

        if abs_value >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f}T"

        if abs_value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if abs_value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if abs_value >= 1_000:
            return f"{value / 1_000:.2f}K"

        return f"{value:.0f}"

    except (TypeError, ValueError):
        return "--"


# ==========================================================
# MARKET CAP
# ==========================================================

def format_market_cap(value: Optional[float]) -> str:
    """
    Format market capitalization.
    """

    return format_large_number(value)


# ==========================================================
# VOLUME
# ==========================================================

def format_volume(value: Optional[float]) -> str:
    """
    Format trading volume.
    """

    return format_large_number(value)


# ==========================================================
# PRICE CHANGE
# ==========================================================

def format_price_change(
    current: Optional[float],
    previous: Optional[float],
) -> str:
    """
    Calculate and format percentage price change.
    """

    if current is None or previous is None:
        return "--"

    try:

        current = float(current)
        previous = float(previous)

        if previous == 0:
            return "--"

        change = ((current - previous) / previous) * 100

        return format_percentage(change)

    except (TypeError, ValueError, ZeroDivisionError):
        return "--"


# ==========================================================
# BOOLEAN
# ==========================================================

def format_boolean(value: bool) -> str:
    """
    Format boolean values.
    """

    return "Yes" if value else "No"


# ==========================================================
# FILE SIZE
# ==========================================================

def format_file_size(size: int) -> str:
    """
    Format file sizes into human-readable units.
    """

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"

    return f"{size / (1024 ** 3):.2f} GB"