import { describe, expect, it } from 'vitest'
import {
  assertHeroServiceMatch,
  getHeroLcpHref,
  heroSlides,
  shouldMountHeroImage,
} from './heroMedia'

describe('heroMedia', () => {
  it('keeps service titles, paths, and alts in lockstep', () => {
    expect(assertHeroServiceMatch()).toBe(true)
  })

  it('preloads the facial LCP asset', () => {
    expect(getHeroLcpHref()).toBe('/images/hero-facial.jpg')
  })

  it('only mounts the active slide and the next slide', () => {
    expect(shouldMountHeroImage(0, 0, 3)).toBe(true)
    expect(shouldMountHeroImage(0, 1, 3)).toBe(true)
    expect(shouldMountHeroImage(0, 2, 3)).toBe(false)
    expect(shouldMountHeroImage(2, 2, 3)).toBe(true)
    expect(shouldMountHeroImage(2, 0, 3)).toBe(true)
    expect(shouldMountHeroImage(2, 1, 3)).toBe(false)
  })

  it('defines stable object-position and srcset for every slide', () => {
    expect(heroSlides).toHaveLength(3)
    heroSlides.forEach((slide) => {
      expect(slide.objectPosition.length).toBeGreaterThan(3)
      expect(slide.srcset).toContain(slide.image)
      expect(slide.width).toBeGreaterThan(800)
      expect(slide.height).toBeGreaterThan(600)
    })
  })
})
