// Great-circle helpers; mirrors backend/app/geo.py.

type LatLng = [number, number]

const toRad = (deg: number) => (deg * Math.PI) / 180
const toDeg = (rad: number) => (rad * 180) / Math.PI

/** `segments + 1` points along the great circle from `from` to `to`. */
export function greatCirclePoints(from: LatLng, to: LatLng, segments = 64): LatLng[] {
  const [phi1, lambda1] = [toRad(from[0]), toRad(from[1])]
  const [phi2, lambda2] = [toRad(to[0]), toRad(to[1])]
  const delta =
    2 *
    Math.asin(
      Math.sqrt(
        Math.sin((phi2 - phi1) / 2) ** 2 +
          Math.cos(phi1) * Math.cos(phi2) * Math.sin((lambda2 - lambda1) / 2) ** 2,
      ),
    )
  if (delta === 0) return [from, to]

  const points: LatLng[] = []
  for (let i = 0; i <= segments; i++) {
    const f = i / segments
    const a = Math.sin((1 - f) * delta) / Math.sin(delta)
    const b = Math.sin(f * delta) / Math.sin(delta)
    const x = a * Math.cos(phi1) * Math.cos(lambda1) + b * Math.cos(phi2) * Math.cos(lambda2)
    const y = a * Math.cos(phi1) * Math.sin(lambda1) + b * Math.cos(phi2) * Math.sin(lambda2)
    const z = a * Math.sin(phi1) + b * Math.sin(phi2)
    points.push([toDeg(Math.atan2(z, Math.hypot(x, y))), toDeg(Math.atan2(y, x))])
  }
  return points
}
