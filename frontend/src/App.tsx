import { useEffect, useState } from 'react'
import { AircraftMap } from './components/AircraftMap'
import { AircraftTable } from './components/AircraftTable'
import { useAircraft } from './hooks/useAircraft'
import { useAirports } from './hooks/useAirports'

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
  const { airports, error: airportsError } = useAirports()

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

      <main className={view === 'map' ? 'map-view' : undefined}>
        {error && <div className="error">Could not load aircraft: {error}</div>}
        {airportsError && <div className="error">Could not load airports: {airportsError}</div>}
        {view === 'map' ? (
          <AircraftMap aircraft={aircraft} airports={airports} />
        ) : loading ? (
          <p className="muted">Loading…</p>
        ) : (
          <AircraftTable aircraft={aircraft} />
        )}
      </main>
    </div>
  )
}
