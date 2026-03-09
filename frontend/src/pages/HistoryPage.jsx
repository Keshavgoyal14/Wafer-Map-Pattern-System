import { useEffect, useMemo, useState } from 'react'
import { fetchHistory } from '../api'
import { DashboardHeader, ErrorState, LoadingState, MiniGrid, Panel, StatGrid } from '../components/ui'

export function HistoryPage() {
  const [items, setItems] = useState([])
  const [error, setError] = useState('')
  const [selectedDefect, setSelectedDefect] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    let active = true
    fetchHistory()
      .then((payload) => {
        if (active) setItems(payload.items || [])
      })
      .catch((requestError) => {
        if (active) setError(requestError.message)
      })
    return () => {
      active = false
    }
  }, [])

  const availableDefects = useMemo(() => ['All', ...new Set(items.map((item) => item.defect_type))], [items])

  const filtered = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return items.filter((item) => {
      if (selectedDefect !== 'All' && item.defect_type !== selectedDefect) return false
      if (!query) return true
      return [item.id, item.defect_type, item.insight].join(' ').toLowerCase().includes(query)
    })
  }, [items, searchQuery, selectedDefect])

  if (error) return <ErrorState message={error} />
  if (!items.length && !error) return <LoadingState label="Loading wafer history…" />

  const confidenceValues = items.map((item) => item.confidence).filter((value) => typeof value === 'number')
  const linkedImages = items.filter((item) => item.image_url).length
  const linkedHeatmaps = items.filter((item) => item.heatmap_url).length

  return (
    <>
      <DashboardHeader
        eyebrow="Traceability"
        title="Wafer Inspection History"
        description="A cleaner inspection ledger for reviewing historical predictions, confidence, AI notes, and linked output artifacts."
      />

      <StatGrid
        items={[
          { label: 'Inspections', value: String(items.length), caption: 'Recent records fetched from MongoDB.' },
          { label: 'Linked Images', value: String(linkedImages), caption: 'Entries with a stored image artifact URL.' },
          { label: 'Linked Heatmaps', value: String(linkedHeatmaps), caption: 'Entries with an uploaded heatmap artifact.' },
          { label: 'Average Confidence', value: confidenceValues.length ? `${((confidenceValues.reduce((sum, value) => sum + value, 0) / confidenceValues.length) * 100).toFixed(1)}%` : '-', caption: 'Mean model confidence across records with a prediction value.' },
        ]}
      />

      <Panel title="Review workflow">
        <p>Use the filters below to narrow the ledger, spot unusually low-confidence predictions, and jump to stored artifacts when deeper review is needed.</p>
      </Panel>

      <div className="filters-row">
        <label>
          <span>Filter by defect</span>
          <select value={selectedDefect} onChange={(event) => setSelectedDefect(event.target.value)}>
            {availableDefects.map((defect) => (
              <option key={defect} value={defect}>{defect}</option>
            ))}
          </select>
        </label>
        <label>
          <span>Search insight or record id</span>
          <input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Type to filter history" />
        </label>
      </div>

      <MiniGrid
        items={[
          { title: 'Filtered records', body: String(filtered.length) },
          { title: 'Current filter', body: selectedDefect },
          { title: 'Search query', body: searchQuery || 'None' },
        ]}
      />

      <Panel title="Inspection ledger">
        <div className="history-table-wrap">
          <table className="history-table-react">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Defect</th>
                <th>Confidence</th>
                <th>Insight</th>
                <th>Image</th>
                <th>Heatmap</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id}>
                  <td>{item.timestamp ? new Date(item.timestamp).toLocaleString() : '-'}</td>
                  <td><span className="pill-react">{item.defect_type}</span></td>
                  <td>{item.confidence != null ? `${(item.confidence * 100).toFixed(2)}%` : '-'}</td>
                  <td><div className="insight-snippet-react">{item.insight || '-'}</div></td>
                  <td>{item.image_url ? <a className="link-chip-react" href={item.image_url} target="_blank" rel="noreferrer">Open image</a> : '-'}</td>
                  <td>{item.heatmap_url ? <a className="link-chip-react" href={item.heatmap_url} target="_blank" rel="noreferrer">Open heatmap</a> : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  )
}