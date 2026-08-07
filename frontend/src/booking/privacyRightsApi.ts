/**
 * Privacy rights + published data map — thin Django client (ticket id only, no PII echo).
 */
import { bookingApiBase, ensureBookingCsrfToken } from './bookingCsrf'
import { GENERIC_BOOKING_API_ERROR, publicBookingGet, publicBookingPost, safeApiText } from './bookingApi'

export type PrivacyRequestType = 'access' | 'erasure' | 'rectification' | 'objection'

export interface PrivacyRightsTicket {
  ticketId: string
  requestType: string
  status: string
  detail: string
}

export interface PrivacyDataMapField {
  purpose: string
  lawfulBasis: string
  retention: string
}

function parseTicket(payload: unknown): PrivacyRightsTicket | null {
  if (!payload || typeof payload !== 'object') return null
  const row = payload as Record<string, unknown>
  const ticketId = safeApiText(row.ticket_id, 64)
  if (!ticketId) return null
  return {
    ticketId,
    requestType: safeApiText(row.request_type, 32),
    status: safeApiText(row.status, 32),
    detail: safeApiText(row.detail, 240) || 'Your privacy request was accepted and will be reviewed.',
  }
}

function parseDataMap(payload: unknown): Record<string, PrivacyDataMapField> | null {
  if (!payload || typeof payload !== 'object') return null
  const map = (payload as { data_map?: unknown }).data_map
  if (!map || typeof map !== 'object') return null
  const out: Record<string, PrivacyDataMapField> = {}
  for (const [key, value] of Object.entries(map as Record<string, unknown>)) {
    if (!value || typeof value !== 'object') continue
    const row = value as Record<string, unknown>
    out[key] = {
      purpose: safeApiText(row.purpose, 240),
      lawfulBasis: safeApiText(row.lawful_basis, 64),
      retention: safeApiText(row.retention, 240),
    }
  }
  return Object.keys(out).length ? out : null
}

export async function fetchPrivacyDataMap(
  apiBaseUrl: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: Record<string, PrivacyDataMapField> } | { error: string }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingGet(
    base,
    '/api/bookings/privacy/data-map/',
    {},
    parseDataMap,
    options,
  )
  if ('error' in result) return { error: result.error }
  return { data: result.data }
}

export async function submitPrivacyRightsRequest(
  apiBaseUrl: string,
  body: {
    requestType: PrivacyRequestType
    email: string
    phone?: string
    details?: string
  },
  options?: { signal?: AbortSignal },
): Promise<{ data: PrivacyRightsTicket } | { error: string; throttled: boolean }> {
  const base = bookingApiBase(apiBaseUrl)
  const csrfToken = await ensureBookingCsrfToken(apiBaseUrl, { timeoutMs: 10_000 })
  if (!csrfToken) {
    return { error: GENERIC_BOOKING_API_ERROR, throttled: false }
  }
  const result = await publicBookingPost(
    base,
    '/api/bookings/privacy/rights-request/',
    {
      request_type: body.requestType,
      email: body.email.trim(),
      phone: (body.phone || '').trim(),
      details: (body.details || '').trim().slice(0, 500),
    },
    parseTicket,
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { data: result.data }
}
