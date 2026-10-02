import type { Aircraft, AirportRef } from '../types'
import { StatusBadge } from './StatusBadge'

const integer = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

// Durations are simulated time, matching the flight's own clock.
function formatDuration(seconds: number): string {
  const minutes = Math.max(0, Math.ceil(seconds / 60))
  if (minutes < 60) return `${minutes} min`
  return `${Math.floor(minutes / 60)} h ${minutes % 60} min`
}

function FlightCell({ aircraft: a }: { aircraft: Aircraft }) {
  switch (a.status) {
    case 'on_ground':
      return <span className="muted">Departs in {formatDuration(a.ground_time_remaining_s)}</span>
    case 'landed':
      return <span className="muted">Taxiing in</span>
    default: {
      const progress = a.route_distance_nm > 0 ? a.distance_flown_nm / a.route_distance_nm : 0
      const remaining = a.route_distance_nm - a.distance_flown_nm
      return (
        <span className="flight-progress" title={`${integer.format(remaining)} nm to go`}>
          <span className="progress-bar">
            <span style={{ width: `${progress * 100}%` }} />
          </span>
          {Math.round(progress * 100)}% · {integer.format(remaining)} nm
        </span>
      )
    }
  }
}

function AirportCell({ airport }: { airport: AirportRef | null }) {
  if (!airport) return <span className="muted">—</span>
  return <abbr title={airport.name}>{airport.code}</abbr>
}

export function AircraftTable({ aircraft }: { aircraft: Aircraft[] }) {
  if (aircraft.length === 0) {
    return <p className="muted">No aircraft.</p>
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Callsign</th>
            <th>Type</th>
            <th>Status</th>
            <th>Origin</th>
            <th>Destination</th>
            <th>Flight</th>
            <th className="num">Latitude</th>
            <th className="num">Longitude</th>
            <th className="num">Altitude (ft)</th>
            <th className="num">Speed (kts)</th>
            <th className="num">Heading</th>
          </tr>
        </thead>
        <tbody>
          {aircraft.map((a) => (
            <tr key={a.id}>
              <td className="callsign">{a.callsign}</td>
              <td>{a.aircraft_type}</td>
              <td>
                <StatusBadge status={a.status} />
              </td>
              <td>
                <AirportCell airport={a.origin} />
              </td>
              <td>
                <AirportCell airport={a.destination} />
              </td>
              <td>
                <FlightCell aircraft={a} />
              </td>
              <td className="num">{a.latitude.toFixed(4)}</td>
              <td className="num">{a.longitude.toFixed(4)}</td>
              <td className="num">{integer.format(a.altitude_ft)}</td>
              <td className="num">{integer.format(a.ground_speed_kts)}</td>
              <td className="num">{integer.format(a.heading_deg)}°</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
