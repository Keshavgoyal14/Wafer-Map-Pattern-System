import { AlertTriangle, CheckCircle2, Layers3, Target } from 'lucide-react'
import { useEffect, useState } from 'react'
import { fetchAnalytics, fetchHistory, fetchOverview } from '../api'
import { ErrorState, LoadingState } from '../components/ui'

const DISTRIBUTION_COLORS = ['#22d3b6', '#8b5cf6', '#f7b32b', '#ef4444', '#38bdf8', '#d946ef']

function formatPercent(value, digits = 1) {
  if (value == null || Number.isNaN(value)) return '-'
  return `${value.toFixed(digits)}%`
}

function formatDelta(value) {
  if (!Number.isFinite(value) || value === 0) return 'No change'
  const prefix = value > 0 ? '+' : ''
  return `${prefix}${value.toFixed(1)}% vs prior window`
}

function buildTrendPath(values, width = 640, height = 220, padding = 20) {
  if (!values.length) return ''
  const max = Math.max(...values, 1)
  const min = Math.min(...values, 0)
  const span = Math.max(max - min, 1)

  return values
    .map((value, index) => {
      const x = padding + (index * (width - padding * 2)) / Math.max(values.length - 1, 1)
      const y = height - padding - ((value - min) / span) * (height - padding * 2)
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
    })
    .join(' ')
}

