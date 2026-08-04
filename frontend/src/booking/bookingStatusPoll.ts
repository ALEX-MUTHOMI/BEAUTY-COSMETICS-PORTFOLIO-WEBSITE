import { retryAfterDelayMs } from '../payment/checkoutResilience'
import { BookingRequestGovernor, GENERIC_BOOKING_THROTTLE_ERROR } from './bookingRequestGovernor'
import { fetchBookingStatus, type BookingStatusSnapshot } from './bookingWriteApi'

export const BOOKING_STATUS_POLL = {
  initialDelayMs: 2_000,
  maxDelayMs: 15_000,
  maxWaitMs: 120_000,
} as const

const TERMINAL_STATUSES = new Set(['confirmed', 'cancelled', 'expired', 'failed'])

/** Shared governor so navigation remounts cannot open parallel status bombardments. */
const statusGovernor = new BookingRequestGovernor()

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
  const externalSignal = handlers.signal

  const onExternalAbort = () => {
    statusGovernor.abortStatusFetch()
  }
  externalSignal?.addEventListener('abort', onExternalAbort, { once: true })

  try {
    while (Date.now() - startedAt < BOOKING_STATUS_POLL.maxWaitMs) {
      if (externalSignal?.aborted) return null

      const governed = statusGovernor.beginStatusFetch()
      if (!governed) {
        // Client cushion — wait out the governor window instead of hammering the API.
        await sleep(BOOKING_STATUS_POLL.initialDelayMs, externalSignal)
        continue
      }

      const linked = linkSignals(governed, externalSignal)
      try {
        const result = await fetchBookingStatus(apiBaseUrl, bookingPublicId, { signal: linked })
        if ('data' in result) {
          handlers.onUpdate(result.data)
          if (isTerminalBookingStatus(result.data)) {
            return result.data
          }
        } else if (result.error === GENERIC_BOOKING_THROTTLE_ERROR) {
          await sleep(BOOKING_STATUS_POLL.maxDelayMs, externalSignal)
        }
      } finally {
        statusGovernor.finishStatusFetch()
      }

      attempt += 1
      const delay = nextStatusPollDelayMs(attempt)
      await sleep(delay, externalSignal)
    }

    return null
  } finally {
    externalSignal?.removeEventListener('abort', onExternalAbort)
    statusGovernor.abortStatusFetch()
  }
}

function linkSignals(governed: AbortSignal, external?: AbortSignal): AbortSignal {
  if (!external) return governed
  const controller = new AbortController()
  const abort = () => controller.abort()
  if (governed.aborted || external.aborted) {
    controller.abort()
    return controller.signal
  }
  governed.addEventListener('abort', abort, { once: true })
  external.addEventListener('abort', abort, { once: true })
  return controller.signal
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
