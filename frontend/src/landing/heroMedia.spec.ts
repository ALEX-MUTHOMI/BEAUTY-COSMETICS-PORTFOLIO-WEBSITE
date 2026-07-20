import { describe, expect, it } from 'vitest'
import {
  assertHeroImagesAreLocal,
  assertHeroLayoutPhotoForward,
  assertHeroServiceMatch,
  formatHeroHeadline,
  getHeroLcpHref,
  assertHeroTiming,
  HERO_COPY_FADE_MS,
  HERO_CROSSFADE_MS,
  HERO_CTA,
  HERO_FADE_MS,
  HERO_LAYOUT,
  heroSlides,
  shouldMountHeroImage,
} from './heroMedia'

describe('heroMedia', () => {
  it('keeps four treatment frames in lockstep', () => {
    expect(assertHeroServiceMatch()).toBe(true)
    expect(heroSlides).toHaveLength(4)
    expect(heroSlides.map((s) => s.service)).toEqual(['facial', 'massage', 'waxing', 'makeup'])
  })

  it('uses Mellis-style Shee + treatment script headlines', () => {
    expect(formatHeroHeadline(heroSlides[0]!)).toBe('Shee Facials')
    expect(formatHeroHeadline(heroSlides[1]!)).toBe('Shee Massage')
    expect(formatHeroHeadline(heroSlides[2]!)).toBe('Shee Waxing')
    expect(formatHeroHeadline(heroSlides[3]!)).toBe('Shee Makeup')
    heroSlides.forEach((slide) => {
      expect(slide.headline).toMatch(/^Shee /)
      expect(slide.eyebrow.toLowerCase()).toContain('unwind')
    })
  })

  it('keeps Discover more CTA like Mellis Discover More', () => {
    expect(HERO_CTA.label.toLowerCase()).toContain('discover')
    expect(HERO_CTA.to).toBe('/services')
  })

  it('preloads the facial LCP asset', () => {
    expect(getHeroLcpHref()).toBe('/images/hero-facial.jpg')
  })

  it('mounts every frame for the ambient fade gallery', () => {
    for (let active = 0; active < 4; active += 1) {
      for (let index = 0; index < 4; index += 1) {
        expect(shouldMountHeroImage(active, index, 4)).toBe(true)
      }
    }
  })

  it('defines stable object-position and srcset for every slide', () => {
    heroSlides.forEach((slide) => {
      expect(slide.objectPosition.length).toBeGreaterThan(3)
      expect(slide.srcset).toContain(slide.image)
      expect(slide.width).toBeGreaterThan(800)
      expect(slide.height).toBeGreaterThan(600)
    })
  })

  it('uses a wave seam and calm crossfade (no ash fog)', () => {
    expect(assertHeroLayoutPhotoForward()).toBe(true)
    expect(assertHeroTiming()).toBe(true)
    expect(HERO_CROSSFADE_MS).toBe(1800)
    expect(HERO_LAYOUT.fadeMs).toBe(1800)
    expect(HERO_FADE_MS).toBe(5600)
    expect(HERO_COPY_FADE_MS).toBeGreaterThanOrEqual(1000)
    expect(HERO_LAYOUT.blendFadePercent).toBe(0)
    expect(HERO_LAYOUT.seam).toBe('wave')
  })

  it('hardens hero image paths to same-origin local assets only', () => {
    expect(assertHeroImagesAreLocal()).toBe(true)
    expect(
      assertHeroImagesAreLocal([
        {
          ...heroSlides[0]!,
          image: '//evil.example/x.jpg',
        },
      ]),
    ).toBe(false)
  })
})
