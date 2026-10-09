import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import {
  Activity,
  ArrowDownToLine,
  ArrowUpRight,
  BarChart3,
  BellRing,
  Check,
  ChevronDown,
  ChevronUp,
  CircleAlert,
  Copy,
  LoaderCircle,
  Mail,
  Menu,
  Moon,
  Search,
  ShieldCheck,
  Sparkles,
  SunMedium,
  TrendingUp,
  X,
} from 'lucide-react'
import {
  fetchBacktest,
  fetchHistory,
  fetchMarkets,
  fetchPrediction,
} from './api/client.js'

const IndicatorChart = lazy(() => import('./components/IndicatorChart.jsx'))
const PriceChart = lazy(() => import('./components/PriceChart.jsx'))

const periods = ['1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max']
const intervals = [
  { value: '1d', label: '1 day' },
  { value: '1wk', label: '1 week' },
  { value: '1mo', label: '1 month' },
]
const horizons = [5, 10, 15, 30]
const popularSymbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA']
const marketNames = new Set(['S&P 500', 'NASDAQ', 'DOW JONES', 'NIFTY 50', 'BTC', 'ETH', 'Gold', 'Crude Oil'])
const faqItems = [
  { title: 'How often is the data refreshed?', answer: 'The market snapshot is refreshed on demand and the dashboard is designed to surface delays clearly when Yahoo Finance is slow or unavailable.' },
  { title: 'Is the forecast trading advice?', answer: 'No. Forecasts are experimental model outputs for analysis and comparison with a simple baseline, not a buy or sell recommendation.' },
  { title: 'Why does the baseline sometimes beat the model?', answer: 'Market noise and short-history samples make simple baselines surprisingly competitive. The dashboard highlights that through walk-forward evaluation.' },
  { title: 'Can I use this for other tickers?', answer: 'Yes. Search a stock symbol in the site search or enter a ticker manually in the control panel to analyze a different instrument.' },
]

function formatNumber(value, options = {}) {
  if (value == null || !Number.isFinite(Number(value))) return 'Unavailable'
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    ...options,
  }).format(Number(value))
}

function formatQuote(quote) {
  if (quote.price == null) return 'Unavailable'
  const symbol = quote.currency === 'INR' ? '₹' : '$'
  return `${symbol}${formatNumber(quote.price)}`
}

function withUtm(url, utmSource = 'stockpredictor') {
  if (!url) return url
  const hasQuery = url.includes('?')
  const prefix = hasQuery ? '&' : '?'
  return `${url}${prefix}utm_source=${utmSource}`
}

function Metric({ label, value, detail, tone }) {
  return (
    <div className="metric-cell">
      <span className="metric-label">{label}</span>
      <strong className={tone || ''}>{value ?? 'Unavailable'}</strong>
      {detail && <small>{detail}</small>}
    </div>
  )
}

