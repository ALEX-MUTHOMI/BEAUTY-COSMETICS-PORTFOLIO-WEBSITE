import { packages } from './landingContent'
import { serviceCategories } from './servicesContent'
import { isServiceCategoryId, type ServiceCategoryId } from './servicesNavigation'

/** Stable URL slug for a display name — never pass raw names in query strings. */
export function slugifyCatalogName(name: string): string {
  return name
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export const PACKAGE_PLAN_SLUGS = packages.map((pkg) => slugifyCatalogName(pkg.name)) as readonly string[]

export type PackagePlanSlug = (typeof PACKAGE_PLAN_SLUGS)[number]

const PACKAGE_BY_SLUG = Object.fromEntries(
  packages.map((pkg) => [slugifyCatalogName(pkg.name), pkg] as const),
) as Record<PackagePlanSlug, (typeof packages)[number]>

export function isPackagePlanSlug(value: string): value is PackagePlanSlug {
  return Object.prototype.hasOwnProperty.call(PACKAGE_BY_SLUG, value)
}

export function packagePlanSlugForName(name: string): PackagePlanSlug | null {
  const slug = slugifyCatalogName(name)
  return isPackagePlanSlug(slug) ? slug : null
}

export function getPackageBySlug(slug: PackagePlanSlug) {
  return PACKAGE_BY_SLUG[slug]
}

/** Treatment slug → { category, name } built from static catalog only. */
const TREATMENT_INDEX = new Map<
  string,
  { category: ServiceCategoryId; name: string }
>()

for (const category of serviceCategories) {
  if (!isServiceCategoryId(category.id)) continue
  for (const treatment of category.treatments) {
    TREATMENT_INDEX.set(slugifyCatalogName(treatment.name), {
      category: category.id,
      name: treatment.name,
    })
  }
}

export const TREATMENT_SLUGS = [...TREATMENT_INDEX.keys()] as readonly string[]

export type TreatmentSlug = (typeof TREATMENT_SLUGS)[number]

export function isTreatmentSlug(value: string): value is TreatmentSlug {
  return TREATMENT_INDEX.has(value)
}

export function treatmentSlugForName(name: string): TreatmentSlug | null {
  const slug = slugifyCatalogName(name)
  return isTreatmentSlug(slug) ? slug : null
}

export function getTreatmentBySlug(slug: TreatmentSlug) {
  return TREATMENT_INDEX.get(slug) ?? null
}