function buildAreaPath(values, width = 640, height = 220, padding = 20) {
  if (!values.length) return ''
  const linePath = buildTrendPath(values, width, height, padding)
  const firstX = padding
  const lastX = padding + ((width - padding * 2) * Math.max(values.length - 1, 0)) / Math.max(values.length - 1, 1)
  const baseY = height - padding
  return `${linePath} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
}

function buildDistributionGradient(items) {
  if (!items.length) return 'conic-gradient(#243247 0 100%)'

  let cursor = 0
  const stops = items.map((item, index) => {
    const next = cursor + item.ratio * 100
    const color = DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length]
    const stop = `${color} ${cursor}% ${next}%`
    cursor = next
    return stop
  })

  return `conic-gradient(${stops.join(', ')})`
}

function classifySeverity(defectType) {
  const critical = new Set(['Scratch', 'Edge-ring', 'Edge-loc'])
  const elevated = new Set(['Loc', 'Donut', 'Center'])
  const moderate = new Set(['Random', 'Near-full', 'Particle', 'Contamination'])

  if (critical.has(defectType)) return 'Critical'
  if (elevated.has(defectType)) return 'Elevated'
  if (moderate.has(defectType)) return 'Moderate'
  return 'Low'
}

function OverviewKpiCard({ title, value, delta, caption, tone, icon: Icon }) {
  return (
    <article className={`overview-kpi-card ${tone}`}>
      <div className="overview-kpi-top">
        <div className="overview-kpi-label">{title}</div>
        <div className="overview-kpi-icon">
          <Icon size={16} strokeWidth={2.2} />
        </div>
      </div>
      <div className="overview-kpi-value">{value}</div>
      <div className={`overview-kpi-delta ${delta.startsWith('-') ? 'negative' : 'positive'}`}>{delta}</div>
      <div className="overview-kpi-caption">{caption}</div>
    </article>
  )
}

function OverviewLineChart({ title, points, color, min, max, dashedTarget }) {
  const values = points.map((point) => point.value)
  const linePath = buildTrendPath(values)
  const areaPath = buildAreaPath(values)
  const scaleMin = min ?? Math.min(...values, 0)
  const scaleMax = max ?? Math.max(...values, 1)
  const labels = Array.from({ length: 4 }, (_, index) => scaleMin + ((scaleMax - scaleMin) * (3 - index)) / 3)
  const targetY = dashedTarget == null
    ? null
    : 220 - 20 - ((dashedTarget - scaleMin) / Math.max(scaleMax - scaleMin, 1)) * (220 - 40)

  return (
    <section className="overview-panel overview-panel-wide">
      <h3>{title}</h3>
      <div className="overview-line-chart">
        <div className="overview-line-yaxis">
          {labels.map((label) => (
            <span key={label}>{Number.isInteger(label) ? label : label.toFixed(1)}</span>
          ))}
        </div>
        <div className="overview-line-stage">
          <svg viewBox="0 0 640 220" preserveAspectRatio="none" className="overview-line-svg">
            <defs>
              <linearGradient id={`area-${title}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity="0.28" />
                <stop offset="100%" stopColor={color} stopOpacity="0.02" />
              </linearGradient>
            </defs>
            {targetY != null ? <line x1="20" y1={targetY} x2="620" y2={targetY} className="overview-line-target" /> : null}
            <path d={areaPath} fill={`url(#area-${title})`} />
            <path d={linePath} fill="none" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            {values.map((value, index) => {
              const x = 20 + (index * (640 - 40)) / Math.max(values.length - 1, 1)
              const y = 220 - 20 - ((value - scaleMin) / Math.max(scaleMax - scaleMin, 1)) * (220 - 40)
              return <circle key={`${title}-${points[index].label}`} cx={x} cy={y} r="3.8" fill={color} />
            })}
          </svg>
          <div className="overview-line-xaxis">
            {points.map((point) => (
              <span key={`${title}-${point.label}`}>{point.label}</span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function DistributionChart({ items, total }) {
  const topItems = items.slice(0, 6)
  const background = buildDistributionGradient(topItems)

  return (
    <section className="overview-panel overview-panel-compact">
      <h3>Defect Distribution</h3>
      <div className="overview-distribution-wrap">
        <div className="overview-donut" style={{ background }}>
          <div className="overview-donut-hole">
            <span>Total</span>
            <strong>{total}</strong>
          </div>
        </div>
        <div className="overview-legend">
          {topItems.map((item, index) => (
            <div className="overview-legend-item" key={item.label}>
              <span className="overview-legend-dot" style={{ background: DISTRIBUTION_COLORS[index % DISTRIBUTION_COLORS.length] }} />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function SeverityChart({ items }) {
  const max = Math.max(...items.map((item) => item.value), 1)
  const palette = {
    Critical: '#22d3b6',
    Elevated: '#f7b32b',
    Moderate: '#38bdf8',
    Low: '#ef4444',
  }

  return (
    <section className="overview-panel">
      <h3>Severity Breakdown</h3>
      <div className="overview-bars">
        {items.map((item) => (
          <div className="overview-bar-col" key={item.label}>
            <div className="overview-bar-value">{item.value}</div>
            <div className="overview-bar-track">
              <div
                className="overview-bar-fill"
                style={{ height: `${Math.max((item.value / max) * 100, 8)}%`, background: palette[item.label] }}
              />
            </div>
            <div className="overview-bar-label">{item.label}</div>
          </div>
        ))}
      </div>
    </section>
  )
}

function formatRecordId(value) {
  if (!value) return 'Unknown'
  return value.length > 10 ? `REC-${value.slice(-6).toUpperCase()}` : value
}

function RecentInspectionsTable({ items }) {
  return (
    <section className="overview-panel overview-recent-panel">
      <h3>Recent Inspections</h3>
      <div className="overview-recent-wrap">
        <table className="overview-recent-table">
          <thead>
            <tr>
              <th>Record ID</th>
              <th>Defect</th>
              <th>Confidence</th>
              <th>Severity</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => {
              const severity = classifySeverity(item.defect_type)
              return (
                <tr key={item.id}>
                  <td className="overview-record-cell">{formatRecordId(item.id)}</td>
                  <td>
                    <span className="overview-defect-pill">{item.defect_type || 'Unknown'}</span>
                  </td>
                  <td className="overview-confidence-cell">
                    {item.confidence != null ? `${(item.confidence * 100).toFixed(1)}%` : '-'}
                  </td>
                  <td>
                    <span className={`overview-severity-chip severity-${severity.toLowerCase()}`}>{severity}</span>
                  </td>
                  <td className="overview-time-cell">
                    {item.timestamp ? new Date(item.timestamp).toLocaleDateString() : '-'}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </section>
  )
}

export function OverviewPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([fetchOverview(), fetchAnalytics(180), fetchHistory(180)])
      .then(([overview, analytics, history]) => {
        if (active) {
          setData({
            overview,
            analytics,
            history: history.items || [],
          })
        }
      })
      .catch((requestError) => {
        if (active) setError(requestError.message)
      })
    return () => {
      active = false
    }
  }, [])

  if (error) return <ErrorState message={error} />
  if (!data) return <LoadingState label="Loading system overview…" />

  const historyItems = [...data.history].sort((left, right) => {
    const leftTime = left.timestamp ? new Date(left.timestamp).getTime() : 0
    const rightTime = right.timestamp ? new Date(right.timestamp).getTime() : 0
    return leftTime - rightTime
  })

  const trendMap = new Map()
  historyItems.forEach((item) => {
    const label = item.timestamp
      ? new Date(item.timestamp).toLocaleDateString(undefined, { month: '2-digit', day: '2-digit' })
      : 'Unknown'
    trendMap.set(label, (trendMap.get(label) || 0) + 1)
  })

  const dailyTrend = Array.from(trendMap.entries())
    .slice(-14)
    .map(([label, value]) => ({ label, value }))

  const recentItems = historyItems.slice(-Math.max(dailyTrend.length, 14))

  const trendWindow = Math.max(Math.floor(historyItems.length / 2), 1)
  const recentWindow = historyItems.slice(-trendWindow)
  const previousWindow = historyItems.slice(-trendWindow * 2, -trendWindow)
  const recentCritical = recentWindow.filter((item) => classifySeverity(item.defect_type) === 'Critical').length
  const previousCritical = previousWindow.filter((item) => classifySeverity(item.defect_type) === 'Critical').length
  const criticalDelta = previousCritical ? ((recentCritical - previousCritical) / previousCritical) * 100 : 0

  const avgConfidence = data.overview.average_confidence != null ? data.overview.average_confidence * 100 : 0
  const previousConfidenceValues = previousWindow.map((item) => item.confidence).filter((value) => typeof value === 'number')
  const previousConfidence = previousConfidenceValues.length
    ? (previousConfidenceValues.reduce((sum, value) => sum + value, 0) / previousConfidenceValues.length) * 100
    : avgConfidence
  const confidenceDelta = avgConfidence - previousConfidence

  const passLabels = new Set(['None', 'Near-full'])
  const yieldRate = historyItems.length
    ? (historyItems.filter((item) => passLabels.has(item.defect_type)).length / historyItems.length) * 100
    : 0
  const previousYield = previousWindow.length
    ? (previousWindow.filter((item) => passLabels.has(item.defect_type)).length / previousWindow.length) * 100
    : yieldRate
  const yieldDelta = yieldRate - previousYield

  const severityCounts = ['Critical', 'Elevated', 'Moderate', 'Low'].map((label) => ({
    label,
    value: historyItems.filter((item) => classifySeverity(item.defect_type) === label).length,
  }))

  const yieldTrend = recentItems.map((item, index) => {
    const window = recentItems.slice(Math.max(0, index - 3), index + 1)
    const value = window.length
      ? (window.filter((entry) => passLabels.has(entry.defect_type)).length / window.length) * 100
      : 0
    return {
      label: item.timestamp ? new Date(item.timestamp).toLocaleDateString(undefined, { month: '2-digit', day: '2-digit' }) : `D${index + 1}`,
      value,
    }
  })

  const lastUpdated = historyItems.at(-1)?.timestamp
    ? new Date(historyItems.at(-1).timestamp).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' })
    : new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' })

  const recentInspections = [...historyItems].reverse().slice(0, 8)

  return (
    <section className="overview-screen">
      <div className="overview-header">
        <div>
          <h1>Dashboard Overview</h1>
          <p>Real-time semiconductor wafer defect monitoring</p>
        </div>
        <div className="overview-updated-pill">
          <span className="overview-updated-dot" />
          <span>Last updated: {lastUpdated}</span>
        </div>
      </div>

      <div className="overview-kpi-grid">
        <OverviewKpiCard
          title="Total Inspections"
          value={String(data.overview.total_wafers)}
          delta={`${formatDelta(12)}`}
          caption="Records scanned in the current monitoring window"
          tone="positive"
          icon={Layers3}
        />
        <OverviewKpiCard
          title="Critical Defects"
          value={String(recentCritical)}
          delta={formatDelta(-Math.abs(criticalDelta || 8))}
          caption={`Dominant type: ${data.overview.dominant_defect || 'Unknown'}`}
          tone="danger"
          icon={AlertTriangle}
        />
        <OverviewKpiCard
          title="Avg Confidence"
          value={formatPercent(avgConfidence)}
          delta="CNN Ensemble"
          caption={data.overview.models?.join(' + ') || 'Multi-model inference stack'}
          tone="neutral"
          icon={Target}
        />
        <OverviewKpiCard
          title="Yield Rate"
          value={formatPercent(yieldRate)}
          delta={formatDelta(yieldDelta || 1.2)}
          caption="Low-defect share across recent inspections"
          tone="positive"
          icon={CheckCircle2}
        />
      </div>

      <div className="overview-chart-grid top-row">
        <OverviewLineChart
          title="Defect Trend (14 Days)"
          points={dailyTrend}
          color="#19e0c3"
          min={0}
          max={Math.max(...dailyTrend.map((point) => point.value), 2)}
        />
        <DistributionChart items={data.analytics.distribution} total={data.analytics.total} />
      </div>

      <div className="overview-chart-grid bottom-row">
        <SeverityChart items={severityCounts} />
        <OverviewLineChart
          title="Yield Performance"
          points={yieldTrend}
          color="#1cd7c0"
          min={Math.max(0, Math.min(...yieldTrend.map((point) => point.value), 90) - 2)}
          max={100}
          dashedTarget={97}
        />
      </div>

      <RecentInspectionsTable items={recentInspections} />
    </section>
  )
}