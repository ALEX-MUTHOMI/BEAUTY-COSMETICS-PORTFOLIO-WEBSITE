import { describe, expect, it } from 'vitest'
import { BOOKING_SUBMIT_LIMITS, BookingSubmitGovernor } from './bookingSubmitGovernor'

describe('BookingSubmitGovernor', () => {
  it('allows only one in-flight submit at a time', () => {
    const governor = new BookingSubmitGovernor()
    expect(governor.beginSubmit()).toBe(true)
    expect(governor.beginSubmit()).toBe(false)
    governor.finishSubmit()
    expect(governor.beginSubmit()).toBe(true)
  })

  it('caps rapid hold attempts per minute', () => {
    const governor = new BookingSubmitGovernor()
    let now = 1_000
    for (let index = 0; index < BOOKING_SUBMIT_LIMITS.maxHoldAttemptsPerMinute; index += 1) {
      expect(governor.canAttemptHold(now)).toBe(true)
      governor.recordHoldAttempt(now)
      now += BOOKING_SUBMIT_LIMITS.minMsBetweenHoldAttempts
    }
    expect(governor.canAttemptHold(now)).toBe(false)
  })

  it('enters abuse mode when hold TTL is shortened', () => {
    const governor = new BookingSubmitGovernor()
    governor.noteHoldTtlMinutes(BOOKING_SUBMIT_LIMITS.abuseHoldTtlMinutes)
    expect(governor.abuseMode).toBe(true)
  })
})
