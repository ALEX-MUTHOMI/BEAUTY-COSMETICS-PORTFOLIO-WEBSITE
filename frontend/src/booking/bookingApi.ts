/** Shared helpers for public booking API calls — no user strings in DOM without validation. */

import { stripControlCharsForDisplay } from '../security/textGuards'
import { GENERIC_BOOKING_THROTTLE_ERROR } from './bookingRequestGovernor'

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
  const cleaned = stripControlCharsForDisplay(String(value ?? '').replace(/<[^>]*>/g, ' '))
    .replace(/\s+/g, ' ')
    .trim()
  return cleaned.slice(0, maxLength)
}

export async function publicBookingGet<T>(
  apiBaseUrl: string,
  path: string,
  params: Record<string, string>,
  parse: (payload: unknown) => T | null,
  options?: { signal?: AbortSignal },
): Promise<{ data: T } | { error: string }> {
  const base = trimApiBaseUrl(apiBaseUrl)
  const search = new URLSearchParams(params).toString()
  const url = `${base}${path}${search ? `?${search}` : ''}`

  try {
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
      signal: options?.signal,
    })
    if (response.status === 429) return { error: GENERIC_BOOKING_THROTTLE_ERROR }
    if (!response.ok) return { error: GENERIC_BOOKING_API_ERROR }
    const payload: unknown = await response.json()
    const data = parse(payload)
    if (!data) return { error: GENERIC_BOOKING_API_ERROR }
    return { data }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return { error: GENERIC_BOOKING_API_ERROR }
    }
    return { error: GENERIC_BOOKING_API_ERROR }
  }
}

export type PublicBookingPostResult<T> =
  | { data: T; status: number }
  | { error: string; status: number; throttled: boolean }

export async function publicBookingPost<T>(
  apiBaseUrl: string,
  path: string,
  body: Record<string, unknown>,
  parse: (payload: unknown) => T | null,
  options: { csrfToken: string; signal?: AbortSignal },
): Promise<PublicBookingPostResult<T>> {
  const base = trimApiBaseUrl(apiBaseUrl)
  const url = `${base}${path}`

  try {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': options.csrfToken,
      },
      body: JSON.stringify(body),
      signal: options.signal,
    })
    if (response.status === 429) {
      return { error: GENERIC_BOOKING_THROTTLE_ERROR, status: 429, throttled: true }
    }
    let payload: unknown = null
    try {
      payload = await response.json()
    } catch {
      payload = null
    }
    if (!response.ok) {
      return {
        error: GENERIC_BOOKING_API_ERROR,
        status: response.status,
        throttled: response.status === 429,
      }
    }
    const data = parse(payload)
    if (!data) {
      return { error: GENERIC_BOOKING_API_ERROR, status: response.status, throttled: false }
    }
    return { data, status: response.status }
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return { error: GENERIC_BOOKING_API_ERROR, status: 0, throttled: false }
    }
    return { error: GENERIC_BOOKING_API_ERROR, status: 0, throttled: false }
  }
}
