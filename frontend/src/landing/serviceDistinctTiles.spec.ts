import { describe, expect, it } from 'vitest'
import {
  SERVICE_DISTINCT_TILES_CONTRACT,
  validateServiceDistinctTiles,
} from './serviceDistinctTiles'

describe('serviceDistinctTiles', () => {
  it('enforces 2x2 responsive category grid on mobile viewports', () => {
    expect(validateServiceDistinctTiles(SERVICE_DISTINCT_TILES_CONTRACT)).toBe(true)
    expect(SERVICE_DISTINCT_TILES_CONTRACT.mobileCategoryGridColumns).toBe(2)
    expect(SERVICE_DISTINCT_TILES_CONTRACT.desktopCategoryGridColumns).toBe(4)
  })

  it('ensures distinct individual service tile boundaries and spacing', () => {
    expect(SERVICE_DISTINCT_TILES_CONTRACT.hasIndividualTileSeparation).toBe(true)
    expect(parseFloat(SERVICE_DISTINCT_TILES_CONTRACT.tileMarginBottom)).toBeGreaterThanOrEqual(0.5)
  })
})
