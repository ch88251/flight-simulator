import { useEffect, useState } from 'react'
import { fetchAirports } from '../api'
import type { Airport } from '../types'

/** Loads the airports once; they are static reference data. */
export function useAirports(): { airports: Airport[]; error: string | null } {
  const [airports, setAirports] = useState<Airport[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    fetchAirports(controller.signal)
      .then(setAirports)
      .catch((err) => {
        if (!controller.signal.aborted) setError(String(err))
      })
    return () => controller.abort()
  }, [])

  return { airports, error }
}
