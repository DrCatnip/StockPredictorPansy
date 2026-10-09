from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routers.stock import router

app = FastAPI(
    title="StockPredictor AI",
    description="Market data, technical indicators, and experimental stock forecasts.",
    version="4.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
async def root():
    return {"name": "StockPredictor AI", "version": "4.0.0", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}