import { describe, expect, it } from 'vitest'
import {
  dayStatusLabel,
  isDaySelectable,
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
})
