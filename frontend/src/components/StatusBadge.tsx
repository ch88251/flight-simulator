import type { AircraftStatus } from '../types'

const LABELS: Record<AircraftStatus, string> = {
  on_ground: 'On ground',
  climbing: 'Climbing',
  cruising: 'Cruising',
  descending: 'Descending',
}

export function StatusBadge({ status }: { status: AircraftStatus }) {
  return <span className={`badge badge-${status}`}>{LABELS[status]}</span>
}
