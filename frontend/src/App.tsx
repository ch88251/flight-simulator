import { useEffect, useState } from 'react'
import { AircraftTable } from './components/AircraftTable'
import { useAircraft } from './hooks/useAircraft'

type View = 'table' | 'map'

const VIEWS: { id: View; label: string }[] = [
  { id: 'table', label: 'Table' },
  { id: 'map', label: 'Map' },
]

// The active view is kept in the URL hash (#table / #map) so reloads keep it.
function viewFromHash(): View {
  return window.location.hash === '#map' ? 'map' : 'table'
}

export default function App() {
  const [view, setView] = useState<View>(viewFromHash)
  const { aircraft, error, loading } = useAircraft()

  useEffect(() => {
    const onHashChange = () => setView(viewFromHash())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Flight Simulator</h1>
        <nav className="tabs">
          {VIEWS.map(({ id, label }) => (
            <a key={id} href={`#${id}`} className={view === id ? 'tab active' : 'tab'}>
              {label}
            </a>
          ))}
        </nav>
        <span className="muted">{aircraft.length} aircraft</span>
      </header>

      <main>
        {error && <div className="error">Could not load aircraft: {error}</div>}
        {loading ? (
          <p className="muted">Loading…</p>
        ) : view === 'table' ? (
          <AircraftTable aircraft={aircraft} />
        ) : (
          <p className="muted">Map view coming soon.</p>
        )}
      </main>
    </div>
  )
}
