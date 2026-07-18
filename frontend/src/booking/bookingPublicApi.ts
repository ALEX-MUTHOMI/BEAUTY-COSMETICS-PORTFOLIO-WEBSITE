import { GENERIC_BOOKING_API_ERROR, isIsoDate, isUuid, publicBookingGet, safeApiText } from './bookingApi'

export type CalendarDayStatus =
  | 'available'
  | 'capacity_full'
  | 'no_slots'
  | 'not_offered'
  | 'closed'

export interface CalendarCapacity {
  max: number
  booked: number
  remaining: number
}

export interface CalendarDay {
  date: string
  weekday: number
  day_type: string
  status: CalendarDayStatus
  reason_code: string | null
  slot_count: number
  capacity: CalendarCapacity
}

export interface ResolvedSelection {
  selectionType: 'normal' | 'full_package'
  publicId: string
  slug: string
  name: string
  durationMinutes: number
}

export interface CalendarWeek {
  week_start: string
  days: CalendarDay[]
}

export interface BookingCalendar {
  timezone: string
  layout: 'singles' | 'package_pairs'
  range: { start: string; end: string }
  selection: {
    type: 'normal' | 'full_package'
    public_id: string
    slug: string
    name: string
  }
  days: CalendarDay[]
  weeks: CalendarWeek[]
}

export interface BookingSlot {
  startsAt: string
  endsAt: string
  durationMinutes: number
  bufferMinutes: number
  resourcePublicId: string
  servicePublicId: string
}

const CALENDAR_STATUSES = new Set([
  'available',
  'capacity_full',
  'no_slots',
  'not_offered',
  'closed',
])

function parseSelection(payload: unknown): ResolvedSelection | null {
  if (!payload || typeof payload !== 'object') return null
  const row = (payload as { selection?: unknown }).selection
  if (!row || typeof row !== 'object') return null
  const data = row as Record<string, unknown>
  const selectionType = String(data.selection_type ?? '')
  const publicId = String(data.public_id ?? '')
  if (!isUuid(publicId)) return null
  if (selectionType !== 'normal' && selectionType !== 'full_package') return null
  const durationMinutes = Number(data.duration_minutes)
  if (!Number.isFinite(durationMinutes) || durationMinutes <= 0) return null
  return {
    selectionType,
    publicId,
    slug: safeApiText(data.slug, 140),
    name: safeApiText(data.name),
    durationMinutes,
  }
}

function parseCalendarDay(value: unknown): CalendarDay | null {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>
  const date = String(row.date ?? '')
  if (!isIsoDate(date)) return null
  const status = String(row.status ?? '')
  if (!CALENDAR_STATUSES.has(status)) return null
  const capacityRow = row.capacity
  if (!capacityRow || typeof capacityRow !== 'object') return null
  const capacity = capacityRow as Record<string, unknown>
  return {
    date,
    weekday: Number(row.weekday),
    day_type: safeApiText(row.day_type, 32),
    status: status as CalendarDayStatus,
    reason_code: row.reason_code ? safeApiText(row.reason_code, 64) : null,
    slot_count: Number(row.slot_count) || 0,
    capacity: {
      max: Number(capacity.max) || 0,
      booked: Number(capacity.booked) || 0,
      remaining: Number(capacity.remaining) || 0,
    },
  }
}

function parseCalendar(payload: unknown): BookingCalendar | null {
  if (!payload || typeof payload !== 'object') return null
  const calendar = (payload as { calendar?: unknown }).calendar
  if (!calendar || typeof calendar !== 'object') return null
  const row = calendar as Record<string, unknown>
  const range = row.range
  if (!range || typeof range !== 'object') return null
  const rangeData = range as Record<string, unknown>
  const start = String(rangeData.start ?? '')
  const end = String(rangeData.end ?? '')
  if (!isIsoDate(start) || !isIsoDate(end)) return null
  if (!Array.isArray(row.days)) return null
  const days = row.days.map(parseCalendarDay).filter((day): day is CalendarDay => day !== null)
  if (days.length !== row.days.length) return null
  const layout = String(row.layout ?? '')
  if (layout !== 'singles' && layout !== 'package_pairs') return null
  if (!Array.isArray(row.weeks)) return null
  const weeks: CalendarWeek[] = []
  for (const week of row.weeks) {
    if (!week || typeof week !== 'object') return null
    const weekRow = week as Record<string, unknown>
    const weekStart = String(weekRow.week_start ?? '')
    if (!isIsoDate(weekStart) || !Array.isArray(weekRow.days)) return null
    const weekDays = weekRow.days.map(parseCalendarDay).filter((day): day is CalendarDay => day !== null)
    if (weekDays.length !== weekRow.days.length) return null
    weeks.push({ week_start: weekStart, days: weekDays })
  }
  const selection = row.selection
  if (!selection || typeof selection !== 'object') return null
  const sel = selection as Record<string, unknown>
  const type = String(sel.type ?? '')
  const publicId = String(sel.public_id ?? '')
  if (!isUuid(publicId) || (type !== 'normal' && type !== 'full_package')) return null
  return {
    timezone: safeApiText(row.timezone, 64),
    layout,
    range: { start, end },
    selection: {
      type,
      public_id: publicId,
      slug: safeApiText(sel.slug, 140),
      name: safeApiText(sel.name),
    },
    days,
    weeks,
  }
}

