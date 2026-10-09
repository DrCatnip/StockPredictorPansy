import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function shortDate(value) {
  return value?.slice(0, 7) || ''
}

export default function IndicatorChart({
  title,
  candles,
  series,
  theme,
  barKey,
  referenceLines = [],
  domain,
}) {
  const isDark = theme === 'dark'
  const axisColor = isDark ? '#9aaaA1' : '#84918c'
  const gridColor = isDark ? '#34433b' : '#edf0e9'
  const hasData = candles?.some((candle) => series.some(({ key }) => candle[key] != null))

  return (
    <section className="panel indicator-panel">
      <div className="panel-heading compact-heading">
        <div>
          <p className="eyebrow">Technical study</p>
          <h3>{title}</h3>
        </div>
      </div>
      {hasData ? (
        <ResponsiveContainer height={210} width="100%">
          <ComposedChart data={candles} margin={{ top: 8, right: 12, bottom: 0, left: -18 }}>
            <CartesianGrid stroke={gridColor} strokeDasharray="3 5" vertical={false} />
            <XAxis
              axisLine={false}
              dataKey="date"
              minTickGap={32}
              tick={{ fill: axisColor, fontSize: 10, fontFamily: 'IBM Plex Mono, monospace' }}
              tickFormatter={shortDate}
              tickLine={false}
            />
            <YAxis
              axisLine={false}
              domain={domain || ['auto', 'auto']}
              tick={{ fill: axisColor, fontSize: 10, fontFamily: 'IBM Plex Mono, monospace' }}
              tickLine={false}
              width={52}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: isDark ? '#1c2622' : '#ffffff',
                border: `1px solid ${isDark ? '#43534a' : '#dfe4dc'}`,
                borderRadius: 4,
                color: isDark ? '#e8eeea' : '#111827',
                fontSize: 12,
              }}
              labelFormatter={(label) => label}
            />
            {referenceLines.map((line) => (
              <ReferenceLine
                key={line.value}
                stroke={isDark ? '#58685f' : '#b9c1ba'}
                strokeDasharray="4 4"
                y={line.value}
              />
            ))}
            {barKey && <Bar dataKey={barKey} fill="#88a99b" maxBarSize={8} opacity={0.6} />}
            {series.map((item) => (
              <Line
                connectNulls
                dataKey={item.key}
                dot={false}
                key={item.key}
                name={item.name}
                stroke={item.color}
                strokeWidth={1.7}
                type="monotone"
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>
      ) : (
        <div className="chart-empty">Indicator values are not available for this range.</div>
      )}
      <div className="indicator-legend">
        {series.map((item) => (
          <span key={item.key}><i style={{ background: item.color }} />{item.name}</span>
        ))}
        {barKey && <span><i className="legend-bar" />Histogram</span>}
      </div>
    </section>
  )
}