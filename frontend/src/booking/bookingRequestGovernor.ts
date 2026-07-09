/**
 * Client-side booking API governor — defense in depth against click/bot exhaustion.
 * Server throttles remain authoritative; this reduces accidental and scripted spam.
 */

export const BOOKING_CLIENT_LIMITS = {
  /** Minimum gap between availability (day tap) fetches. */
  minMsBetweenDaySlotFetches: 450,
  /** Minimum gap between full calendar reloads (resolve + calendar). */
  minMsBetweenCalendarLoads: 2_000,
  /** Hard cap on day-slot fetches per browser session per minute. */
  maxDaySlotFetchesPerMinute: 12,
} as const

export const GENERIC_BOOKING_THROTTLE_ERROR =
  'Too many requests. Please wait a moment and try again.'

export class BookingRequestGovernor {
  private calendarLoadToken = 0
  private lastCalendarLoadAt = 0
  private lastDaySlotFetchAt = 0
  private daySlotFetchTimestamps: number[] = []
  private daySlotAbort: AbortController | null = null

  beginCalendarLoad(now = Date.now()): number {
    if (
      this.lastCalendarLoadAt !== 0 &&
      now - this.lastCalendarLoadAt < BOOKING_CLIENT_LIMITS.minMsBetweenCalendarLoads
    ) {
      return -1
    }
    this.lastCalendarLoadAt = now
    this.calendarLoadToken += 1
    this.daySlotAbort?.abort()
    this.daySlotAbort = null
    return this.calendarLoadToken
  }

  isCalendarLoadStale(token: number): boolean {
    return token !== this.calendarLoadToken
  }

  canFetchDaySlots(now = Date.now()): boolean {
    this.daySlotFetchTimestamps = this.daySlotFetchTimestamps.filter(
      (stamp) => now - stamp < 60_000,
    )
    if (this.daySlotFetchTimestamps.length >= BOOKING_CLIENT_LIMITS.maxDaySlotFetchesPerMinute) {
      return false
    }
    if (now - this.lastDaySlotFetchAt < BOOKING_CLIENT_LIMITS.minMsBetweenDaySlotFetches) {
      return false
    }
    return true
  }

  beginDaySlotFetch(now = Date.now()): AbortSignal {
    this.daySlotAbort?.abort()
    this.daySlotAbort = new AbortController()
    this.lastDaySlotFetchAt = now
    this.daySlotFetchTimestamps.push(now)
    return this.daySlotAbort.signal
  }

  clearDaySlotFetch(): void {
    this.daySlotAbort = null
  }

  reset(): void {
    this.calendarLoadToken += 1
    this.lastCalendarLoadAt = 0
    this.lastDaySlotFetchAt = 0
    this.daySlotFetchTimestamps = []
    this.daySlotAbort?.abort()
    this.daySlotAbort = null
  }
}
