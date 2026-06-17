/**
 * @module bookCtaTargets
 * Defines target URLs and sections for CTA buttons.
 */
/**
 * Canonical book deep-links for primary CTAs (skip /services catalog hop).
 */
import { bookHrefForPackageName, bookHrefForTreatment } from './bookingHandoff'
import type { HeroService } from './heroMedia'
import { SINGLE_HIGHLIGHT_PICKS } from './servicesContent'
import type { ServiceCategoryId } from './servicesNavigation'
import { SERVICES_ROUTES } from './servicesNavigation'

/** Featured package for package-day Book CTAs. */
export const FEATURED_PACKAGE_NAME = 'Classic Full Package'

const HERO_SERVICE_TO_CATEGORY: Record<HeroService, ServiceCategoryId> = {
  facial: 'facials',
  massage: 'massage',
  waxing: 'waxing',
  makeup: 'makeup',
}

/** Default single when Book has no slide context (header / sticky / treatments day). */
export const DEFAULT_TREATMENT_CATEGORY: ServiceCategoryId = 'facials'

export function featuredPackageBookHref(): string {
  return bookHrefForPackageName(FEATURED_PACKAGE_NAME)
}

export function defaultTreatmentBookHref(
  categoryId: ServiceCategoryId = DEFAULT_TREATMENT_CATEGORY,
): string {
  const name = SINGLE_HIGHLIGHT_PICKS[categoryId]
  return bookHrefForTreatment(categoryId, name)
}

export function treatmentBookHrefForHeroService(service: HeroService): string {
  return defaultTreatmentBookHref(HERO_SERVICE_TO_CATEGORY[service])
}

/** Browse-only catalog entry (See all / Explore). */
export const CATALOG_PACKAGES_HREF = SERVICES_ROUTES.fullPackages
export const CATALOG_TREATMENTS_HREF = SERVICES_ROUTES.singleSessions

export { SINGLE_HIGHLIGHT_PICKS }
