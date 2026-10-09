import { useEffect, useRef, useState } from 'react'
import {
  CandlestickSeries,
  ColorType,
  createChart,
  HistogramSeries,
  LineSeries,
} from 'lightweight-charts'
import { ChartNoAxesCombined } from 'lucide-react'

const overlayOptions = [
  { key: 'sma20', label: 'SMA 20', color: '#cb7b37' },
  { key: 'sma50', label: 'SMA 50', color: '#3b7f70' },
  { key: 'bb_upper', label: 'Bollinger', color: '#7e78a7' },
]

export default function PriceChart({ candles, prediction, theme }) {
  const containerRef = useRef(null)
  const [visibleOverlays, setVisibleOverlays] = useState(['sma20', 'sma50'])

  useEffect(() => {
    const container = containerRef.current
    if (!container || !candles?.length) return undefined
    const isDark = theme === 'dark'

    const chart = createChart(container, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: isDark ? '#1c2622' : '#fffefa' },
        textColor: isDark ? '#a5b3ac' : '#64736f',
        fontFamily: 'IBM Plex Mono, monospace',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: isDark ? '#2c3a33' : '#edf0e9' },
        horzLines: { color: isDark ? '#2c3a33' : '#edf0e9' },
      },
      rightPriceScale: { borderColor: isDark ? '#43534a' : '#dfe4dc' },
      timeScale: { borderColor: isDark ? '#43534a' : '#dfe4dc', timeVisible: false },
      crosshair: { vertLine: { color: isDark ? '#829189' : '#84958f' }, horzLine: { color: isDark ? '#829189' : '#84958f' } },
    })

    const validCandles = candles.filter(
      (candle) => candle.open != null && candle.high != null && candle.low != null && candle.close != null,
    )
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#2e866a',
      downColor: '#c45e50',
      borderUpColor: '#2e866a',
      borderDownColor: '#c45e50',
      wickUpColor: '#2e866a',
      wickDownColor: '#c45e50',
      priceLineVisible: true,
    })
    candleSeries.setData(validCandles.map((candle) => ({
      time: candle.date,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    })))

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceScaleId: 'volume',
      priceFormat: { type: 'volume' },
      lastValueVisible: false,
      priceLineVisible: false,
    })
    volumeSeries.setData(validCandles.map((candle) => ({
      time: candle.date,
      value: candle.volume || 0,
      color: candle.close >= candle.open ? 'rgba(46, 134, 106, .42)' : 'rgba(196, 94, 80, .38)',
    })))
    chart.priceScale('volume').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } })

    for (const overlay of overlayOptions) {
      if (!visibleOverlays.includes(overlay.key)) continue
      const series = chart.addSeries(LineSeries, {
        color: overlay.color,
        lineWidth: 1,
        crosshairMarkerVisible: false,
        lastValueVisible: false,
        priceLineVisible: false,
      })
      series.setData(validCandles
        .filter((candle) => candle[overlay.key] != null)
        .map((candle) => ({ time: candle.date, value: candle[overlay.key] })))
    }

    if (prediction?.predictions?.length && validCandles.length) {
      const forecast = chart.addSeries(LineSeries, {
        color: '#bb7a2e',
        lineWidth: 3,
        lineStyle: 2,
        crosshairMarkerVisible: true,
        lastValueVisible: true,
        priceLineVisible: false,
      })
      const last = validCandles.at(-1)
      forecast.setData([
        { time: last.date, value: last.close },
        ...prediction.predictions.map((point) => ({
          time: point.date,
          value: point.predicted_close,
        })),
      ])
    }

    chart.timeScale().fitContent()
    return () => chart.remove()
  }, [candles, prediction, theme, visibleOverlays])

  function toggleOverlay(key) {
    setVisibleOverlays((current) => (
      current.includes(key)
        ? current.filter((item) => item !== key)
        : [...current, key]
    ))
  }

  return (
    <div>
      <div className="chart-toolbar">
        <span className="chart-toolbar-label"><ChartNoAxesCombined size={14} /> Overlays</span>
        {overlayOptions.map((overlay) => (
          <button
            aria-pressed={visibleOverlays.includes(overlay.key)}
            className={`overlay-toggle ${visibleOverlays.includes(overlay.key) ? 'is-active' : ''}`}
            key={overlay.key}
            onClick={() => toggleOverlay(overlay.key)}
            type="button"
          >
            <span style={{ '--swatch': overlay.color }} />{overlay.label}
          </button>
        ))}
        {prediction && <span className="forecast-legend"><i /> LSTM forecast</span>}
      </div>
      <div aria-label="Candlestick price chart with volume" className="price-chart" ref={containerRef} />
    </div>
  )
}