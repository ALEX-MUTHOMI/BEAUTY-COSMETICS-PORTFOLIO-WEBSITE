import { describe, expect, it } from 'vitest'
import {
  PACKAGE_DAYS,
  SINGLE_DAYS_LABEL,
  assertSafeDisplayText,
  flowSteps,
  heroSlides,
  isPackageDay,
  packageDayHeadline,
  packageDayUrgency,
  packages,
  singleTreatments,
  validateLandingPackages,
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

  it('defines booking flow steps with circle images', () => {
    expect(flowSteps).toHaveLength(3)
    expect(flowSteps[0]?.title).toBe('Choose online')
    expect(flowSteps[1]?.title).toBe('Your treatment')
    expect(flowSteps[2]?.title).toBe('Leave glowing')
    flowSteps.forEach((step) => {
      expect(step.image).toMatch(/^\/images\/step-/)
      expect(step.num).toMatch(/^\d{2}$/)
    })
  })

  it('maps hero slides to four Shee script titles', () => {
    expect(heroSlides.map((s) => s.service)).toEqual(['facial', 'massage', 'waxing', 'makeup'])
    expect(heroSlides.map((s) => s.headline)).toEqual([
      'Shee Facials',
      'Shee Massage',
      'Shee Waxing',
      'Shee Makeup',
    ])
    expect(heroSlides[0]?.image).toBe('/images/hero-facial.jpg')
    expect(heroSlides[1]?.image).toBe('/images/hero-massage.jpg')
    expect(heroSlides[2]?.image).toContain('wax')
    expect(heroSlides[3]?.image).toBe('/images/hero-makeup.jpg')
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
})