function parseSlot(value: unknown): BookingSlot | null {
  if (!value || typeof value !== 'object') return null
  const row = value as Record<string, unknown>
  const startsAt = String(row.starts_at ?? '')
  const endsAt = String(row.ends_at ?? '')
  const resourcePublicId = String(row.resource_public_id ?? '')
  const servicePublicId = String(row.service_public_id ?? '')
  if (!startsAt || !endsAt || !isUuid(resourcePublicId) || !isUuid(servicePublicId)) return null
  return {
    startsAt,
    endsAt,
    durationMinutes: Number(row.duration_minutes) || 0,
    bufferMinutes: Number(row.buffer_minutes) || 0,
    resourcePublicId,
    servicePublicId,
  }
}

function parseAvailability(payload: unknown): BookingSlot[] | null {
  if (!payload || typeof payload !== 'object') return null
  const days = (payload as { availability?: unknown }).availability
  if (!Array.isArray(days) || days.length !== 1) return null
  const day = days[0]
  if (!day || typeof day !== 'object') return null
  const slots = (day as { slots?: unknown }).slots
  if (!Array.isArray(slots)) return null
  const parsed = slots.map(parseSlot).filter((slot): slot is BookingSlot => slot !== null)
  return parsed.length === slots.length ? parsed : null
}

export async function resolveHandoff(
  apiBaseUrl: string,
  params: { type: string; plan?: string; category?: string; treatment?: string },
): Promise<{ data: ResolvedSelection } | { error: string }> {
  const query: Record<string, string> = { type: params.type }
  if (params.plan) query.plan = params.plan
  if (params.category) query.category = params.category
  if (params.treatment) query.treatment = params.treatment
  const result = await publicBookingGet(apiBaseUrl, '/api/bookings/catalog/resolve-handoff/', query, parseSelection)
  if ('error' in result) return result
  return { data: result.data }
}

export async function fetchCalendar(
  apiBaseUrl: string,
  selection: ResolvedSelection,
): Promise<{ data: BookingCalendar } | { error: string }> {
  const params: Record<string, string> = {
    selection_type: selection.selectionType,
  }
  if (selection.selectionType === 'full_package') {
    params.full_package_public_id = selection.publicId
  } else {
    params.service_public_id = selection.publicId
  }
  const result = await publicBookingGet(apiBaseUrl, '/api/bookings/calendar/', params, parseCalendar)
  if ('error' in result) return result
  return { data: result.data }
}

export async function fetchDaySlots(
  apiBaseUrl: string,
  selection: ResolvedSelection,
  isoDate: string,
  options?: { signal?: AbortSignal },
): Promise<{ data: BookingSlot[] } | { error: string }> {
  if (!isIsoDate(isoDate)) return { error: GENERIC_BOOKING_API_ERROR }
  const params: Record<string, string> = {
    selection_type: selection.selectionType,
    start_date: isoDate,
    end_date: isoDate,
  }
  if (selection.selectionType === 'full_package') {
    params.full_package_public_id = selection.publicId
  } else {
    params.service_public_id = selection.publicId
  }
  const result = await publicBookingGet(
    apiBaseUrl,
    '/api/bookings/availability/',
    params,
    parseAvailability,
    options,
  )
  if ('error' in result) return result
  return { data: result.data }
}

export function formatSlotLabel(startsAt: string): string {
  try {
    return new Intl.DateTimeFormat('en-KE', {
      timeZone: 'Africa/Nairobi',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    }).format(new Date(startsAt))
  } catch {
    return ''
  }
}

/** Nairobi hour band label for hour-view grouping (e.g. "7 AM"). */
export function formatSlotHourBand(startsAt: string): string {
  try {
    return new Intl.DateTimeFormat('en-KE', {
      timeZone: 'Africa/Nairobi',
      hour: 'numeric',
      hour12: true,
    }).format(new Date(startsAt))
  } catch {
    return ''
  }
}

/** Start–end range from backend slot fields — never invent times. */
export function formatSlotRange(startsAt: string, endsAt: string): string {
  const start = formatSlotLabel(startsAt)
  const end = formatSlotLabel(endsAt)
  if (!start) return ''
  if (!end) return start
  return `${start} – ${end}`
}

export function isSameBookingSlot(a: BookingSlot | null, b: BookingSlot | null): boolean {
  if (!a || !b) return false
  return a.startsAt === b.startsAt && a.resourcePublicId === b.resourcePublicId
}

export function dayStatusLabel(day: CalendarDay): string {
  if (day.status === 'available') {
    return day.slot_count === 1 ? '1 slot' : `${day.slot_count} slots`
  }
  if (day.status === 'capacity_full') return 'Full'
  if (day.status === 'no_slots') return 'No times'
  if (day.status === 'closed') return 'Closed'
  return '—'
}

export function isDaySelectable(day: CalendarDay): boolean {
  return day.status === 'available'
}
