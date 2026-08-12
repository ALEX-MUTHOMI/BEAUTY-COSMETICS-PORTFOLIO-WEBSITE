import { describe, expect, it } from 'vitest'
import { PACKAGE_GRID_CONTRACT, validatePackageGridContract } from './packageMobileGrid'

describe('packageMobileGrid', () => {
  it('enforces 100% full-width vertical stacking on mobile viewports', () => {
    expect(validatePackageGridContract(PACKAGE_GRID_CONTRACT)).toBe(true)
    expect(PACKAGE_GRID_CONTRACT.mobileWidth).toBe('100%')
  })

  it('enforces 3-column grid contract on desktop viewports', () => {
    expect(PACKAGE_GRID_CONTRACT.desktopLayout).toContain('repeat(3, 1fr)')
  })
})
