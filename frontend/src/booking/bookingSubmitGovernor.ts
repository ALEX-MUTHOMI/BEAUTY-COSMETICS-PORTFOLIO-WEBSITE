/**
 * Submit-phase governor — hold/checkout click and bot exhaustion controls.
 * Complements BookingRequestGovernor (read path) per OWASP API abuse patterns.
 */

export const BOOKING_SUBMIT_LIMITS = {
  minMsBetweenHoldAttempts: 2_000,
  maxHoldAttemptsPerMinute: 3,
  minMsBetweenCheckoutAttempts: 2_000,
  maxCheckoutAttemptsPerMinute: 2,
  abuseHoldTtlMinutes: 3,
} as const

export const GENERIC_BOOKING_SUBMIT_ERROR =
  'We could not complete your booking. Please check your details and try again.'

export class BookingSubmitGovernor {
  private holdTimestamps: number[] = []
  private checkoutTimestamps: number[] = []
  private lastHoldAt = 0
  private lastCheckoutAt = 0
  private abuseSuspected = false
  private inFlight = false

  get isInFlight(): boolean {
    return this.inFlight
  }

  get abuseMode(): boolean {
    return this.abuseSuspected
  }

  markAbuseSuspected(): void {
    this.abuseSuspected = true
  }

  noteHoldTtlMinutes(ttl: number): void {
    if (ttl <= BOOKING_SUBMIT_LIMITS.abuseHoldTtlMinutes) {
      this.abuseSuspected = true
    }
  }

  beginSubmit(): boolean {
    if (this.inFlight) return false
    this.inFlight = true
    return true
  }

  finishSubmit(): void {
    this.inFlight = false
  }

  canAttemptHold(now = Date.now()): boolean {
    // Concurrency is guarded by beginSubmit(); this method runs inside an active
    // submit (inFlight === true), so it must only enforce rate/volume limits.
    this.holdTimestamps = this.holdTimestamps.filter((stamp) => now - stamp < 60_000)
    if (this.holdTimestamps.length >= BOOKING_SUBMIT_LIMITS.maxHoldAttemptsPerMinute) return false
    if (this.lastHoldAt !== 0 && now - this.lastHoldAt < BOOKING_SUBMIT_LIMITS.minMsBetweenHoldAttempts) {
      return false
    }
    return true
  }

  recordHoldAttempt(now = Date.now()): void {
    this.lastHoldAt = now
    this.holdTimestamps.push(now)
  }

  canAttemptCheckout(now = Date.now()): boolean {
    // Runs inside an active submit (inFlight === true) after a successful hold;
    // beginSubmit() owns concurrency, so only enforce rate/volume limits here.
    this.checkoutTimestamps = this.checkoutTimestamps.filter((stamp) => now - stamp < 60_000)
    if (this.checkoutTimestamps.length >= BOOKING_SUBMIT_LIMITS.maxCheckoutAttemptsPerMinute) return false
    if (
      this.lastCheckoutAt !== 0 &&
      now - this.lastCheckoutAt < BOOKING_SUBMIT_LIMITS.minMsBetweenCheckoutAttempts
    ) {
      return false
    }
    return true
  }

  recordCheckoutAttempt(now = Date.now()): void {
    this.lastCheckoutAt = now
    this.checkoutTimestamps.push(now)
  }

  reset(): void {
    this.holdTimestamps = []
    this.checkoutTimestamps = []
    this.lastHoldAt = 0
    this.lastCheckoutAt = 0
    this.abuseSuspected = false
    this.inFlight = false
  }
}
