import { bookingApiBase } from './bookingCsrf'
import {
  GENERIC_BOOKING_API_ERROR,
  isIsoDate,
  isUuid,
  publicBookingGet,
  publicBookingPost,
  safeApiText,
} from './bookingApi'
import type { BookingCustomerInput } from './bookingCustomer'
import { resolveSafeBookingStatusPath } from './bookingNavigation'
import type { BookingSlot, ResolvedSelection } from './bookingPublicApi'

export interface BookingHoldResult {
  bookingPublicId: string
  status: string
  holdExpiresAt: string
  holdTtlMinutes: number
  nextAction: string
}

export interface BookingCheckoutResult {
  bookingPublicId: string
  checkoutPublicId: string
  statusUrl: string
  statusApiUrl: string
  amount: string
  currency: string
  nextAction: string
}

export interface BookingStatusSnapshot {
  bookingReference: string
  bookingStatus: string
  paymentStatus: string
  nextAction: string
  serviceName: string
  scheduleDate: string
  scheduleTime: string
}

function parseHold(payload: unknown): BookingHoldResult | null {
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

function parseCheckout(payload: unknown): BookingCheckoutResult | null {
  if (!payload || typeof payload !== 'object') return null
  const checkout = (payload as { checkout?: unknown }).checkout
  if (!checkout || typeof checkout !== 'object') return null
  const row = checkout as Record<string, unknown>
  const bookingPublicId = String(row.booking_public_id ?? '')
  const checkoutPublicId = String(row.checkout_public_id ?? '')
  if (!isUuid(bookingPublicId) || !isUuid(checkoutPublicId)) return null
  const statusUrl = resolveSafeBookingStatusPath(String(row.status_url ?? ''), bookingPublicId)
  const statusApiUrl = `/api/bookings/status/${bookingPublicId}/`
  return {
    bookingPublicId,
    checkoutPublicId,
    statusUrl,
    statusApiUrl,
    amount: safeApiText(row.amount, 32),
    currency: safeApiText(row.currency, 8),
    nextAction: safeApiText(row.next_action, 48),
  }
}

function parseStatus(payload: unknown): BookingStatusSnapshot | null {
  if (!payload || typeof payload !== 'object') return null
  const row = payload as Record<string, unknown>
  const bookingReference = String(row.booking_reference ?? '')
  if (!isUuid(bookingReference)) return null
  const schedule = row.schedule
  if (!schedule || typeof schedule !== 'object') return null
  const scheduleRow = schedule as Record<string, unknown>
  const service = row.service
  const serviceRow = service && typeof service === 'object' ? (service as Record<string, unknown>) : {}
  return {
    bookingReference,
    bookingStatus: safeApiText(row.booking_status, 48),
    paymentStatus: safeApiText(row.payment_status, 48),
    nextAction: safeApiText(row.next_action, 48),
    serviceName: safeApiText(serviceRow.name),
    scheduleDate: isIsoDate(String(scheduleRow.date ?? '')) ? String(scheduleRow.date) : '',
    scheduleTime: safeApiText(scheduleRow.start_time_eat, 32),
  }
}

function parsePolicyText(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') return null
  const text = safeApiText((payload as { checkbox_text?: unknown }).checkbox_text, 2_048)
  return text || null
}

function holdBody(
  selection: ResolvedSelection,
  slot: BookingSlot,
  customer: BookingCustomerInput,
  idempotencyKey: string,
  turnstileToken: string,
): Record<string, unknown> {
  const body: Record<string, unknown> = {
    selection_type: selection.selectionType,
    resource_public_id: slot.resourcePublicId,
    starts_at: slot.startsAt,
    idempotency_key: idempotencyKey,
    turnstile_token: turnstileToken,
    customer: {
      full_name: customer.fullName,
      email: customer.email,
      phone: customer.phone,
    },
  }
  if (selection.selectionType === 'full_package') {
    body.full_package_public_id = selection.publicId
  } else {
    body.service_public_id = slot.servicePublicId || selection.publicId
  }
  return body
}

export async function fetchPolicyAcceptanceText(apiBaseUrl: string): Promise<{ data: string } | { error: string }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingGet(base, '/api/bookings/policy-acceptance-text/', {}, parsePolicyText)
  if ('error' in result) return result
  return { data: result.data }
}

export async function createBookingHold(
  apiBaseUrl: string,
  selection: ResolvedSelection,
  slot: BookingSlot,
  customer: BookingCustomerInput,
  idempotencyKey: string,
  csrfToken: string,
  options?: { turnstileToken?: string; signal?: AbortSignal },
): Promise<{ data: BookingHoldResult } | { error: string; throttled: boolean }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingPost(
    base,
    '/api/bookings/holds/',
    holdBody(selection, slot, customer, idempotencyKey, options?.turnstileToken ?? ''),
    parseHold,
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { data: result.data }
}

export async function createBookingCheckout(
  apiBaseUrl: string,
  bookingPublicId: string,
  idempotencyKey: string,
  policyCheckboxText: string,
  csrfToken: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: BookingCheckoutResult } | { error: string; throttled: boolean }> {
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingPost(
    base,
    '/api/bookings/checkout/',
    {
      booking_public_id: bookingPublicId,
      idempotency_key: idempotencyKey,
      policy_acceptance: {
        accepted: true,
        checkbox_text: policyCheckboxText,
        locale: 'en-KE',
        timezone_name: 'Africa/Nairobi',
        country_hint: 'KE',
      },
    },
    parseCheckout,
    { csrfToken, signal: options?.signal },
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.throttled }
  }
  return { data: result.data }
}

export async function fetchBookingStatus(
  apiBaseUrl: string,
  bookingPublicId: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: BookingStatusSnapshot } | { error: string; throttled: boolean }> {
  if (!isUuid(bookingPublicId)) return { error: GENERIC_BOOKING_API_ERROR, throttled: false }
  const base = bookingApiBase(apiBaseUrl)
  const result = await publicBookingGet(
    base,
    `/api/bookings/status/${bookingPublicId}/`,
    {},
    parseStatus,
    options,
  )
  if ('error' in result) {
    return { error: result.error, throttled: result.error.includes('Too many') }
  }
  return { data: result.data, throttled: false }
}
