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

  it('defines Mellis flow steps with circle images', () => {
    expect(flowSteps).toHaveLength(3)
    expect(flowSteps[0]?.title).toBe('Meeting')
    expect(flowSteps[1]?.title).toBe('Treatment')
    expect(flowSteps[2]?.title).toBe('Finalizing')
    flowSteps.forEach((step) => {
      expect(step.image).toMatch(/^\/images\/step-/)
      expect(step.num).toMatch(/^\d{2}$/)
    })
  })

  it('keeps hero slides short and Mellis-style — no brand in the carousel', () => {
    expect(heroSlides).toHaveLength(3)
    expect(heroSlides[0]?.title).toBe('Spa Beauty')
    expect(heroSlides[0]?.eyebrow).toMatch(/unwind/i)
    heroSlides.forEach((slide) => {
      expect(slide.title.length).toBeLessThan(30)
      expect(slide.eyebrow).not.toMatch(/shee aesthetics/i)
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
