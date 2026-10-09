# StockPredictor AI

Stock analysis dashboard with market data, technical indicators, and experimental forecasts, built with a React frontend and FastAPI backend.

## Features

- Yahoo Finance history, company metrics, and cached global-market snapshots
- Candlestick/volume chart with moving-average and Bollinger overlays
- RSI and MACD studies
- LSTM forecasts with interval-aware dates
- Three-window walk-forward evaluation against a last-close baseline
- Typed API responses, request validation, and loading/error states

Forecasts are experimental and are not investment advice. Yahoo Finance data can be delayed.

## Stack

- Frontend: React, Vite, Recharts, Lightweight Charts
- API: FastAPI, Pydantic
- Data/model: yfinance, pandas, NumPy, TensorFlow 2.21/Keras, scikit-learn
- Local runtime: Python 3.12 and Node.js 24+

## Run Locally

Create the Python environment and install backend dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Start the API from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

In another terminal, install and start the frontend:

```powershell
npm install --prefix frontend
npm run dev --prefix frontend
```

Open `http://localhost:5173`. The API docs are at `http://localhost:8000/docs`. Vite proxies `/api` to the local FastAPI server.

## Deploy

The Render blueprint deploys a free FastAPI web service and React static frontend as separate services. Create or update the blueprint from this repository's `render.yaml`. The frontend and API origins are configured for `stockpredictor-web.onrender.com` and `stockpredictor-api.onrender.com`.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

API contract tests use the development client dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```
