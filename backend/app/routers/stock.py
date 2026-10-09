from __future__ import annotations

import math
import re

from fastapi import APIRouter, HTTPException, Query
from fastapi.concurrency import run_in_threadpool

from backend.app.core.constants import (
    AVAILABLE_INTERVALS,
    AVAILABLE_PERIODS,
    BACKTEST_WINDOWS,
    DEFAULT_INTERVAL,
    DEFAULT_PERIOD,
    DEFAULT_SYMBOL,
    PREDICTION_DAYS,
)
from backend.app.models.schemas import (
    BacktestResponse,
    Candle,
    MarketOverviewResponse,
    PredictionResponse,
    StockHistoryResponse,
)
from backend.app.services.indicators import calculate_indicators
from backend.app.services.lstm_service import backtest_walk_forward, predict_stock
from backend.app.services.yahoo_service import (
    StockDataLoader,
    fetch_market_overview,
)

router = APIRouter(prefix="/api", tags=["market"])
SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9.^=_-]{1,20}$")


def _validate_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(normalized):
        raise HTTPException(status_code=400, detail="Invalid ticker symbol.")
    return normalized


def _safe_float(value) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _load_history(symbol: str, period: str, interval: str):
    history = StockDataLoader(symbol).history(period=period, interval=interval)
    if history.empty:
        raise HTTPException(status_code=404, detail=f"No market data found for '{symbol}'.")
    return history


@router.get("/markets", response_model=MarketOverviewResponse)
async def get_markets():
    return MarketOverviewResponse(
        quotes=await run_in_threadpool(fetch_market_overview)
    )


@router.get("/stocks/{symbol}/history", response_model=StockHistoryResponse)
async def get_history(
    symbol: str = DEFAULT_SYMBOL,
    period: str = Query(default=DEFAULT_PERIOD),
    interval: str = Query(default=DEFAULT_INTERVAL),
):
    symbol = _validate_symbol(symbol)
    if period not in AVAILABLE_PERIODS:
        raise HTTPException(status_code=400, detail=f"Invalid period. Choose one of {AVAILABLE_PERIODS}.")
    if interval not in AVAILABLE_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Choose one of {AVAILABLE_INTERVALS}.")

    history = await run_in_threadpool(_load_history, symbol, period, interval)
    history = calculate_indicators(history)
    metrics = await run_in_threadpool(StockDataLoader(symbol).dashboard_metrics)
    candles = [
        Candle(
            date=index.strftime("%Y-%m-%d"),
            open=_safe_float(row["Open"]),
            high=_safe_float(row["High"]),
            low=_safe_float(row["Low"]),
            close=_safe_float(row["Close"]),
            volume=_safe_float(row["Volume"]),
            sma20=_safe_float(row.get("SMA20")),
            sma50=_safe_float(row.get("SMA50")),
            sma200=_safe_float(row.get("SMA200")),
            ema20=_safe_float(row.get("EMA20")),
            ema50=_safe_float(row.get("EMA50")),
            rsi=_safe_float(row.get("RSI")),
            macd=_safe_float(row.get("MACD")),
            signal=_safe_float(row.get("Signal")),
            histogram=_safe_float(row.get("Histogram")),
            bb_upper=_safe_float(row.get("BB_Upper")),
            bb_middle=_safe_float(row.get("BB_Middle")),
            bb_lower=_safe_float(row.get("BB_Lower")),
            atr=_safe_float(row.get("ATR")),
            vwap=_safe_float(row.get("VWAP")),
        )
        for index, row in history.iterrows()
    ]
    return StockHistoryResponse(
        symbol=symbol,
        period=period,
        interval=interval,
        candles=candles,
        metrics=metrics,
    )


async def _prediction_history(symbol: str, period: str, interval: str):
    if period not in AVAILABLE_PERIODS:
        raise HTTPException(status_code=400, detail=f"Invalid period. Choose one of {AVAILABLE_PERIODS}.")
    if interval not in AVAILABLE_INTERVALS:
        raise HTTPException(status_code=400, detail=f"Invalid interval. Choose one of {AVAILABLE_INTERVALS}.")
    return await run_in_threadpool(_load_history, symbol, period, interval)


@router.get("/stocks/{symbol}/predict", response_model=PredictionResponse)
async def get_prediction(
    symbol: str,
    period: str = Query(default=DEFAULT_PERIOD),
    interval: str = Query(default=DEFAULT_INTERVAL),
    future_days: int = Query(default=10),
    epochs: int = Query(default=10, ge=1, le=50),
):
    symbol = _validate_symbol(symbol)
    if future_days not in PREDICTION_DAYS:
        raise HTTPException(status_code=400, detail=f"future_days must be one of {PREDICTION_DAYS}.")
    history = await _prediction_history(symbol, period, interval)
    try:
        result = await run_in_threadpool(
            predict_stock,
            symbol,
            period,
            interval,
            history,
            future_days,
            epochs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PredictionResponse(**result)


@router.get("/stocks/{symbol}/backtest", response_model=BacktestResponse)
async def get_backtest(
    symbol: str,
    period: str = Query(default=DEFAULT_PERIOD),
    interval: str = Query(default=DEFAULT_INTERVAL),
    horizon: int = Query(default=30),
    windows: int = Query(default=3),
    epochs: int = Query(default=10, ge=1, le=50),
):
    symbol = _validate_symbol(symbol)
    if horizon not in PREDICTION_DAYS:
        raise HTTPException(status_code=400, detail=f"horizon must be one of {PREDICTION_DAYS}.")
    if windows not in BACKTEST_WINDOWS:
        raise HTTPException(status_code=400, detail=f"windows must be one of {BACKTEST_WINDOWS}.")
    history = await _prediction_history(symbol, period, interval)
    try:
        result = await run_in_threadpool(
            backtest_walk_forward,
            symbol,
            period,
            interval,
            history,
            horizon,
            windows,
            epochs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return BacktestResponse(**result)