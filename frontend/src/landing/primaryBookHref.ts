/**
 * @module primaryBookHref
 * Primary URL resolution for booking.
 */
/**
 * Day-aware primary Book CTA — matches published hours in the footer.
 *
 * Schedule is evaluated in Africa/Nairobi (studio local), not the visitor’s
 * browser timezone, so diaspora traffic still sees Meru open/closed days.
 *
 * Sun → WhatsApp when live contact is configured; else services hub (closed).
 * Tue–Wed → featured package book path. Else → default treatment book path.
 */
import {
  defaultTreatmentBookHref,
  featuredPackageBookHref,
  treatmentBookHrefForHeroService,
} from './bookCtaTargets'
import { HERO_CTA, type HeroService } from './heroMedia'
import { LANDING_CONTACT_IS_LIVE, LANDING_WHATSAPP_URL } from './landingContent'
import { SERVICES_ROUTES } from './servicesNavigation'

export type PrimaryBookHrefKind = 'packages' | 'treatments' | 'whatsapp'

export type PrimaryBookContactOverride = {
  contactIsLive?: boolean
  whatsappUrl?: string
}

/** Studio timezone for open/closed day bias on Book CTAs. */
export const STUDIO_TIME_ZONE = 'Africa/Nairobi'

/** Weekday in Africa/Nairobi: 0 Sun … 6 Sat (same numbering as Date#getDay). */
export function studioWeekday(now: Date = new Date(), timeZone: string = STUDIO_TIME_ZONE): number {
  const weekday = new Intl.DateTimeFormat('en-US', { timeZone, weekday: 'short' }).format(now)
  const map: Record<string, number> = {
    Sun: 0,
    Mon: 1,
    Tue: 2,
    Wed: 3,
    Thu: 4,
    Fri: 5,
    Sat: 6,
  }
  return map[weekday] ?? now.getDay()
}

export function primaryBookHrefKind(now: Date = new Date()): PrimaryBookHrefKind {
  const day = studioWeekday(now)
  if (day === 0) return 'whatsapp'
  if (day === 2 || day === 3) return 'packages'
  return 'treatments'
}

/**
 * Day-aware primary Book — deep-links into /book/... (not /services).
 * Sun → WhatsApp when live; else services hub.
 */
export function primaryBookHref(
  now: Date = new Date(),
  contact: PrimaryBookContactOverride = {},
): string {
  const kind = primaryBookHrefKind(now)
  const contactIsLive = contact.contactIsLive ?? LANDING_CONTACT_IS_LIVE
  const whatsappUrl = contact.whatsappUrl ?? LANDING_WHATSAPP_URL
  if (kind === 'whatsapp') {
    return contactIsLive && whatsappUrl ? whatsappUrl : SERVICES_ROUTES.page
  }
  if (kind === 'packages') return featuredPackageBookHref()
  return defaultTreatmentBookHref()
}

export function primaryBookIsExternal(href: string): boolean {
  return href.startsWith('http://') || href.startsWith('https://') || href.startsWith('tel:')
}

/**
 * Day-aware hero Book this visit — opens /book/... for the active slide.
 * Packages day → Classic Full Package; treatment day → slide highlight;
 * Sunday → WhatsApp when live, else /services.
 */
export function heroCtaForSlide(
  slide: Pick<{ service: HeroService }, 'service'>,
  now: Date = new Date(),
  contact: PrimaryBookContactOverride = {},
): { label: string; to: string } {
  const kind = primaryBookHrefKind(now)
  if (kind === 'whatsapp') {
    return { label: HERO_CTA.label, to: primaryBookHref(now, contact) }
  }
  if (kind === 'packages') {
    return { label: HERO_CTA.label, to: featuredPackageBookHref() }
  }
  return { label: HERO_CTA.label, to: treatmentBookHrefForHeroService(slide.service) }
}