function App() {
  const [symbol, setSymbol] = useState('AAPL')
  const [symbolDraft, setSymbolDraft] = useState('AAPL')
  const [period, setPeriod] = useState('5y')
  const [interval, setInterval] = useState('1d')
  const [horizon, setHorizon] = useState(10)
  const [history, setHistory] = useState(null)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [historyError, setHistoryError] = useState('')
  const [markets, setMarkets] = useState([])
  const [marketError, setMarketError] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [predictionLoading, setPredictionLoading] = useState(false)
  const [predictionError, setPredictionError] = useState('')
  const [backtest, setBacktest] = useState(null)
  const [backtestLoading, setBacktestLoading] = useState(false)
  const [backtestError, setBacktestError] = useState('')
  const [symbolError, setSymbolError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [bannerVisible, setBannerVisible] = useState(true)
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')
  const [searchTerm, setSearchTerm] = useState('')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [showTopButton, setShowTopButton] = useState(false)
  const [scrollProgress, setScrollProgress] = useState(0)
  const [showModal, setShowModal] = useState(false)
  const [pendingAction, setPendingAction] = useState(null)
  const [faqOpen, setFaqOpen] = useState(0)
  const [copyState, setCopyState] = useState('idle')
  const predictionRequestId = useRef(0)
  const backtestRequestId = useRef(0)

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [theme])

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight
      const progress = maxScroll > 0 ? (scrollTop / maxScroll) * 100 : 0
      setScrollProgress(progress)
      setShowTopButton(scrollTop > 240)
    }

    handleScroll()
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    if (!successMessage) return undefined
    const timeout = window.setTimeout(() => setSuccessMessage(''), 2200)
    return () => window.clearTimeout(timeout)
  }, [successMessage])

  const siteSearchResults = useMemo(() => {
    const query = searchTerm.trim().toLowerCase()
    if (!query) return []

    const entries = [
      ...popularSymbols.map((item) => ({ label: `Ticker ${item}`, value: item, kind: 'symbol' })),
      { label: 'AI forecast', value: 'forecast', kind: 'section' },
      { label: 'Market overview', value: 'markets', kind: 'section' },
      { label: 'Backtest evaluation', value: 'backtest', kind: 'section' },
      { label: 'Technical studies', value: 'indicators', kind: 'section' },
      ...Array.from(marketNames).map((item) => ({ label: `${item} market`, value: item, kind: 'market' })),
    ]

    return entries.filter((entry) => entry.label.toLowerCase().includes(query) || entry.value.toLowerCase().includes(query)).slice(0, 6)
  }, [searchTerm])

  useEffect(() => {
    const controller = new AbortController()
    setHistoryLoading(true)
    setHistoryError('')

    fetchHistory(symbol, { period, interval }, controller.signal)
      .then(setHistory)
      .catch((error) => {
        if (error.name !== 'AbortError') {
          setHistory(null)
          setHistoryError(error.message)
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setHistoryLoading(false)
      })

    return () => controller.abort()
  }, [symbol, period, interval])

  useEffect(() => {
    predictionRequestId.current += 1
    backtestRequestId.current += 1
    setPrediction(null)
    setPredictionError('')
    setPredictionLoading(false)
    setBacktest(null)
    setBacktestError('')
    setBacktestLoading(false)
  }, [symbol, period, interval, horizon])

  useEffect(() => {
    const controller = new AbortController()
    fetchMarkets(controller.signal)
      .then((result) => {
        setMarkets(result.quotes.filter((quote) => marketNames.has(quote.name)))
        setMarketError('')
      })
      .catch((error) => {
        if (error.name !== 'AbortError') setMarketError(error.message)
      })
    return () => controller.abort()
  }, [])

  function submitSymbol(event) {
    event.preventDefault()
    const next = symbolDraft.trim().toUpperCase()
    if (!/^[A-Z0-9.^=_-]{1,20}$/.test(next)) {
      setSymbolError('Enter a valid ticker symbol.')
      return
    }
    setSymbolError('')
    setSymbol(next)
    setSymbolDraft(next)
    setSuccessMessage(`${next} loaded successfully.`)
    setSearchTerm('')
  }

  function applySearch(item) {
    if (!item) return
    if (item.kind === 'symbol' || item.kind === 'market') {
      const next = String(item.value).trim().toUpperCase()
      setSymbolDraft(next)
      setSymbol(next)
      setSuccessMessage(`${next} loaded successfully.`)
      setSearchTerm('')
      return
    }

    const target = item.value.toLowerCase()
    const sectionMap = {
      forecast: () => {
        setPendingAction('forecast')
        setShowModal(true)
      },
      markets: () => document.getElementById('markets')?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
      backtest: () => document.getElementById('backtest')?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
      indicators: () => document.getElementById('indicators')?.scrollIntoView({ behavior: 'smooth', block: 'start' }),
    }

    if (sectionMap[target]) sectionMap[target]()
    setSearchTerm('')
  }

  async function generatePrediction() {
    const requestId = ++predictionRequestId.current
    setPredictionLoading(true)
    setPredictionError('')
    setPrediction(null)
    setSuccessMessage('Generating forecast…')
    try {
      const result = await fetchPrediction(symbol, {
        period,
        interval,
        future_days: horizon,
      })
      if (requestId === predictionRequestId.current) setPrediction(result)
      if (requestId === predictionRequestId.current) setSuccessMessage(`Forecast ready for ${symbol}.`)
    } catch (error) {
      if (requestId === predictionRequestId.current) setPredictionError(error.message)
    } finally {
      if (requestId === predictionRequestId.current) setPredictionLoading(false)
    }
  }

  async function evaluateForecast() {
    const requestId = ++backtestRequestId.current
    setBacktestLoading(true)
    setBacktestError('')
    setBacktest(null)
    setSuccessMessage('Evaluating forecast…')
    try {
      const result = await fetchBacktest(symbol, {
        period,
        interval,
        horizon,
        windows: 3,
      })
      if (requestId === backtestRequestId.current) setBacktest(result)
      if (requestId === backtestRequestId.current) setSuccessMessage(`Backtest complete for ${symbol}.`)
    } catch (error) {
      if (requestId === backtestRequestId.current) setBacktestError(error.message)
    } finally {
      if (requestId === backtestRequestId.current) setBacktestLoading(false)
    }
  }

  const metrics = history?.metrics
  const candles = history?.candles || []
  const baselineWins = backtest && backtest.baseline.mae <= backtest.lstm.mae

  async function handleCopySummary() {
    if (!prediction && !backtest) return
    const summary = `StockPredictor · ${symbol} · ${period} · Horizon ${horizon} bars. ${prediction ? 'Forecast generated.' : 'Backtest available.'}`
    try {
      await navigator.clipboard.writeText(summary)
      setCopyState('success')
    } catch {
      setCopyState('idle')
    }
    window.setTimeout(() => setCopyState('idle'), 1800)
  }

  function confirmPendingAction() {
    setShowModal(false)
    if (pendingAction === 'forecast') generatePrediction()
    if (pendingAction === 'backtest') evaluateForecast()
    setPendingAction(null)
  }

  const footerDate = new Date().toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">Skip to content</a>
      <div className="scroll-progress"><span style={{ width: `${scrollProgress}%` }} /></div>
      <div className="bg-orb orb-1" />
      <div className="bg-orb orb-2" />

      {bannerVisible && (
        <div className="announcement-bar">
          <div className="announcement-inner">
            <BellRing size={14} />
            <span>Market data is refreshed on demand. Forecasts remain experimental and are shown alongside baseline comparisons.</span>
          </div>
          <button className="close-banner" onClick={() => setBannerVisible(false)} aria-label="Dismiss announcement" type="button">
            <X size={14} />
          </button>
        </div>
      )}

      <motion.header
        className="topbar"
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
      >
        <a className="brand" href="#top" aria-label="StockPredictor home">
          <span className="brand-mark"><TrendingUp size={18} strokeWidth={2.3} /></span>
          <span>Stock<span>Predictor</span></span>
        </a>

        <div className="topbar-actions">
          <div className="site-search">
            <Search size={14} />
            <input
              aria-label="Search site content"
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search symbols or content"
              type="text"
              value={searchTerm}
            />
            {searchTerm && siteSearchResults.length > 0 && (
              <div className="search-results" aria-live="polite">
                {siteSearchResults.map((item) => (
                  <button key={`${item.kind}-${item.value}`} onClick={() => applySearch(item)} type="button">
                    <span>{item.label}</span>
                    <small>{item.kind}</small>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            aria-label="Toggle theme"
            className="theme-toggle"
            onClick={() => setTheme((current) => (current === 'light' ? 'dark' : 'light'))}
            type="button"
          >
            {theme === 'light' ? <Moon size={14} /> : <SunMedium size={14} />}
            {theme === 'light' ? 'Dark' : 'Light'}
          </button>

          <button
            aria-label="Open mobile menu"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen((current) => !current)}
            type="button"
          >
            <Menu size={16} />
          </button>
        </div>
      </motion.header>

      {mobileMenuOpen && (
        <nav className="mobile-menu" aria-label="Mobile navigation">
          <button onClick={() => setTheme((current) => (current === 'light' ? 'dark' : 'light'))} type="button">
            {theme === 'light' ? 'Switch to dark' : 'Switch to light'}
          </button>
          <button onClick={() => document.getElementById('markets')?.scrollIntoView({ behavior: 'smooth' })} type="button">Markets</button>
          <button onClick={() => document.getElementById('indicators')?.scrollIntoView({ behavior: 'smooth' })} type="button">Indicators</button>
          <button onClick={() => document.getElementById('faq')?.scrollIntoView({ behavior: 'smooth' })} type="button">FAQ</button>
        </nav>
      )}

      <main id="main-content" className="page-wrap">
        <motion.section
          className="workspace-heading"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.04 }}
        >
          <div className="heading-copy">
            <p className="eyebrow">Market intelligence / fintech</p>
            <h1>Stock analysis</h1>
          </div>
          <div className="heading-meta">
            <span className="mini-pill"><Sparkles size={13} /> AI forecast</span>
            <p className="heading-note">Signal, charts, and forecast quality in one calm workspace.</p>
          </div>
        </motion.section>

        {successMessage && <div className="inline-success"><ShieldCheck size={15} /> <span>{successMessage}</span></div>}

        <section className="market-section" id="markets">
          <motion.div
            className="section-heading"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.28, delay: 0.08 }}
          >
            <div>
              <p className="eyebrow">Cross-asset snapshot</p>
              <h2>Global markets</h2>
            </div>
            <span className="cache-note">Quotes can be delayed · cached 15 min</span>
          </motion.div>
          {marketError && <p className="inline-warning">Market snapshot unavailable: {marketError}</p>}
          <div className="market-grid">
            {markets.length ? markets.map((quote, index) => (
              <motion.article
                className="market-tile"
                key={quote.symbol}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.28, delay: 0.08 + index * 0.03 }}
                whileHover={{ y: -4, scale: 1.015 }}
              >
                <span>{quote.name}</span>
                <strong>{formatQuote(quote)}</strong>
                <small className={quote.change_percent >= 0 ? 'positive' : 'negative'}>
                  {quote.change_percent == null ? 'Change unavailable' : `${quote.change_percent >= 0 ? '+' : ''}${formatNumber(quote.change_percent)}%`}
                </small>
              </motion.article>
            )) : Array.from({ length: 8 }, (_, index) => (
              <motion.article
                className="market-tile market-loading"
                key={index}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.28, delay: 0.08 + index * 0.03 }}
              >
                <span>{['S&P 500', 'NASDAQ', 'DOW JONES', 'NIFTY 50', 'BTC', 'ETH', 'Gold', 'Crude Oil'][index]}</span>
                <strong>—</strong><small>Loading quote</small>
              </motion.article>
            ))}
          </div>
        </section>

        <div className="dashboard-layout">
          <aside className="control-rail">
            <section className="panel control-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Instrument</p>
                  <h2>Explore</h2>
                </div>
                <Search size={17} />
              </div>
              <form onSubmit={submitSymbol}>
                <label className="field-label" htmlFor="ticker">Ticker symbol</label>
                <div className="ticker-field">
                  <input
                    autoCapitalize="characters"
                    autoComplete="off"
                    id="ticker"
                    maxLength={20}
                    onChange={(event) => setSymbolDraft(event.target.value.toUpperCase())}
                    placeholder="AAPL"
                    spellCheck="false"
                    value={symbolDraft}
                  />
                  <button aria-label="Load ticker" className="icon-submit" title="Load ticker" type="submit">
                    <ArrowUpRight size={17} />
                  </button>
                </div>
                {symbolError && <p className="field-error">{symbolError}</p>}
                <div className="quick-symbols" aria-label="Popular tickers">
                  {popularSymbols.map((item) => (
                    <button
                      className={item === symbol ? 'selected' : ''}
                      key={item}
                      onClick={() => { setSymbolDraft(item); setSymbol(item); setSymbolError(''); setSuccessMessage(`${item} loaded successfully.`) }}
                      type="button"
                    >
                      {item}
                    </button>
                  ))}
                </div>

                <label className="field-label" htmlFor="period">Historical period</label>
                <select id="period" onChange={(event) => setPeriod(event.target.value)} value={period}>
                  {periods.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>

                <label className="field-label" htmlFor="interval">Data interval</label>
                <select id="interval" onChange={(event) => setInterval(event.target.value)} value={interval}>
                  {intervals.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
                </select>

                <label className="field-label" htmlFor="horizon">Forecast horizon</label>
                <select id="horizon" onChange={(event) => setHorizon(Number(event.target.value))} value={horizon}>
                  {horizons.map((item) => <option key={item} value={item}>{item} bars</option>)}
                </select>
              </form>

              <div className="action-stack">
                <button className="primary-button" disabled={predictionLoading || !history} onClick={() => { setPendingAction('forecast'); setShowModal(true) }} type="button">
                  {predictionLoading ? <LoaderCircle className="spin" size={16} /> : <Sparkles size={16} />}
                  {predictionLoading ? 'Training model…' : 'Generate forecast'}
                </button>
                <button className="secondary-button" disabled={backtestLoading || !history} onClick={() => { setPendingAction('backtest'); setShowModal(true) }} type="button">
                  {backtestLoading ? <LoaderCircle className="spin" size={16} /> : <Activity size={16} />}
                  {backtestLoading ? 'Evaluating windows…' : 'Evaluate forecast'}
                </button>
              </div>
              <p className="control-footnote">Forecasts are experimental estimates, not investment advice.</p>
            </section>
            <section className="rail-note">
              <BarChart3 size={17} />
              <div><strong>Model transparency</strong><span>Forecast quality is compared with a simple last-close baseline.</span></div>
            </section>
          </aside>

          <div className="main-column">
            {historyError && (
              <section className="error-banner"><CircleAlert size={18} /><span>{historyError}</span></section>
            )}

            {historyLoading && <section className="panel loading-panel"><LoaderCircle className="spin" size={20} /> Loading {symbol} market history…</section>}

            {!historyLoading && history && (
              <>
                <motion.section
                  className="metrics-panel"
                  aria-label="Stock metrics"
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.09 }}
                >
                  <Metric label={metrics.company_name || symbol} value={metrics.current_price_formatted} detail={metrics.day_change ? `${metrics.day_change.change >= 0 ? '+' : ''}${formatNumber(metrics.day_change.change)} (${metrics.day_change.percent}%) today` : 'Day change unavailable'} tone="metric-primary" />
                  <Metric label="Market cap" value={metrics.market_cap_formatted} />
                  <Metric label="P/E ratio" value={metrics.pe_ratio == null ? '—' : formatNumber(metrics.pe_ratio)} />
                  <Metric label="Volume" value={metrics.volume_formatted} />
                  <Metric label="52-week high" value={metrics.fifty_two_week_high_formatted} tone="positive" />
                  <Metric label="52-week low" value={metrics.fifty_two_week_low_formatted} tone="negative" />
                </motion.section>

                <motion.section
                  className="panel price-panel"
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.12 }}
                >
                  <div className="panel-heading price-panel-heading">
                    <div>
                      <p className="eyebrow">{symbol} / {period} / {interval}</p>
                      <h2>Price history</h2>
                    </div>
                    <span className="chart-key"><i /> OHLC candles <i className="volume-key" /> Volume</span>
                  </div>
                  <Suspense fallback={<div className="chart-skeleton">Loading price chart…</div>}>
                    <PriceChart candles={candles} prediction={prediction} theme={theme} />
                  </Suspense>
                  <p className="chart-disclaimer">Yahoo Finance data may be delayed. Forecast dates are approximate and do not account for exchange holidays.</p>
                </motion.section>

                <section className="indicator-section" id="indicators">
                  <div className="section-heading indicator-title">
                    <div><p className="eyebrow">Calculated from selected history</p><h2>Technical studies</h2></div>
                    <span className="cache-note">{candles.length.toLocaleString()} data bars</span>
                  </div>
                  <div className="indicator-grid">
                    <Suspense fallback={<div className="chart-skeleton">Loading technical studies…</div>}>
                    <IndicatorChart candles={candles} theme={theme} series={[
                      { key: 'sma20', name: 'SMA 20', color: '#cb7b37' },
                      { key: 'sma50', name: 'SMA 50', color: '#3b7f70' },
                      { key: 'ema20', name: 'EMA 20', color: '#7e78a7' },
                    ]} title="Moving averages" />
                    <IndicatorChart candles={candles} theme={theme} series={[
                      { key: 'bb_upper', name: 'Upper', color: '#7e78a7' },
                      { key: 'bb_middle', name: 'Middle', color: '#cb7b37' },
                      { key: 'bb_lower', name: 'Lower', color: '#7e78a7' },
                    ]} title="Bollinger bands" />
                    <IndicatorChart candles={candles} domain={[0, 100]} referenceLines={[{ value: 30 }, { value: 70 }]} theme={theme} series={[
                      { key: 'rsi', name: 'RSI', color: '#3b7f70' },
                    ]} title="Relative strength index" />
                    <IndicatorChart barKey="histogram" candles={candles} theme={theme} series={[
                      { key: 'macd', name: 'MACD', color: '#3b7f70' },
                      { key: 'signal', name: 'Signal', color: '#cb7b37' },
                    ]} title="MACD" />
                    </Suspense>
                  </div>
                </section>

                {prediction && (
                  <motion.section
                    className="result-panel forecast-result"
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.28, delay: 0.14 }}
                  >
                    <div className="result-heading"><div><p className="eyebrow">Experimental model output</p><h2>LSTM forecast</h2></div><span>{prediction.future_days} future bars</span></div>
                    <div className="result-actions">
                      <p>Recursive price estimate based on the selected history. Treat as experimental; it is not a trading recommendation.</p>
                      <button className="mini-button" onClick={handleCopySummary} type="button">
                        {copyState === 'success' ? <Check size={14} /> : <Copy size={14} />}
                        {copyState === 'success' ? 'Copied' : 'Copy'}
                      </button>
                    </div>
                  </motion.section>
                )}
                {predictionError && <section className="error-banner"><CircleAlert size={18} /><span>{predictionError}</span></section>}

                {backtest && (
                  <motion.section
                    id="backtest"
                    className="result-panel backtest-result"
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.28, delay: 0.17 }}
                  >
                    <div className="result-heading"><div><p className="eyebrow">Chronological evaluation</p><h2>Walk-forward backtest</h2></div><span>{backtest.windows} windows · {backtest.horizon} bars each</span></div>
                    <p className="backtest-explainer">Each model trains on earlier bars and predicts a later window. Lower errors are better; this historical test does not guarantee future accuracy.</p>
                    <div className="backtest-metrics">
                      {['mae', 'rmse', 'mape'].map((key) => {
                        const lstmValue = backtest.lstm[key]
                        const baselineValue = backtest.baseline[key]
                        const delta = lstmValue == null || baselineValue == null ? null : baselineValue - lstmValue
                        return (
                          <div className="backtest-metric" key={key}>
                            <span>{key.toUpperCase()}</span>
                            <strong>LSTM {lstmValue == null ? 'N/A' : formatNumber(lstmValue)}</strong>
                            <small className={delta == null ? '' : delta > 0 ? 'positive' : 'negative'}>
                              {delta == null ? 'Baseline unavailable' : `${delta > 0 ? '+' : ''}${formatNumber(delta)} vs baseline`}
                            </small>
                          </div>
                        )
                      })}
                    </div>
                    <div className="table-scroll">
                      <table>
                        <thead><tr><th>Window</th><th>Training bars</th><th>LSTM MAE</th><th>Baseline MAE</th><th>Lower error</th></tr></thead>
                        <tbody>{backtest.window_results.map((window) => (
                          <tr key={window.window}>
                            <td>{String(window.window).padStart(2, '0')}</td>
                            <td>{window.training_bars.toLocaleString()}</td>
                            <td>{formatNumber(window.lstm.mae)}</td>
                            <td>{formatNumber(window.baseline.mae)}</td>
                            <td>{window.lstm.mae < window.baseline.mae ? 'LSTM' : 'Last close'}</td>
                          </tr>
                        ))}</tbody>
                      </table>
                    </div>
                    <div className="backtest-verdict">
                      {baselineWins ? <ArrowDownToLine size={16} /> : <ArrowUpRight size={16} />}
                      Lower aggregate MAE on these windows: {baselineWins ? 'last-close baseline' : 'LSTM'}.
                    </div>
                  </motion.section>
                )}
                {backtestError && <section className="error-banner"><CircleAlert size={18} /><span>{backtestError}</span></section>}

                <section className="panel faq-panel" id="faq">
                  <div className="result-heading faq-heading">
                    <div><p className="eyebrow">Support</p><h2>FAQ</h2></div>
                    <span>Updated {footerDate}</span>
                  </div>
                  <div className="faq-list">
                    {faqItems.map((item, index) => {
                      const isOpen = faqOpen === index
                      return (
                        <div className={`faq-item ${isOpen ? 'open' : ''}`} key={item.title}>
                          <button onClick={() => setFaqOpen(isOpen ? -1 : index)} type="button">
                            <span>{item.title}</span>
                            {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                          </button>
                          {isOpen && <p>{item.answer}</p>}
                        </div>
                      )
                    })}
                  </div>
                </section>
              </>
            )}
          </div>
        </div>
      </main>

      <button
        aria-label="Back to top"
        className={`top-button ${showTopButton ? 'visible' : ''}`}
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        type="button"
      >
        <ChevronUp size={18} />
      </button>

      <a className="floating-contact" href={withUtm('mailto:hello@stockpredictor.app?subject=StockPredictor%20support')}>
        <Mail size={16} />
        Contact
      </a>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-card" onClick={(event) => event.stopPropagation()} role="dialog" aria-modal="true">
            <div className="modal-header">
              <h3>{pendingAction === 'forecast' ? 'Generate forecast' : 'Evaluate forecast'}</h3>
              <button className="modal-close" onClick={() => setShowModal(false)} type="button" aria-label="Close modal">
                <X size={16} />
              </button>
            </div>
            <p>
              {pendingAction === 'forecast'
                ? `Run a new forecast for ${symbol} using the current settings?`
                : `Evaluate the current ${symbol} model against the baseline with the selected horizon?`}
            </p>
            <div className="modal-actions">
              <button className="secondary-button" onClick={() => setShowModal(false)} type="button">Cancel</button>
              <button className="primary-button" onClick={confirmPendingAction} type="button">Confirm</button>
            </div>
          </div>
        </div>
      )}

      <footer className="page-footer">
        <span>StockPredictor AI</span>
        <span>Last updated {footerDate} · Data by Yahoo Finance · For analysis, not investment advice</span>
      </footer>
    </div>
  )
}

export default App