import { describe, expect, it } from 'vitest'
import {
  PACKAGE_CARD_COMPACT_CONTRACT,
  validatePackageCardCompactDensity,
} from './packageCardCompactDensity'

describe('packageCardCompactDensity', () => {
  it('enforces compact padding bounds on mobile and desktop', () => {
    expect(validatePackageCardCompactDensity(PACKAGE_CARD_COMPACT_CONTRACT)).toBe(true)
    expect(parseFloat(PACKAGE_CARD_COMPACT_CONTRACT.maxCardPaddingMobile)).toBeLessThanOrEqual(1.25)
    expect(parseFloat(PACKAGE_CARD_COMPACT_CONTRACT.maxCardPaddingDesktop)).toBeLessThanOrEqual(1.5)
  })

  it('enforces 2-column inclusion grid layout on mobile to reduce height by >50%', () => {
    expect(PACKAGE_CARD_COMPACT_CONTRACT.inclusionGridColumnsMobile).toBeGreaterThanOrEqual(2)
  })
})
