import { describe, expect, it } from 'vitest'
import {
  dayStatusLabel,
  formatSlotHourBand,
  formatSlotRange,
  isDaySelectable,
  isSameBookingSlot,
  type BookingSlot,
  type CalendarDay,
} from './bookingPublicApi'

const sampleDay: CalendarDay = {
  date: '2026-07-07',
  weekday: 1,
  day_type: 'full_package',
  status: 'available',
  reason_code: null,
  slot_count: 4,
  capacity: { max: 3, booked: 1, remaining: 2 },
}

const sampleSlot: BookingSlot = {
  startsAt: '2026-07-06T04:00:00+00:00',
  endsAt: '2026-07-06T05:00:00+00:00',
  durationMinutes: 60,
  bufferMinutes: 0,
  resourcePublicId: 'res-1',
  servicePublicId: 'svc-1',
}

describe('bookingPublicApi presentation helpers', () => {
  it('only allows selecting server-marked available days', () => {
    expect(isDaySelectable(sampleDay)).toBe(true)
    expect(isDaySelectable({ ...sampleDay, status: 'capacity_full' })).toBe(false)
    expect(isDaySelectable({ ...sampleDay, status: 'not_offered' })).toBe(false)
  })

  it('formats status labels without embedding raw API strings', () => {
    expect(dayStatusLabel(sampleDay)).toBe('4 slots')
    expect(dayStatusLabel({ ...sampleDay, status: 'capacity_full' })).toBe('Full')
  })

  it('formats Nairobi hour bands and start–end ranges from backend timestamps', () => {
    expect(formatSlotHourBand(sampleSlot.startsAt)).toMatch(/7/)
    expect(formatSlotRange(sampleSlot.startsAt, sampleSlot.endsAt)).toMatch(/–/)
  })

  it('compares slots by start and resource', () => {
    expect(isSameBookingSlot(sampleSlot, { ...sampleSlot })).toBe(true)
    expect(isSameBookingSlot(sampleSlot, { ...sampleSlot, resourcePublicId: 'other' })).toBe(false)
  })
})
