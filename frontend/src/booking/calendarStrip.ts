import type { CalendarDay, CalendarWeek } from './bookingPublicApi'

/** Default number of offered days shown before "Show more". */
export const CALENDAR_STRIP_COLLAPSED_COUNT = 4

/** Flatten week buckets into a single ordered day list (API order preserved). */
export function flattenCalendarDays(
  days: CalendarDay[],
  weeks?: CalendarWeek[],
): CalendarDay[] {
  if (weeks?.length) {
    return weeks.flatMap((week) => week.days)
  }
  return days
}

/**
 * Visible slice for the compact date strip.
 * Collapsed: first N days in offered order. Expanded: all.
 */
export function visibleStripDays(
  days: CalendarDay[],
  expanded: boolean,
  collapsedCount: number = CALENDAR_STRIP_COLLAPSED_COUNT,
): CalendarDay[] {
  if (expanded || days.length <= collapsedCount) return days
  return days.slice(0, collapsedCount)
}

export function stripHasMore(
  days: CalendarDay[],
  collapsedCount: number = CALENDAR_STRIP_COLLAPSED_COUNT,
): boolean {
  return days.length > collapsedCount
}
