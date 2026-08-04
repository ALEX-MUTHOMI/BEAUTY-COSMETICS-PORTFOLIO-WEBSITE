import { containsUnsafeDecodedToken } from '../security/textGuards'

/** Canonical routes and hash allowlists for the services page (no user-controlled IDs). */

export const SERVICES_ROUTES = {
  page: '/services',
  fullPackages: '/services#full-packages',
  singleSessions: '/services#single-sessions',
} as const

export const SERVICES_SECTION_IDS = ['full-packages', 'single-sessions'] as const
export type ServicesSectionId = (typeof SERVICES_SECTION_IDS)[number]

export const SERVICE_CATEGORY_IDS = ['facials', 'massage', 'waxing', 'makeup'] as const
export type ServiceCategoryId = (typeof SERVICE_CATEGORY_IDS)[number]

/** Homepage single card name → treatment menu tab id */
export const SINGLE_NAME_TO_CATEGORY: Record<string, ServiceCategoryId> = {
  Facial: 'facials',
  Massage: 'massage',
  Waxing: 'waxing',
  Makeup: 'makeup',
}

export function isServicesSectionId(value: string): value is ServicesSectionId {
  return (SERVICES_SECTION_IDS as readonly string[]).includes(value)
}

export function isServiceCategoryId(value: string): value is ServiceCategoryId {
  return (SERVICE_CATEGORY_IDS as readonly string[]).includes(value)
}

/** Strip URI decoding tricks and path-like fragments before allowlist checks. */
export function normalizeServicesHash(raw: string): string {
  const withoutLead = raw.replace(/^#/, '').trim()
  if (!withoutLead || /[<>"'`]/.test(withoutLead)) return ''

  try {
    const decoded = decodeURIComponent(withoutLead)
    if (containsUnsafeDecodedToken(decoded)) return ''
    const firstToken = decoded.split(/[?#/\\]/)[0]?.trim() ?? ''
    return /^[a-z0-9-]+$/i.test(firstToken) ? firstToken.toLowerCase() : ''
  } catch {
    return ''
  }
}

export function parseServicesHash(raw: string): {
  section?: ServicesSectionId
  category?: ServiceCategoryId
} {
  const token = normalizeServicesHash(raw)
  if (!token) return {}
  if (isServicesSectionId(token)) return { section: token }
  if (isServiceCategoryId(token)) return { category: token }
  return {}
}

export function categoryHrefForSingle(name: string): string {
  const category = SINGLE_NAME_TO_CATEGORY[name]
  if (!category || !isServiceCategoryId(category)) {
    return SERVICES_ROUTES.singleSessions
  }
  return `${SERVICES_ROUTES.page}#${category}`
}
