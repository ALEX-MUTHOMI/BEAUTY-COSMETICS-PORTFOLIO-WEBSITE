import { describe, expect, it } from 'vitest'
import type { CalendarDay, CalendarWeek } from './bookingPublicApi'
import {
  CALENDAR_STRIP_COLLAPSED_COUNT,
  flattenCalendarDays,
  stripHasMore,
  visibleStripDays,
} from './calendarStrip'

function day(date: string, weekday = 1): CalendarDay {
  return {
    date,
    weekday,
    day_type: 'single',
    status: 'available',
    reason_code: null,
    slot_count: 3,
    capacity: { max: 5, booked: 0, remaining: 5 },
  }
}

describe('calendarStrip', () => {
  it('flattens weeks in offered order', () => {
    const weeks: CalendarWeek[] = [
      { week_start: '2026-07-13', days: [day('2026-07-14'), day('2026-07-16')] },
      { week_start: '2026-07-20', days: [day('2026-07-21')] },
    ]
    expect(flattenCalendarDays([], weeks).map((d) => d.date)).toEqual([
      '2026-07-14',
      '2026-07-16',
      '2026-07-21',
    ])
  })

  it('falls back to days when weeks are empty', () => {
    const days = [day('2026-07-14'), day('2026-07-15')]
    expect(flattenCalendarDays(days, []).map((d) => d.date)).toEqual([
      '2026-07-14',
      '2026-07-15',
    ])
  })

  it('shows at most collapsed count when not expanded', () => {
    const days = Array.from({ length: 8 }, (_, i) => day(`2026-07-${14 + i}`))
    const visible = visibleStripDays(days, false)
    expect(visible).toHaveLength(CALENDAR_STRIP_COLLAPSED_COUNT)
    expect(visible.map((d) => d.date)).toEqual([
      '2026-07-14',
      '2026-07-15',
      '2026-07-16',
      '2026-07-17',
    ])
  })

  it('shows all days when expanded or already short', () => {
    const days = Array.from({ length: 8 }, (_, i) => day(`2026-07-${14 + i}`))
    expect(visibleStripDays(days, true)).toHaveLength(8)

    const short = days.slice(0, 3)
    expect(visibleStripDays(short, false)).toHaveLength(3)
    expect(stripHasMore(short)).toBe(false)
  })

  it('reports more dates only when beyond collapsed count', () => {
    const days = Array.from({ length: 8 }, (_, i) => day(`2026-07-${14 + i}`))
    expect(stripHasMore(days)).toBe(true)
    expect(stripHasMore(days.slice(0, CALENDAR_STRIP_COLLAPSED_COUNT))).toBe(false)
  })
})
