/**
 * Returning-client device cookie APIs — never store plaintext email in localStorage.
 */
import { bookingApiBase } from './bookingCsrf'
import {
  GENERIC_BOOKING_API_ERROR,
  isUuid,
  publicBookingGet,
  publicBookingPost,
  safeApiText,
} from './bookingApi'
import type { BookingHoldResult } from './bookingWriteApi'
import type { BookingSlot, ResolvedSelection } from './bookingPublicApi'

export const REMEMBER_DEVICE_CUSTOMER_COPY =
  'Save my details on this device for faster booking next time. Sensitive actions still require verification.'

export interface RememberedProfileSummary {
  displayName: string
  emailRedacted: string
  phoneRedacted: string
}

export interface RememberedDeviceState {
  remembered: boolean
  canUseSavedDetails: boolean
  profileSummary: RememberedProfileSummary | null
}

function parseSummary(raw: unknown): RememberedProfileSummary | null {
  if (!raw || typeof raw !== 'object') return null
  const row = raw as Record<string, unknown>
  const displayName = safeApiText(row.display_name, 80)
  const emailRedacted = safeApiText(row.email_redacted, 80)
  const phoneRedacted = safeApiText(row.phone_redacted, 40)
  if (!displayName && !emailRedacted) return null
  return { displayName, emailRedacted, phoneRedacted }
}

function parseRememberedGet(payload: unknown): RememberedDeviceState | null {
  if (!payload || typeof payload !== 'object') return null
  const row = payload as Record<string, unknown>
  const remembered = row.remembered === true
  if (!remembered) {
    return { remembered: false, canUseSavedDetails: false, profileSummary: null }
  }
  return {
    remembered: true,
    canUseSavedDetails: row.can_use_saved_details === true,
    profileSummary: parseSummary(row.profile_summary),
  }
}

function parseHoldEnvelope(payload: unknown): BookingHoldResult | null {
  if (!payload || typeof payload !== 'object') return null
  const booking = (payload as { booking?: unknown }).booking
  if (!booking || typeof booking !== 'object') return null
  const row = booking as Record<string, unknown>
  const bookingPublicId = String(row.booking_public_id ?? '')
  if (!isUuid(bookingPublicId)) return null
  const holdTtlMinutes = Number(row.hold_ttl_minutes)
  if (!Number.isFinite(holdTtlMinutes)) return null
  return {
    bookingPublicId,
    status: safeApiText(row.status, 32),
    holdExpiresAt: String(row.hold_expires_at ?? ''),
    holdTtlMinutes,
    nextAction: safeApiText(row.next_action, 48),
  }
}

export async function fetchRememberedDevice(
  apiBaseUrl: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: RememberedDeviceState } | { error: string }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingGet(
    base,
    '/api/customers/remembered-device/',
    {},
    parseRememberedGet,
    options,
  )
  if ('error' in result) return { error: result.error }
  return { data: result.data }
}

export async function optInRememberDevice(
  apiBaseUrl: string,
  bookingPublicId: string,
  csrfToken: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: RememberedProfileSummary | null } | { error: string; throttled: boolean }> {
  if (!isUuid(bookingPublicId)) {
    return { error: GENERIC_BOOKING_API_ERROR, throttled: false }
  }
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingPost(
    base,
    '/api/customers/remember-device/',
    { booking_public_id: bookingPublicId, remember_device: true },
    (payload) => {
      if (!payload || typeof payload !== 'object') return null
      if ((payload as { remembered?: unknown }).remembered !== true) return null
      return parseSummary((payload as { profile_summary?: unknown }).profile_summary)
    },
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { data: result.data }
}

export async function forgetRememberedDevice(
  apiBaseUrl: string,
  csrfToken: string,
  options?: { signal?: AbortSignal },
): Promise<{ ok: true } | { error: string; throttled: boolean }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingPost(
    base,
    '/api/customers/remembered-device/forget/',
    {},
    (payload) => {
      if (!payload || typeof payload !== 'object') return null
      return (payload as { forgotten?: unknown }).forgotten === true ? true : null
    },
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { ok: true }
}

export async function createHoldFromRememberedDevice(
  apiBaseUrl: string,
  selection: ResolvedSelection,
  slot: BookingSlot,
  idempotencyKey: string,
  csrfToken: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: BookingHoldResult } | { error: string; throttled: boolean }> {
  const base = bookingApiBase(apiBaseUrl)
  const body: Record<string, unknown> = {
    resource_public_id: slot.resourcePublicId,
    starts_at: slot.startsAt,
    idempotency_key: idempotencyKey,
  }
  if (selection.selectionType === 'full_package') {
    body.full_package_public_id = selection.publicId
  } else {
    body.service_public_id = slot.servicePublicId || selection.publicId
  }
  const result = await publicBookingPost(
    base,
    '/api/customers/remembered-device/use/',
    body,
    parseHoldEnvelope,
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { data: result.data }
}
