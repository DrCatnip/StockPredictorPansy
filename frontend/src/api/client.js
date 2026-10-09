const baseUrl = import.meta.env.VITE_API_BASE_URL || ''

async function get(path, signal) {
  const response = await fetch(`${baseUrl}${path}`, { signal })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }
  return data
}

function query(parameters) {
  return new URLSearchParams(parameters).toString()
}

export function fetchHistory(symbol, options, signal) {
  return get(
    `/api/stocks/${encodeURIComponent(symbol)}/history?${query(options)}`,
    signal,
  )
}

export function fetchMarkets(signal) {
  return get('/api/markets', signal)
}

export function fetchPrediction(symbol, options, signal) {
  return get(
    `/api/stocks/${encodeURIComponent(symbol)}/predict?${query(options)}`,
    signal,
  )
}

export function fetchBacktest(symbol, options, signal) {
  return get(
    `/api/stocks/${encodeURIComponent(symbol)}/backtest?${query(options)}`,
    signal,
  )
}