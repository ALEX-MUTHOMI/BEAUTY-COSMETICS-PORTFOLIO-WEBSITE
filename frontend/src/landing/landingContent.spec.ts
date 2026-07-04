import { describe, expect, it } from 'vitest'
import {
  PACKAGE_DAYS,
  assertSafeDisplayText,
  isPackageDay,
  packageDayHeadline,
  packageDayUrgency,
  packages,
  validateLandingPackages,
} from './landingContent'

describe('landingContent', () => {
  it('sells Tue and Wed as the only full-package days', () => {
    expect(PACKAGE_DAYS).toEqual(['Tuesday', 'Wednesday'])
    expect(isPackageDay('Tuesday')).toBe(true)
    expect(isPackageDay('Wednesday')).toBe(true)
    expect(isPackageDay('Monday')).toBe(false)
    expect(isPackageDay('Saturday')).toBe(false)
  })

  it('uses must-book urgency copy for package days', () => {
    expect(packageDayHeadline.toLowerCase()).toContain('book')
    expect(packageDayUrgency.toLowerCase()).toMatch(/tue|tuesday/)
    expect(packageDayUrgency.toLowerCase()).toMatch(/wed|wednesday/)
    expect(packageDayUrgency.toLowerCase()).toMatch(/fill|book/)
  })

  it('defines Mellis-style packages with feature lists and a featured plan', () => {
    expect(validateLandingPackages(packages)).toBe(true)
    const featured = packages.find((p) => p.featured)
    expect(featured?.badge).toBeTruthy()
    expect(featured?.includes.length).toBeGreaterThanOrEqual(4)
  })

  it('rejects unsafe display strings (XSS guard for future CMS copy)', () => {
    expect(assertSafeDisplayText('Shee Aesthetics')).toBe(true)
    expect(assertSafeDisplayText('<script>alert(1)</script>')).toBe(false)
    expect(assertSafeDisplayText('javascript:alert(1)')).toBe(false)
  })
})
