export function DashboardHeader({ eyebrow, title, description, actions }) {
  return (
    <section className="dashboard-header-card">
      <div>
        {eyebrow ? <div className="dashboard-eyebrow">{eyebrow}</div> : null}
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {actions ? <div className="dashboard-header-actions">{actions}</div> : null}
    </section>
  )
}

export function Hero({ eyebrow, title, description }) {
  return (
    <DashboardHeader eyebrow={eyebrow} title={title} description={description} />
  )
}

export function StatGrid({ items }) {
  return (
    <section className="stat-grid">
      {items.map((item) => (
        <article className="stat-card" key={item.label}>
          <div className="stat-label">{item.label}</div>
          <div className="stat-value">{item.value}</div>
          <div className="stat-caption">{item.caption}</div>
        </article>
      ))}
    </section>
  )
}

export function Panel({ title, children }) {
  return (
    <section className="panel-card">
      <h3>{title}</h3>
      <div>{children}</div>
    </section>
  )
}

export function KeyValueList({ items }) {
  return (
    <div className="kv-list">
      {items.map(([key, value]) => (
        <div className="kv-item" key={key}>
          <div className="kv-key">{key}</div>
          <div className="kv-value">{value}</div>
        </div>
      ))}
    </div>
  )
}

export function MiniGrid({ items }) {
  return (
    <section className="mini-grid">
      {items.map((item) => (
        <article className="mini-card" key={item.title}>
          <strong>{item.title}</strong>
          <span>{item.body}</span>
        </article>
      ))}
    </section>
  )
}

export function PieChart({ items, total }) {
  const palette = ['#d96c2f', '#0f766e', '#f29b4b', '#295f98', '#7c5cfa', '#c2410c']
  const stops = []
  let cursor = 0

  items.forEach((item, index) => {
    const next = cursor + item.ratio * 100
    const color = palette[index % palette.length]
    stops.push(`${color} ${cursor}% ${next}%`)
    cursor = next
  })

  const background = `conic-gradient(${stops.join(', ')})`

  return (
    <section className="panel-card">
      <h3>Defect Mix</h3>
      <div className="pie-layout-react">
        <div className="pie-card-react">
          <div className="pie-ring" style={{ background }}>
            <div className="pie-hole">
              <span>Wafers</span>
              <strong>{total}</strong>
            </div>
          </div>
        </div>
        <div className="pie-legend-react">
          {items.map((item, index) => (
            <div className="pie-legend-row" key={item.label}>
              <span className="pie-swatch" style={{ background: palette[index % palette.length] }} />
              <span className="pie-label">{item.label}</span>
              <span className="pie-meta">{item.count} | {(item.ratio * 100).toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export function LoadingState({ label }) {
  return <div className="loading-state">{label}</div>
}

export function ErrorState({ message }) {
  return <div className="error-state">{message}</div>
}