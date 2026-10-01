import { useEffect, useState } from 'react'
import { fetchAircraft } from '../api'
import type { Aircraft } from '../types'

const POLL_INTERVAL_MS = 2000

interface AircraftState {
  aircraft: Aircraft[]
  error: string | null
  loading: boolean
}

/** Loads the fleet and keeps it fresh by polling the API. */
export function useAircraft(): AircraftState {
  const [state, setState] = useState<AircraftState>({ aircraft: [], error: null, loading: true })

  useEffect(() => {
    const controller = new AbortController()

    const load = async () => {
      try {
        const aircraft = await fetchAircraft(controller.signal)
        setState({ aircraft, error: null, loading: false })
      } catch (err) {
        if (controller.signal.aborted) return
        // Keep showing the last good data alongside the error.
        setState((prev) => ({ ...prev, error: String(err), loading: false }))
      }
    }

    load()
    const timer = setInterval(load, POLL_INTERVAL_MS)
    return () => {
      clearInterval(timer)
      controller.abort()
    }
  }, [])

  return state
}
