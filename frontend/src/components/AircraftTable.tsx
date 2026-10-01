import type { Aircraft, AirportRef } from '../types'
import { StatusBadge } from './StatusBadge'

const integer = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

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
