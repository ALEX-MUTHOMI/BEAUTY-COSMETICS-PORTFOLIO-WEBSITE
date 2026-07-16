import { isUuid } from './bookingApi'

/** Same-app booking status path only — blocks open redirects from API status_url. */
const BOOKING_STATUS_PATH_RE =
  /^\/booking\/status\/([0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})\/?$/i

/**
 * Resolve a safe in-app status route after checkout.
 * Never trust absolute URLs, protocol-relative hosts, or off-path redirects.
 */
export function resolveSafeBookingStatusPath(
  statusUrl: string | null | undefined,
  bookingPublicId: string,
): string {
  if (!isUuid(bookingPublicId)) {
    return '/services'
  }
  const fallback = `/booking/status/${bookingPublicId}/`
  const candidate = String(statusUrl ?? '').trim()
  if (!candidate) return fallback
  if (/^[a-z][a-z0-9+.-]*:/i.test(candidate)) return fallback
  if (candidate.startsWith('//')) return fallback
  if (candidate.includes('\\')) return fallback
  if (candidate.includes('..')) return fallback

  const match = BOOKING_STATUS_PATH_RE.exec(candidate)
  if (!match) return fallback
  const pathId = match[1]
  if (!pathId || pathId.toLowerCase() !== bookingPublicId.toLowerCase()) return fallback
  return `/booking/status/${bookingPublicId}/`
}
