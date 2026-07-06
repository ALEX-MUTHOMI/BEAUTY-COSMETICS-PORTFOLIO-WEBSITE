import { describe, expect, it } from 'vitest'
import { PACKAGE_PLAN_SLUGS, slugifyCatalogName, treatmentSlugForName } from './bookingCatalog'
import { packages } from './landingContent'
import { serviceCategories } from './servicesContent'

describe('bookingCatalog', () => {
  it('assigns stable slugs to every package', () => {
    expect(PACKAGE_PLAN_SLUGS).toHaveLength(packages.length)
    expect(PACKAGE_PLAN_SLUGS).toContain('classic-full-package')
    expect(PACKAGE_PLAN_SLUGS).toContain('glow-package')
    expect(PACKAGE_PLAN_SLUGS).toContain('relax-package')
  })

  it('slugifies treatment names from the static menu', () => {
    const waxing = serviceCategories.find((c) => c.id === 'waxing')
    const brow = waxing?.treatments.find((t) => /brow/i.test(t.name))
    expect(brow).toBeTruthy()
    expect(slugifyCatalogName(brow!.name)).toBe('brow-shaping')
    expect(treatmentSlugForName(brow!.name)).toBe('brow-shaping')
  })
})
