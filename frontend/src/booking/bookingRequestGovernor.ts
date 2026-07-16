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
  /** Minimum gap between booking status polls (anti-bombardment). */
  minMsBetweenStatusFetches: 1_500,
  /** Hard cap on status GETs per minute — server throttle remains authoritative. */
  maxStatusFetchesPerMinute: 20,
  /** At most one in-flight status poll per tab. */
  maxConcurrentStatusPolls: 1,
} as const

export const GENERIC_BOOKING_THROTTLE_ERROR =
  'Please wait a moment and try again.'

export class BookingRequestGovernor {
  private calendarLoadToken = 0
  private lastCalendarLoadAt = 0
  private lastDaySlotFetchAt = 0
  private daySlotFetchTimestamps: number[] = []
  private daySlotAbort: AbortController | null = null
  private lastStatusFetchAt = 0
  private statusFetchTimestamps: number[] = []
  private statusInFlight = 0
  private statusAbort: AbortController | null = null

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

  canFetchStatus(now = Date.now()): boolean {
    this.statusFetchTimestamps = this.statusFetchTimestamps.filter((stamp) => now - stamp < 60_000)
    if (this.statusInFlight >= BOOKING_CLIENT_LIMITS.maxConcurrentStatusPolls) {
      return false
    }
    if (this.statusFetchTimestamps.length >= BOOKING_CLIENT_LIMITS.maxStatusFetchesPerMinute) {
      return false
    }
    if (
      this.lastStatusFetchAt !== 0 &&
      now - this.lastStatusFetchAt < BOOKING_CLIENT_LIMITS.minMsBetweenStatusFetches
    ) {
      return false
    }
    return true
  }

  beginStatusFetch(now = Date.now()): AbortSignal | null {
    if (!this.canFetchStatus(now)) return null
    this.statusAbort?.abort()
    this.statusAbort = new AbortController()
    this.lastStatusFetchAt = now
    this.statusFetchTimestamps.push(now)
    this.statusInFlight = 1
    return this.statusAbort.signal
  }

  finishStatusFetch(): void {
    this.statusInFlight = 0
  }

  abortStatusFetch(): void {
    this.statusAbort?.abort()
    this.statusAbort = null
    this.statusInFlight = 0
  }

  reset(): void {
    this.calendarLoadToken += 1
    this.lastCalendarLoadAt = 0
    this.lastDaySlotFetchAt = 0
    this.daySlotFetchTimestamps = []
    this.daySlotAbort?.abort()
    this.daySlotAbort = null
    this.lastStatusFetchAt = 0
    this.statusFetchTimestamps = []
    this.abortStatusFetch()
  }
}
