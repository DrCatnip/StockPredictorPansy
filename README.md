# StockPredictor AI

Stock analysis dashboard with market data, technical indicators, and experimental forecasts. The active product direction is a React frontend backed by a FastAPI service. The original Streamlit app remains available as a fallback while the migration is validated.

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

The Render blueprint deploys the FastAPI API and React static frontend as separate services. Configure `ALLOWED_ORIGINS` and `VITE_API_BASE_URL` to match the assigned service URLs if the Render service names change.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

API contract tests use the development client dependency:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

## Streamlit Fallback

The previous dashboard is still in `app.py`:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
