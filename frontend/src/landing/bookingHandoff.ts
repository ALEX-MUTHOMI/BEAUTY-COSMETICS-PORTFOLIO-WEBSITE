import {
  getPackageBySlug,
  getTreatmentBySlug,
  isPackagePlanSlug,
  isTreatmentSlug,
  packagePlanSlugForName,
  treatmentSlugForName,
  type PackagePlanSlug,
  type TreatmentSlug,
} from './bookingCatalog'
import { isServiceCategoryId, type ServiceCategoryId } from './servicesNavigation'

export type BookingIntentType = 'package' | 'single'

export const BOOK_ROUTE = '/book'
export const BOOK_HANDOFF_STORAGE_KEY = 'shee-book-handoff-v1'

export const BOOKING_INTENT_TYPES = ['package', 'single'] as const

const ISO_DATE_RE = /^\d{4}-\d{2}-\d{2}$/

export interface BookHandoffSelection {
  type: BookingIntentType
  plan?: PackagePlanSlug
  category?: ServiceCategoryId
  treatment?: TreatmentSlug
  date?: string
}

export interface ResolvedBookHandoff {
  type: BookingIntentType
  plan?: PackagePlanSlug
  planName?: string
  category?: ServiceCategoryId
  treatment?: TreatmentSlug
  treatmentName?: string
  date?: string
}

/** Strip URI tricks before allowlist checks — same posture as servicesNavigation. */
export function normalizeBookQueryToken(raw: unknown): string {
  const value = String(raw ?? '').trim()
  if (!value || /[<>"'`]/.test(value)) return ''

  try {
    const decoded = decodeURIComponent(value)
    if (/[\s<>"'`\x00-\x1f\x7f]/.test(decoded)) return ''
    const firstToken = decoded.split(/[?#/\\&]/)[0]?.trim() ?? ''
    if (!firstToken || firstToken.length > 64) return ''
    return /^[a-z0-9-]+$/i.test(firstToken) ? firstToken.toLowerCase() : ''
  } catch {
    return ''
  }
}

export function normalizeBookDate(raw: unknown): string {
  const token = normalizeBookQueryToken(raw)
  if (!token || !ISO_DATE_RE.test(token)) return ''
  const [year, month, day] = token.split('-').map(Number)
  if (!year || !month || !day) return ''
  const probe = new Date(Date.UTC(year, month - 1, day))
  if (
    probe.getUTCFullYear() !== year ||
    probe.getUTCMonth() !== month - 1 ||
    probe.getUTCDate() !== day
  ) {
    return ''
  }
  return token
}

export function isBookingIntentType(value: string): value is BookingIntentType {
  return (BOOKING_INTENT_TYPES as readonly string[]).includes(value)
}

export function parseBookHandoffQuery(
  query: Record<string, unknown>,
): ResolvedBookHandoff | null {
  const typeToken = normalizeBookQueryToken(query.type)
  if (!typeToken || !isBookingIntentType(typeToken)) return null

  const resolved: ResolvedBookHandoff = { type: typeToken }

  if (typeToken === 'package') {
    const plan = normalizeBookQueryToken(query.plan)
    if (!plan || !isPackagePlanSlug(plan)) return null
    resolved.plan = plan
    resolved.planName = getPackageBySlug(plan)?.name
  } else {
    const category = normalizeBookQueryToken(query.category)
    if (!category || !isServiceCategoryId(category)) return null
    resolved.category = category

    const treatment = normalizeBookQueryToken(query.treatment)
    if (treatment) {
      if (!isTreatmentSlug(treatment)) return null
      const entry = getTreatmentBySlug(treatment)
      if (!entry || entry.category !== category) return null
      resolved.treatment = treatment
      resolved.treatmentName = entry.name
    }
  }

  const date = normalizeBookDate(query.date)
  if (date) resolved.date = date

  return resolved
}

export function buildBookQuery(selection: BookHandoffSelection): Record<string, string> {
  const params: Record<string, string> = { type: selection.type }

  if (selection.type === 'package' && selection.plan) {
    params.plan = selection.plan
  }
  if (selection.type === 'single' && selection.category) {
    params.category = selection.category
    if (selection.treatment) params.treatment = selection.treatment
  }
  if (selection.date) params.date = selection.date

  return params
}

export function buildBookHref(selection: BookHandoffSelection): string {
  const params = buildBookQuery(selection)
  const search = new URLSearchParams(params).toString()
  return search ? `${BOOK_ROUTE}?${search}` : BOOK_ROUTE
}

export function bookHrefForPackageName(name: string): string {
  const plan = packagePlanSlugForName(name)
  if (!plan) return BOOK_ROUTE
  return buildBookHref({ type: 'package', plan })
}

export function bookHrefForTreatment(
  categoryId: ServiceCategoryId,
  treatmentName: string | null | undefined,
): string {
  if (!isServiceCategoryId(categoryId)) return BOOK_ROUTE
  if (!treatmentName) {
    return buildBookHref({ type: 'single', category: categoryId })
  }
  const treatment = treatmentSlugForName(treatmentName)
  if (!treatment) return buildBookHref({ type: 'single', category: categoryId })
  const entry = getTreatmentBySlug(treatment)
  if (!entry || entry.category !== categoryId) {
    return buildBookHref({ type: 'single', category: categoryId })
  }
  return buildBookHref({ type: 'single', category: categoryId, treatment })
}

export function persistBookHandoff(selection: ResolvedBookHandoff): void {
  if (!import.meta.client) return
  try {
    sessionStorage.setItem(BOOK_HANDOFF_STORAGE_KEY, JSON.stringify(selection))
  } catch {
    // Quota or privacy mode — handoff still works via URL.
  }
}

export function readPersistedBookHandoff(): ResolvedBookHandoff | null {
  if (!import.meta.client) return null
  try {
    const raw = sessionStorage.getItem(BOOK_HANDOFF_STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Record<string, unknown>
    return parseBookHandoffQuery(parsed)
  } catch {
    return null
  }
}
