import { describe, expect, it } from 'vitest'
import { isTerminalBookingStatus, nextStatusPollDelayMs } from './bookingStatusPoll'
import type { BookingStatusSnapshot } from './bookingWriteApi'

const snapshot = (overrides: Partial<BookingStatusSnapshot> = {}): BookingStatusSnapshot => ({
  bookingReference: '11111111-1111-4111-8111-111111111111',
  bookingStatus: 'payment_pending',
  paymentStatus: 'payment_pending',
  nextAction: 'initiate_payment',
  serviceName: 'Soft glam',
  scheduleDate: '2026-07-15',
  scheduleTime: '09:00 AM',
  ...overrides,
})

describe('bookingStatusPoll', () => {
  it('detects terminal booking states', () => {
    expect(isTerminalBookingStatus(snapshot({ bookingStatus: 'confirmed' }))).toBe(true)
    expect(isTerminalBookingStatus(snapshot({ paymentStatus: 'paid' }))).toBe(true)
    expect(isTerminalBookingStatus(snapshot({ nextAction: 'none' }))).toBe(true)
    expect(isTerminalBookingStatus(snapshot())).toBe(false)
  })

  it('backs off polling with bounded exponential delay', () => {
    expect(nextStatusPollDelayMs(1)).toBe(2_000)
    expect(nextStatusPollDelayMs(3)).toBe(8_000)
    expect(nextStatusPollDelayMs(6)).toBe(15_000)
    expect(nextStatusPollDelayMs(2, '30')).toBe(30_000)
  })
})
