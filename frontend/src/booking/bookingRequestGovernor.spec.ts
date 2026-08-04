import { describe, expect, it } from 'vitest'
import { BOOKING_CLIENT_LIMITS, BookingRequestGovernor } from './bookingRequestGovernor'

describe('BookingRequestGovernor', () => {
  it('rejects calendar reloads inside the cooldown window', () => {
    const governor = new BookingRequestGovernor()
    const first = governor.beginCalendarLoad(1_000)
    const second = governor.beginCalendarLoad(1_000 + 500)
    expect(first).toBe(1)
    expect(second).toBe(-1)
  })

  it('invalidates stale calendar responses after a newer load starts', () => {
    const governor = new BookingRequestGovernor()
    const first = governor.beginCalendarLoad(1_000)
    const second = governor.beginCalendarLoad(1_000 + BOOKING_CLIENT_LIMITS.minMsBetweenCalendarLoads + 1)
    expect(governor.isCalendarLoadStale(first)).toBe(true)
    expect(governor.isCalendarLoadStale(second)).toBe(false)
  })

  it('caps rapid day-slot fetches per minute', () => {
    const governor = new BookingRequestGovernor()
    let now = 10_000
    for (let index = 0; index < BOOKING_CLIENT_LIMITS.maxDaySlotFetchesPerMinute; index += 1) {
      expect(governor.canFetchDaySlots(now)).toBe(true)
      governor.beginDaySlotFetch(now)
      now += BOOKING_CLIENT_LIMITS.minMsBetweenDaySlotFetches
    }
    expect(governor.canFetchDaySlots(now)).toBe(false)
  })

  it('aborts the previous in-flight day-slot fetch when a new one starts', () => {
    const governor = new BookingRequestGovernor()
    const first = governor.beginDaySlotFetch(1_000)
    const second = governor.beginDaySlotFetch(1_500)
    expect(first.aborted).toBe(true)
    expect(second.aborted).toBe(false)
  })

  it('caps status poll bombardment per minute and concurrency', () => {
    const governor = new BookingRequestGovernor()
    let now = 50_000
    const first = governor.beginStatusFetch(now)
    expect(first).not.toBeNull()
    expect(governor.canFetchStatus(now + 100)).toBe(false)
    governor.finishStatusFetch()
    expect(governor.canFetchStatus(now + 100)).toBe(false)
    expect(governor.canFetchStatus(now + BOOKING_CLIENT_LIMITS.minMsBetweenStatusFetches)).toBe(true)

    now = 100_000
    for (let index = 0; index < BOOKING_CLIENT_LIMITS.maxStatusFetchesPerMinute; index += 1) {
      const signal = governor.beginStatusFetch(now)
      expect(signal).not.toBeNull()
      governor.finishStatusFetch()
      now += BOOKING_CLIENT_LIMITS.minMsBetweenStatusFetches
    }
    expect(governor.beginStatusFetch(now)).toBeNull()
  })
})
