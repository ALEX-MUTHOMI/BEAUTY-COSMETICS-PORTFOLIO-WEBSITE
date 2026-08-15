import { describe, expect, it } from 'vitest'
import {
  BW_MAKEUP_FILTER_STAGE,
  FEATURED_CARD_DARK_CANVAS,
  LANDING_CONTACT_PLACEHOLDER_E164,
  MELLIS_PALETTE,
  MELLIS_TYPOGRAPHY,
  PACKAGE_DAYS,
  SINGLE_DAYS_LABEL,
  assertSafeDisplayText,
  flowSteps,
  getFeaturedPackages,
  heroSlides,
  isPackageDay,
  landingContactFromE164,
  loaderSafetyTimeoutMs,
  packageDayHeadline,
  packageDayUrgency,
  packages,
  resolveWhatsappE164,
  singleTreatments,
  validateBwMakeupFilter,
  validateFeaturedDarkCardCanvas,
  validateLandingPackages,
  validateMellisDesignSystem,
  validateTreatmentCards,
} from './landingContent'

describe('landingContent', () => {
  it('sells Tue and Wed as the only full-package days', () => {
    expect(PACKAGE_DAYS).toEqual(['Tuesday', 'Wednesday'])
    expect(isPackageDay('Tuesday')).toBe(true)
    expect(isPackageDay('Wednesday')).toBe(true)
    expect(isPackageDay('Monday')).toBe(false)
    expect(isPackageDay('Saturday')).toBe(false)
  })

  it('uses clear marketing copy for package days without filler jargon', () => {
    expect(packageDayHeadline.toLowerCase()).toContain('package')
    expect(packageDayUrgency.toLowerCase()).toMatch(/tue|tuesday|package/)
    expect(packageDayUrgency).not.toMatch(/experience|journey|unlock/i)
  })

  it('defines booking flow steps as book → pay → visit (no images)', () => {
    expect(flowSteps).toHaveLength(3)
    expect(flowSteps[0]?.title).toBe('Choose your visit')
    expect(flowSteps[1]?.title).toBe('Pay with M-Pesa')
    expect(flowSteps[2]?.title).toBe('Come in glowing')
    flowSteps.forEach((step) => {
      expect(step).not.toHaveProperty('image')
      expect(step.num).toMatch(/^\d{2}$/)
      expect(step.text.length).toBeGreaterThan(12)
    })
    expect(flowSteps[1]?.text.toLowerCase()).toMatch(/m-?pesa|slot|receipt/)
  })

  it('maps hero slides to four Shee script titles', () => {
    expect(heroSlides.map((s) => s.service)).toEqual(['makeup', 'facial', 'massage', 'waxing'])
    expect(heroSlides.map((s) => s.headline)).toEqual([
      'Shee Makeup',
      'Shee Facials',
      'Shee Massage',
      'Shee Waxing',
    ])
    expect(heroSlides[0]?.image).toBe('/images/hero-makeup.jpg')
    expect(heroSlides[1]?.image).toBe('/images/hero-facial.jpg')
    expect(heroSlides[2]?.image).toBe('/images/hero-massage.jpg')
    expect(heroSlides[3]?.image).toBe('/images/hero-waxing.jpg')
    heroSlides.forEach((slide) => {
      expect(slide.alt.length).toBeGreaterThan(10)
      expect(slide.eyebrow.toLowerCase()).toContain('unwind')
      expect(slide.headline.toLowerCase()).not.toContain('meru')
    })
  })

  it('defines Mellis-style packages with feature lists and a featured plan', () => {
    expect(validateLandingPackages(packages)).toBe(true)
    const featured = packages.find((p) => p.featured)
    expect(featured?.badge).toBeTruthy()
    expect(featured?.includes.length).toBeGreaterThanOrEqual(4)
  })

  it('returns a single featured package for the home rail', () => {
    const home = getFeaturedPackages()
    expect(home).toHaveLength(1)
    expect(home[0]?.featured).toBe(true)
  })

  it('offers single treatments on non-package days', () => {
    expect(singleTreatments.length).toBeGreaterThanOrEqual(4)
    expect(singleTreatments.every((t) => t.daysLabel === SINGLE_DAYS_LABEL)).toBe(true)
    expect(validateTreatmentCards(singleTreatments)).toBe(true)
  })

  it('rejects unsafe display strings (XSS guard for future CMS copy)', () => {
    expect(assertSafeDisplayText('Shee Aesthetics')).toBe(true)
    expect(assertSafeDisplayText('<script>alert(1)</script>')).toBe(false)
    expect(assertSafeDisplayText('javascript:alert(1)')).toBe(false)
  })

  it('keeps WhatsApp fail-closed for placeholder and short numbers', () => {
    expect(resolveWhatsappE164('')).toBe(LANDING_CONTACT_PLACEHOLDER_E164)
    expect(resolveWhatsappE164('254700000000')).toBe(LANDING_CONTACT_PLACEHOLDER_E164)
    expect(resolveWhatsappE164('+254 712 345 678')).toBe('254712345678')
    expect(landingContactFromE164('254712345678').isLive).toBe(true)
    expect(landingContactFromE164('').whatsappUrl).toBe('')
  })

  it('enforces Mellis design system tokens and B&W aesthetic contracts', () => {
    expect(validateMellisDesignSystem(MELLIS_TYPOGRAPHY, MELLIS_PALETTE)).toBe(true)
    expect(validateBwMakeupFilter(BW_MAKEUP_FILTER_STAGE)).toBe(true)
    expect(validateFeaturedDarkCardCanvas(FEATURED_CARD_DARK_CANVAS)).toBe(true)
    expect(loaderSafetyTimeoutMs(1500)).toBe(2700)
  })
})
