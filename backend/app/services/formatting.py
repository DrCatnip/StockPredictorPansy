from __future__ import annotations

import math
from typing import Any


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def format_currency(value: Any) -> str | None:
    number = _finite_float(value)
    return f"${number:,.2f}" if number is not None else None


def format_price_change(current: Any, previous: Any) -> dict[str, Any] | None:
    current_value = _finite_float(current)
    previous_value = _finite_float(previous)
    if current_value is None or previous_value in (None, 0):
        return None

    change = current_value - previous_value
    return {
        "change": round(change, 2),
        "percent": round(change / previous_value * 100, 2),
        "direction": "up" if change >= 0 else "down",
    }


def _format_abbreviated(value: Any, currency: bool = False) -> str | None:
    number = _finite_float(value)
    if number is None:
        return None
    prefix = "$" if currency else ""
    for threshold, suffix in (
        (1_000_000_000_000, "T"),
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    ):
        if abs(number) >= threshold:
            return f"{prefix}{number / threshold:.2f}{suffix}"
    return f"{prefix}{number:,.0f}"


def format_market_cap(value: Any) -> str | None:
    return _format_abbreviated(value, currency=True)


def format_volume(value: Any) -> str | None:
    return _format_abbreviated(value)