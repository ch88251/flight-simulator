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
  cruise_speed_kts: number
  cruise_altitude_ft: number
  route_distance_nm: number
  distance_flown_nm: number
  /** Simulated seconds until departure (on_ground) or end of taxi-in (landed). */
  ground_time_remaining_s: number
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
