/**
 * Simulates Googlebot-style crawl noise and scripted multi-click bots against
 * client governors. Server throttles remain authoritative; these prove the
 * browser layer cannot be trivially exhausted via UI event loops.
 */
import { describe, expect, it } from 'vitest'
import { BookingRequestGovernor, BOOKING_CLIENT_LIMITS } from './bookingRequestGovernor'
import { BookingSubmitGovernor, BOOKING_SUBMIT_LIMITS } from './bookingSubmitGovernor'
import { createClickGate } from '../staff/botGuard'
import { validateBookingCustomer } from './bookingCustomer'

describe('bot / multi-click abuse — client governors', () => {
  it('blocks calendar reload spam inside the cooldown window', () => {
    const governor = new BookingRequestGovernor()
    expect(governor.beginCalendarLoad(1_000)).toBeGreaterThan(0)
    // Rapid handoff churn / Googlebot query spam
    for (let i = 0; i < 20; i += 1) {
      expect(governor.beginCalendarLoad(1_000 + i * 50)).toBe(-1)
    }
  })

  it('caps day-slot button mashing under the per-minute budget', () => {
    const governor = new BookingRequestGovernor()
    let now = 5_000
    let allowed = 0
    for (let i = 0; i < 40; i += 1) {
      if (governor.canFetchDaySlots(now)) {
        governor.beginDaySlotFetch(now)
        allowed += 1
      }
      now += 100
    }
    expect(allowed).toBeLessThanOrEqual(BOOKING_CLIENT_LIMITS.maxDaySlotFetchesPerMinute)
  })

  it('blocks double-submit hold chains with click gate + in-flight lock', () => {
    const gate = createClickGate(1_200)
    const submit = new BookingSubmitGovernor()
    expect(gate.canRun('hold-checkout', 10_000)).toBe(true)
    expect(submit.beginSubmit()).toBe(true)
    // Second click within cooldown
    expect(gate.canRun('hold-checkout', 10_500)).toBe(false)
    // Concurrent in-flight
    expect(submit.beginSubmit()).toBe(false)
    submit.finishSubmit()
    gate.finish('hold-checkout')
  })

  it('caps scripted hold attempt loops under the client minute budget', () => {
    const submit = new BookingSubmitGovernor()
    let now = 20_000
    let allowed = 0
    for (let i = 0; i < 20; i += 1) {
      if (submit.canAttemptHold(now)) {
        submit.recordHoldAttempt(now)
        allowed += 1
      }
      now += BOOKING_SUBMIT_LIMITS.minMsBetweenHoldAttempts
    }
    expect(allowed).toBe(BOOKING_SUBMIT_LIMITS.maxHoldAttemptsPerMinute)
  })

  it('rejects honeypot-filled bot form posts before any network call', () => {
    expect(
      validateBookingCustomer({
        fullName: 'Bot Name',
        email: 'bot@example.com',
        phone: '0712345678',
        honeypot: 'Acme Corp SEO',
      }),
    ).toBeNull()
  })

  it('rejects XSS / control-char customer names', () => {
    expect(
      validateBookingCustomer({
        fullName: '<script>alert(1)</script>',
        email: 'grace@example.com',
        phone: '0712345678',
        honeypot: '',
      }),
    ).toBeNull()
  })
})
