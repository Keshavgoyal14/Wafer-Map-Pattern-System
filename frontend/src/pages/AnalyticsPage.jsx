import { Activity, AlertTriangle, BarChart3, PieChart } from 'lucide-react'
import { useEffect, useState } from 'react'
import { fetchAnalytics, fetchHistory } from '../api'
import { DashboardHeader, ErrorState, LoadingState } from '../components/ui'

const CHART_COLORS = ['#26d3ba', '#8b5cf6', '#f7b32b', '#ef4444', '#38bdf8', '#d946ef']

function classifySeverity(defectType) {
  const critical = new Set(['Scratch', 'Edge-ring', 'Edge-loc'])
  const high = new Set(['Loc', 'Center', 'Donut'])
  const medium = new Set(['Random', 'Particle', 'Contamination'])

  if (critical.has(defectType)) return 'Critical'
  if (high.has(defectType)) return 'High'
  if (medium.has(defectType)) return 'Medium'
  return 'Low'
}

function buildRadarGeometry(items, radius = 100, center = 130) {
  const total = items.length
  const max = Math.max(...items.map((item) => item.count), 1)

  const getPoint = (index, scale = 1) => {
    const angle = (-Math.PI / 2) + (index * Math.PI * 2) / total
    const x = center + Math.cos(angle) * radius * scale
    const y = center + Math.sin(angle) * radius * scale
    return { x, y }
  }

  const levels = [0.25, 0.5, 0.75, 1].map((level) => items.map((_, index) => getPoint(index, level)))
  const axes = items.map((_, index) => getPoint(index, 1))
  const dataPoints = items.map((item, index) => getPoint(index, item.count / max))

  return {
    levels,
    axes,
    dataPoints,
    labels: items.map((item, index) => ({
      label: item.label,
      ...getPoint(index, 1.16),
    })),
  }
}

function polygonPath(points) {
  return points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ') + ' Z'
}

function buildDonutGradient(items) {
  let cursor = 0
  const stops = items.map((item, index) => {
    const next = cursor + item.ratio * 100
    const stop = `${CHART_COLORS[index % CHART_COLORS.length]} ${cursor}% ${next}%`
    cursor = next
    return stop
  })
  return `conic-gradient(${stops.join(', ')})`
}

export function AnalyticsPage() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([fetchAnalytics(), fetchHistory(240)])
      .then(([analytics, history]) => {
        if (active) {
          setData({
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
  if (!data) return <LoadingState label="Loading defect analytics…" />

  const analytics = data.analytics
  const topItems = analytics.distribution.slice(0, 6)
  const radarItems = topItems.length ? topItems : [{ label: 'No data', count: 0, ratio: 0 }]
  const radar = buildRadarGeometry(radarItems)
  const donutBackground = buildDonutGradient(topItems)

  const severityBuckets = { Low: 0, Medium: 0, High: 0, Critical: 0 }
  data.history.forEach((item) => {
    severityBuckets[classifySeverity(item.defect_type)] += 1
  })

  const severityRows = [
    { label: 'Low', value: severityBuckets.Low, color: '#26d3ba' },
    { label: 'Medium', value: severityBuckets.Medium, color: '#f7b32b' },
    { label: 'High', value: severityBuckets.High, color: '#38bdf8' },
    { label: 'Critical', value: severityBuckets.Critical, color: '#ef4444' },
  ]
  const maxSeverity = Math.max(...severityRows.map((row) => row.value), 1)
  const highPriority = severityBuckets.High + severityBuckets.Critical

  return (
    <section className="analytics-screen">
      <DashboardHeader
        eyebrow="Pattern Monitoring"
        title="Defect Analytics"
        description="Deep dive into defect patterns and quality metrics"
      />

      <div className="analytics-grid analytics-grid-top">
        <section className="analytics-panel">
          <div className="analytics-panel-head">
            <div className="analytics-panel-title"><Activity size={16} /> <span>Defect Radar</span></div>
          </div>
          <div className="analytics-radar-wrap">
            <svg viewBox="0 0 260 260" className="analytics-radar-svg" aria-hidden="true">
              {radar.levels.map((level, index) => (
                <path key={`level-${index}`} d={polygonPath(level)} className="analytics-radar-grid" />
              ))}
              {radar.axes.map((point, index) => (
                <line key={`axis-${radarItems[index].label}`} x1="130" y1="130" x2={point.x} y2={point.y} className="analytics-radar-axis" />
              ))}
              <path d={polygonPath(radar.dataPoints)} className="analytics-radar-area" />
              <path d={polygonPath(radar.dataPoints)} className="analytics-radar-line" />
              {radar.dataPoints.map((point, index) => (
                <circle key={`point-${radarItems[index].label}`} cx={point.x} cy={point.y} r="4" className="analytics-radar-point" />
              ))}
              {radar.labels.map((label) => (
                <text key={label.label} x={label.x} y={label.y} textAnchor="middle" className="analytics-radar-label">{label.label}</text>
              ))}
            </svg>
          </div>
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-head">
            <div className="analytics-panel-title"><PieChart size={16} /> <span>Defect Type Distribution</span></div>
          </div>
          <div className="analytics-donut-layout">
            <div className="analytics-donut-stage">
              <div className="analytics-donut-ring" style={{ background: donutBackground }}>
                <div className="analytics-donut-center">
                  <span>Total</span>
                  <strong>{analytics.total}</strong>
                </div>
              </div>
            </div>
            <div className="analytics-donut-legend">
              {topItems.map((item, index) => (
                <div key={item.label} className="analytics-donut-row">
                  <span className="analytics-donut-dot" style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} />
                  <div className="analytics-donut-copy">
                    <strong>{item.label}</strong>
                    <span>{item.count} cases</span>
                  </div>
                  <div className="analytics-donut-percent">{(item.ratio * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      <div className="analytics-grid analytics-grid-bottom">
        <section className="analytics-panel analytics-panel-accent">
          <div className="analytics-panel-head">
            <div className="analytics-panel-title"><BarChart3 size={16} /> <span>Avg Detections per Defect Type</span></div>
          </div>
          <div className="analytics-hbars">
            {topItems.map((item, index) => (
              <div key={item.label} className="analytics-hbar-row">
                <div className="analytics-hbar-label">{item.label}</div>
                <div className="analytics-hbar-track">
                  <div
                    className="analytics-hbar-fill"
                    style={{
                      width: `${item.ratio * 100}%`,
                      background: CHART_COLORS[index % CHART_COLORS.length],
                    }}
                  />
                </div>
                <div className="analytics-hbar-value">{item.count}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="analytics-panel">
          <div className="analytics-panel-head">
            <div className="analytics-panel-title"><AlertTriangle size={16} /> <span>Severity Analysis</span></div>
          </div>
          <div className="analytics-severity-list">
            {severityRows.map((row) => (
              <div key={row.label} className="analytics-severity-row">
                <div className="analytics-severity-meta">
                  <strong>{row.label}</strong>
                  <span>{row.value} ({data.history.length ? ((row.value / data.history.length) * 100).toFixed(1) : '0.0'}%)</span>
                </div>
                <div className="analytics-severity-track">
                  <div className="analytics-severity-fill" style={{ width: `${(row.value / maxSeverity) * 100}%`, background: row.color }} />
                </div>
              </div>
            ))}
          </div>
          <div className="analytics-quality-summary">
            <strong>Quality Summary:</strong> {highPriority} high-priority defects require immediate attention across {data.history.length || analytics.total} inspections.
          </div>
        </section>
      </div>
    </section>
  )
}