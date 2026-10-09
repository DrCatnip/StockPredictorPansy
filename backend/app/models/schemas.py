from __future__ import annotations

from pydantic import BaseModel


class Candle(BaseModel):
    date: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    sma20: float | None = None
    sma50: float | None = None
    sma200: float | None = None
    ema20: float | None = None
    ema50: float | None = None
    rsi: float | None = None
    macd: float | None = None
    signal: float | None = None
    histogram: float | None = None
    bb_upper: float | None = None
    bb_middle: float | None = None
    bb_lower: float | None = None
    atr: float | None = None
    vwap: float | None = None


class PriceChange(BaseModel):
    change: float
    percent: float
    direction: str


class DashboardMetrics(BaseModel):
    company_name: str
    current_price: float | None = None
    current_price_formatted: str | None = None
    day_change: PriceChange | None = None
    market_cap: float | None = None
    market_cap_formatted: str | None = None
    pe_ratio: float | None = None
    volume: float | None = None
    volume_formatted: str | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_high_formatted: str | None = None
    fifty_two_week_low: float | None = None
    fifty_two_week_low_formatted: str | None = None


class StockHistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    candles: list[Candle]
    metrics: DashboardMetrics


class PredictionPoint(BaseModel):
    date: str
    predicted_close: float


class PredictionResponse(BaseModel):
    symbol: str
    interval: str
    future_days: int
    predictions: list[PredictionPoint]


class MarketQuote(BaseModel):
    name: str
    symbol: str
    currency: str
    price: float | None = None
    change_percent: float | None = None


class MarketOverviewResponse(BaseModel):
    quotes: list[MarketQuote]


class ErrorMetrics(BaseModel):
    mae: float
    rmse: float
    mape: float | None


class BacktestWindow(BaseModel):
    window: int
    training_bars: int
    test_start_bar: int
    test_end_bar: int
    lstm: ErrorMetrics
    baseline: ErrorMetrics


class BacktestResponse(BaseModel):
    symbol: str
    interval: str
    horizon: int
    windows: int
    starting_training_bars: int
    lstm: ErrorMetrics
    baseline: ErrorMetrics
    window_results: list[BacktestWindow]


class ErrorResponse(BaseModel):
    detail: str