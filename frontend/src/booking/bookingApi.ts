/** Shared helpers for public booking API calls — no user strings in DOM without validation. */

export const GENERIC_BOOKING_API_ERROR = 'Booking information is temporarily unavailable. Please try again.'

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/

export function trimApiBaseUrl(apiBaseUrl: string): string {
  try {
    const parsed = new URL(apiBaseUrl)
    return parsed.origin.replace(/\/$/, '')
  } catch {
    return apiBaseUrl.replace(/\/$/, '')
  }
}

export function isUuid(value: string): boolean {
  return UUID_RE.test(value)
}

export function isIsoDate(value: string): boolean {
  if (!ISO_DATE_RE.test(value)) return false
  const [year, month, day] = value.split('-').map(Number)
  if (!year || !month || !day) return false
  const probe = new Date(Date.UTC(year, month - 1, day))
  return (
    probe.getUTCFullYear() === year &&
    probe.getUTCMonth() === month - 1 &&
    probe.getUTCDate() === day
  )
}

/** Strip tags/control chars from API copy before text display. */
export function safeApiText(value: unknown, maxLength = 128): string {
  const cleaned = String(value ?? '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/[\x00-\x1f\x7f]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  return cleaned.slice(0, maxLength)
}

export async function publicBookingGet<T>(
  apiBaseUrl: string,
  path: string,
  params: Record<string, string>,
  parse: (payload: unknown) => T | null,
): Promise<{ data: T } | { error: string }> {
  const base = trimApiBaseUrl(apiBaseUrl)
  const search = new URLSearchParams(params).toString()
  const url = `${base}${path}${search ? `?${search}` : ''}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return { error: GENERIC_BOOKING_API_ERROR }
    const payload: unknown = await response.json()
    const data = parse(payload)
    if (!data) return { error: GENERIC_BOOKING_API_ERROR }
    return { data }
  } catch {
    return { error: GENERIC_BOOKING_API_ERROR }
  }
}
