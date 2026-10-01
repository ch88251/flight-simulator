import type { Aircraft, Airport } from './types'

async function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal })
  if (!response.ok) {
    throw new Error(`GET ${path} failed: ${response.status} ${response.statusText}`)
  }
  return response.json() as Promise<T>
}

export function fetchAircraft(signal?: AbortSignal): Promise<Aircraft[]> {
  return getJson<Aircraft[]>('/api/aircraft', signal)
}

export function fetchAirports(signal?: AbortSignal): Promise<Airport[]> {
  return getJson<Airport[]>('/api/airports', signal)
}
