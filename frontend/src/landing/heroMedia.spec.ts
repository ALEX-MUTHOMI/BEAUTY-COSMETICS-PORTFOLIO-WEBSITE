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
    expect(heroSlides.map((s) => s.service)).toEqual(['makeup', 'facial', 'massage', 'waxing'])
  })

  it('uses Mellis-style Shee + treatment script headlines', () => {
    expect(formatHeroHeadline(heroSlides[0]!)).toBe('Shee Makeup')
    expect(formatHeroHeadline(heroSlides[1]!)).toBe('Shee Facials')
    expect(formatHeroHeadline(heroSlides[2]!)).toBe('Shee Massage')
    expect(formatHeroHeadline(heroSlides[3]!)).toBe('Shee Waxing')
    heroSlides.forEach((slide) => {
      expect(slide.headline).toMatch(/^Shee /)
      expect(slide.eyebrow.toLowerCase()).toContain('unwind')
    })
  })

  it('keeps Discover more CTA like Mellis Discover More', () => {
    expect(HERO_CTA.label.toLowerCase()).toContain('discover')
    expect(HERO_CTA.to).toBe('/services')
  })

  it('preloads the makeup LCP asset at a mobile-friendly width', () => {
    expect(getHeroLcpHref()).toBe('/images/hero-makeup-960.jpg')
  })

  it('mounts only active and next frames on first paint', () => {
    expect(shouldMountHeroImage(0, 0, 4)).toBe(true)
    expect(shouldMountHeroImage(0, 1, 4)).toBe(true)
    expect(shouldMountHeroImage(0, 2, 4)).toBe(false)
    expect(shouldMountHeroImage(0, 3, 4)).toBe(false)
    expect(shouldMountHeroImage(3, 3, 4)).toBe(true)
    expect(shouldMountHeroImage(3, 0, 4)).toBe(true)
    expect(shouldMountHeroImage(3, 1, 4)).toBe(false)
  })

  it('defines stable object-position and multi-width srcset for every slide', () => {
    heroSlides.forEach((slide) => {
      expect(slide.objectPosition.length).toBeGreaterThan(3)
      expect(slide.srcset).toContain(`${slide.image} 1600w`)
      expect(slide.srcset).toContain('-640.jpg 640w')
      expect(slide.srcset).toContain('-960.jpg 960w')
      expect(slide.srcset).toContain('-1280.jpg 1280w')
      expect(slide.sizes).toBe('100vw')
      expect(slide.width).toBeGreaterThanOrEqual(800)
      expect(slide.height).toBeGreaterThanOrEqual(500)
    })
  })

  it('prefers sharp treatment frames for the carousel', () => {
    expect(heroSlides[0]?.image).toBe('/images/hero-makeup.jpg')
    expect(heroSlides[1]?.image).toBe('/images/hero-facial.jpg')
    expect(heroSlides[2]?.image).toBe('/images/hero-massage.jpg')
    expect(heroSlides[3]?.image).toBe('/images/hero-waxing.jpg')
  })

  it('uses a wave seam and calm crossfade (no ash fog)', () => {
    expect(assertHeroLayoutPhotoForward()).toBe(true)
    expect(assertHeroTiming()).toBe(true)
    expect(HERO_CROSSFADE_MS).toBe(2800)
    expect(HERO_LAYOUT.fadeMs).toBe(2800)
    expect(HERO_FADE_MS).toBe(9000)
    expect(HERO_COPY_FADE_MS).toBeGreaterThanOrEqual(1200)
    expect(HERO_LAYOUT.blendFadePercent).toBe(0)
    expect(HERO_LAYOUT.seam).toBe('wave')
  })

  it('locks clear hero heights per breakpoint (no rem caps)', () => {
    expect(HERO_LAYOUT.mobileHeightCss).toBe('92dvh')
    expect(HERO_LAYOUT.minHeightRem).toBe(28)
    expect(HERO_LAYOUT.tabletHeightCss).toBe('92vh')
    expect(HERO_LAYOUT.tabletMinHeightRem).toBe(38)
    expect(HERO_LAYOUT.desktopHeightCss).toBe('100vh')
    expect(HERO_LAYOUT.desktopMinHeightRem).toBe(44)
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
