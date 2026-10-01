// Mirrors the backend's Pydantic schemas in backend/app/schemas.py.

export type AircraftStatus = 'on_ground' | 'climbing' | 'cruising' | 'descending' | 'landed'

export interface AirportRef {
  id: number
  code: string
  name: string
}

export interface Aircraft {
  id: number
  callsign: string
  aircraft_type: string
  status: AircraftStatus
  latitude: number
  longitude: number
  altitude_ft: number
  heading_deg: number
  ground_speed_kts: number
  origin: AirportRef
  destination: AirportRef | null
  updated_at: string
}

export interface Airport {
  id: number
  code: string
  name: string
  city: string
  latitude: number
  longitude: number
  altitude_ft: number
}
