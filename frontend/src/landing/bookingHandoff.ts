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
import { containsUnsafeDecodedToken } from '../security/textGuards'
import {
  isServiceCategoryId,
  SERVICES_ROUTES,
  type ServiceCategoryId,
} from './servicesNavigation'

export type BookingIntentType = 'package' | 'single'

export const BOOK_ROUTE = '/book'
export const SERVICES_BOOK_ENTRY = SERVICES_ROUTES.page
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
    if (containsUnsafeDecodedToken(decoded)) return ''
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
    // Category-only is not bookable — require an allowlisted treatment.
    if (!treatment || !isTreatmentSlug(treatment)) return null
    const entry = getTreatmentBySlug(treatment)
    if (!entry || entry.category !== category) return null
    resolved.treatment = treatment
    resolved.treatmentName = entry.name
  }

  const date = normalizeBookDate(query.date)
  if (date) resolved.date = date

  return resolved
}

/** Fail-closed parse of clean SEO path segments. */
export function parseBookPathParams(params: {
  plan?: unknown
  category?: unknown
  treatment?: unknown
  date?: unknown
}): ResolvedBookHandoff | null {
  const plan = normalizeBookQueryToken(params.plan)
  if (plan) {
    if (!isPackagePlanSlug(plan)) return null
    const resolved: ResolvedBookHandoff = {
      type: 'package',
      plan,
      planName: getPackageBySlug(plan)?.name,
    }
    const date = normalizeBookDate(params.date)
    if (date) resolved.date = date
    return resolved
  }

  const category = normalizeBookQueryToken(params.category)
  const treatment = normalizeBookQueryToken(params.treatment)
  if (!category || !treatment) return null
  if (!isServiceCategoryId(category) || !isTreatmentSlug(treatment)) return null
  const entry = getTreatmentBySlug(treatment)
  if (!entry || entry.category !== category) return null

  const resolved: ResolvedBookHandoff = {
    type: 'single',
    category,
    treatment,
    treatmentName: entry.name,
  }
  const date = normalizeBookDate(params.date)
  if (date) resolved.date = date
  return resolved
}

/** Legacy query helpers kept for redirects / API resolve payloads. */
export function buildBookQuery(selection: BookHandoffSelection): Record<string, string> {
  const params: Record<string, string> = { type: selection.type }

  if (selection.type === 'package' && selection.plan) {
    params.plan = selection.plan
  }
  if (selection.type === 'single' && selection.category && selection.treatment) {
    params.category = selection.category
    params.treatment = selection.treatment
  }
  if (selection.date) params.date = selection.date

  return params
}

/** Canonical shareable book URL (clean path). */
export function buildBookHref(selection: BookHandoffSelection): string {
  if (selection.type === 'package' && selection.plan && isPackagePlanSlug(selection.plan)) {
    const base = `${BOOK_ROUTE}/package/${selection.plan}`
    return selection.date ? `${base}?date=${encodeURIComponent(selection.date)}` : base
  }
  if (
    selection.type === 'single' &&
    selection.category &&
    selection.treatment &&
    isServiceCategoryId(selection.category) &&
    isTreatmentSlug(selection.treatment)
  ) {
    const entry = getTreatmentBySlug(selection.treatment)
    if (!entry || entry.category !== selection.category) return SERVICES_BOOK_ENTRY
    const base = `${BOOK_ROUTE}/${selection.category}/${selection.treatment}`
    return selection.date ? `${base}?date=${encodeURIComponent(selection.date)}` : base
  }
  return SERVICES_BOOK_ENTRY
}

export function bookHrefForPackageName(name: string): string {
  const plan = packagePlanSlugForName(name)
  if (!plan) return SERVICES_BOOK_ENTRY
  return buildBookHref({ type: 'package', plan })
}

export function bookHrefForTreatment(
  categoryId: ServiceCategoryId,
  treatmentName: string | null | undefined,
): string {
  if (!isServiceCategoryId(categoryId) || !treatmentName) return SERVICES_BOOK_ENTRY
  const treatment = treatmentSlugForName(treatmentName)
  if (!treatment) return SERVICES_BOOK_ENTRY
  const entry = getTreatmentBySlug(treatment)
  if (!entry || entry.category !== categoryId) return SERVICES_BOOK_ENTRY
  return buildBookHref({ type: 'single', category: categoryId, treatment })
}

/** Map a resolved handoff (or legacy query) to the canonical clean path. */
export function canonicalBookPath(handoff: ResolvedBookHandoff): string {
  return buildBookHref({
    type: handoff.type,
    plan: handoff.plan,
    category: handoff.category,
    treatment: handoff.treatment,
    date: handoff.date,
  })
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
    // Persisted objects use the same shape as query handoffs; require full treatment for singles.
    return parseBookHandoffQuery(parsed)
  } catch {
    return null
  }
}
