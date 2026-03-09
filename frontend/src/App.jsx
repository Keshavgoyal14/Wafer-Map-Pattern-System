import { Activity, BarChart3, Cpu, History, Upload } from 'lucide-react'
import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { AnalyzePage } from './pages/AnalyzePage'
import { AnalyticsPage } from './pages/AnalyticsPage'
import { HistoryPage } from './pages/HistoryPage'
import { OverviewPage } from './pages/OverviewPage'

const navItems = [
  { to: '/', label: 'Overview', icon: Activity },
  { to: '/analyze', label: 'Analyze', icon: Upload },
  { to: '/history', label: 'History', icon: History },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
]

function WaferLogo() {
  return (
    <svg width="48" height="48" viewBox="0 0 48 48" aria-hidden="true">
      <defs>
        <linearGradient id="waferGradientReact" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#19f0d0" />
          <stop offset="100%" stopColor="#0ea5a5" />
        </linearGradient>
      </defs>
      <rect x="1.5" y="1.5" width="45" height="45" rx="14" fill="rgba(16, 185, 129, 0.1)" stroke="rgba(45, 212, 191, 0.18)" />
      <rect x="15" y="15" width="18" height="18" rx="3.5" fill="none" stroke="url(#waferGradientReact)" strokeWidth="2.2" />
      <path d="M19 24h10M24 19v10" stroke="url(#waferGradientReact)" strokeWidth="2.2" strokeLinecap="round" />
      <path d="M12 18h4M12 24h4M12 30h4M32 12v4M24 12v4M16 12v4M36 18h-4M36 24h-4M36 30h-4M32 36v-4M24 36v-4M16 36v-4" stroke="rgba(126, 247, 229, 0.55)" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  )
}

export default function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <section className="sidebar-brand">
          <div className="sidebar-brand-head">
            <WaferLogo />
            <div className="sidebar-brand-copy">
              <strong>WaferAI</strong>
              <span>Defect Analytics</span>
            </div>
          </div>
        </section>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
            >
              <span className="sidebar-link-icon"><item.icon size={18} strokeWidth={2.1} /></span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-footer-chip">
            <Cpu size={14} strokeWidth={2.1} />
            <span>Models online</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/analyze" element={<AnalyzePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/overview" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}