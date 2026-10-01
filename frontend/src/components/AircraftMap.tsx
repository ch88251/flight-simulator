import 'leaflet/dist/leaflet.css'

import L from 'leaflet'
import { useMemo } from 'react'
import { CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer, Tooltip } from 'react-leaflet'
import type { Aircraft, AircraftStatus, Airport } from '../types'
import { StatusBadge } from './StatusBadge'

const CONTIGUOUS_US: L.LatLngBoundsExpression = [
  [24.5, -125],
  [49.5, -66.5],
]

const STATUS_COLORS: Record<AircraftStatus, string> = {
  on_ground: '#4b5563',
  climbing: '#1a7f3c',
  cruising: '#1d4ed8',
  descending: '#b45309',
  landed: '#b91c1c',
}

const integer = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

// Icons are cached so markers only get a new DOM element when the
// (rounded) heading or the status actually changes.
const iconCache = new Map<string, L.DivIcon>()

function aircraftIcon(headingDeg: number, status: AircraftStatus): L.DivIcon {
  const heading = Math.round(headingDeg) % 360
  const key = `${heading}:${status}`
  let icon = iconCache.get(key)
  if (!icon) {
    // The plane shape points north; rotate it to the aircraft's heading.
    icon = L.divIcon({
      className: 'aircraft-icon',
      iconSize: [28, 28],
      iconAnchor: [14, 14],
      popupAnchor: [0, -14],
      html: `<svg viewBox="0 0 24 24" width="28" height="28" style="transform: rotate(${heading}deg)">
        <path fill="${STATUS_COLORS[status]}" stroke="#fff" stroke-width="1"
          d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z"/>
      </svg>`,
    })
    iconCache.set(key, icon)
  }
  return icon
}

interface Props {
  aircraft: Aircraft[]
  airports: Airport[]
}

export function AircraftMap({ aircraft, airports }: Props) {
  const airportsById = useMemo(() => new Map(airports.map((a) => [a.id, a])), [airports])

  return (
    <div className="map-wrapper">
      <MapContainer bounds={CONTIGUOUS_US} className="map" scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {airports.map((airport) => (
          <CircleMarker
            key={airport.id}
            center={[airport.latitude, airport.longitude]}
            radius={5}
            pathOptions={{ color: '#1c2330', weight: 1.5, fillColor: '#fff', fillOpacity: 1 }}
          >
            <Tooltip direction="right" offset={[6, 0]} permanent className="airport-label">
              {airport.code}
            </Tooltip>
            <Popup>
              <strong>
                {airport.code} · {airport.name}
              </strong>
              <br />
              {airport.city}
              <br />
              Elevation {integer.format(airport.altitude_ft)} ft
            </Popup>
          </CircleMarker>
        ))}

        {aircraft.map((a) => {
          const origin = airportsById.get(a.origin.id)
          const destination = a.destination && airportsById.get(a.destination.id)
          const airborne = a.status !== 'on_ground'
          return (
            <span key={a.id}>
              {airborne && origin && destination && (
                <Polyline
                  positions={[
                    [origin.latitude, origin.longitude],
                    [destination.latitude, destination.longitude],
                  ]}
                  pathOptions={{ color: STATUS_COLORS[a.status], weight: 2, dashArray: '6 6' }}
                />
              )}
              <Marker
                position={[a.latitude, a.longitude]}
                icon={aircraftIcon(a.heading_deg, a.status)}
                zIndexOffset={1000}
              >
                <Tooltip direction="top" offset={[0, -14]}>
                  {a.callsign}
                </Tooltip>
                <Popup>
                  <div className="aircraft-popup">
                    <strong className="callsign">{a.callsign}</strong> {a.aircraft_type}
                    <br />
                    <StatusBadge status={a.status} />{' '}
                    {a.origin.code} → {a.destination?.code ?? '—'}
                    <br />
                    {integer.format(a.altitude_ft)} ft · {integer.format(a.ground_speed_kts)}{' '}
                    kts · {integer.format(a.heading_deg)}°
                  </div>
                </Popup>
              </Marker>
            </span>
          )
        })}
      </MapContainer>
    </div>
  )
}
