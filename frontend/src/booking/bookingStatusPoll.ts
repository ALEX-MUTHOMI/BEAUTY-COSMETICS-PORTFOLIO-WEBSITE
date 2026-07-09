import { retryAfterDelayMs } from '../payment/checkoutResilience'
import { fetchBookingStatus, type BookingStatusSnapshot } from './bookingWriteApi'

export const BOOKING_STATUS_POLL = {
  initialDelayMs: 2_000,
  maxDelayMs: 15_000,
  maxWaitMs: 120_000,
} as const

const TERMINAL_STATUSES = new Set(['confirmed', 'cancelled', 'expired', 'failed'])

export function isTerminalBookingStatus(snapshot: BookingStatusSnapshot): boolean {
  if (TERMINAL_STATUSES.has(snapshot.bookingStatus)) return true
  if (snapshot.paymentStatus === 'paid') return true
  if (snapshot.paymentStatus === 'failed') return true
  if (snapshot.nextAction === 'none') return true
  return false
}

export function nextStatusPollDelayMs(attempt: number, retryAfterHeader: string | null = null): number {
  const exponential = Math.min(
    BOOKING_STATUS_POLL.maxDelayMs,
    BOOKING_STATUS_POLL.initialDelayMs * 2 ** Math.max(0, attempt - 1),
  )
  const retryAfter = retryAfterDelayMs(retryAfterHeader, {
    maxWaitMs: BOOKING_STATUS_POLL.maxWaitMs,
    pollIntervalMs: exponential,
  })
  return Math.max(exponential, retryAfter)
}

export async function pollBookingStatusUntilSettled(
  apiBaseUrl: string,
  bookingPublicId: string,
  handlers: {
    onUpdate: (snapshot: BookingStatusSnapshot) => void
    signal?: AbortSignal
  },
): Promise<BookingStatusSnapshot | null> {
  const startedAt = Date.now()
  let attempt = 0

  while (Date.now() - startedAt < BOOKING_STATUS_POLL.maxWaitMs) {
    if (handlers.signal?.aborted) return null

    const result = await fetchBookingStatus(apiBaseUrl, bookingPublicId, { signal: handlers.signal })
    if ('data' in result) {
      handlers.onUpdate(result.data)
      if (isTerminalBookingStatus(result.data)) {
        return result.data
      }
    }

    attempt += 1
    const delay = nextStatusPollDelayMs(attempt)
    await sleep(delay, handlers.signal)
  }

  return null
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    if (signal?.aborted) {
      resolve()
      return
    }
    const timer = window.setTimeout(resolve, ms)
    signal?.addEventListener(
      'abort',
      () => {
        window.clearTimeout(timer)
        resolve()
      },
      { once: true },
    )
  })
}
