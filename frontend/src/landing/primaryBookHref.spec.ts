import { describe, expect, it } from 'vitest'

import { featuredPackageBookHref, defaultTreatmentBookHref } from './bookCtaTargets'
import { LANDING_WHATSAPP_URL } from './landingContent'
import { heroCtaForSlide, primaryBookHref, primaryBookHrefKind } from './primaryBookHref'
import { SERVICES_ROUTES } from './servicesNavigation'

describe('primaryBookHref', () => {
  it('routes Sunday to WhatsApp only when live contact is configured', () => {
    const sun = new Date('2026-07-26T10:00:00+03:00') // Sunday Africa/Nairobi
    expect(primaryBookHrefKind(sun)).toBe('whatsapp')
    // Placeholder contact must not ship wa.me/254700000000
    expect(primaryBookHref(sun)).toBe(SERVICES_ROUTES.page)
    expect(primaryBookHref(sun)).not.toBe(LANDING_WHATSAPP_URL)
    expect(
      primaryBookHref(sun, {
        contactIsLive: true,
        whatsappUrl: 'https://wa.me/254712345678',
      }),
    ).toBe('https://wa.me/254712345678')
  })

  it('uses Africa/Nairobi weekday even when the Date is UTC evening', () => {
    // Monday 01:30 UTC = Monday 04:30 Nairobi
    const monUtc = new Date('2026-07-20T01:30:00Z')
    expect(primaryBookHrefKind(monUtc)).toBe('treatments')
  })

  it('routes Tuesday and Wednesday to featured package book path', () => {
    const tue = new Date('2026-07-21T10:00:00+03:00')
    const wed = new Date('2026-07-22T10:00:00+03:00')
    expect(primaryBookHref(tue)).toBe(featuredPackageBookHref())
    expect(primaryBookHref(wed)).toBe('/book/package/classic-full-package')
  })

  it('routes Mon and Thu–Sat to default treatment book path', () => {
    const mon = new Date('2026-07-20T10:00:00+03:00')
    const thu = new Date('2026-07-23T10:00:00+03:00')
    expect(primaryBookHref(mon)).toBe(defaultTreatmentBookHref())
    expect(primaryBookHref(thu)).toBe('/book/facials/deep-cleansing-facial')
  })
})

describe('heroCtaForSlide', () => {
  it('deep-links package day to Classic Full Package', () => {
    const tue = new Date('2026-07-21T10:00:00+03:00')
    expect(heroCtaForSlide({ service: 'makeup' }, tue).to).toBe(
      '/book/package/classic-full-package',
    )
    expect(heroCtaForSlide({ service: 'makeup' }, tue).label.toLowerCase()).toContain('book')
  })

  it('deep-links treatment day to the slide highlight book path', () => {
    const mon = new Date('2026-07-20T10:00:00+03:00')
    expect(heroCtaForSlide({ service: 'makeup' }, mon).to).toBe('/book/makeup/soft-glam')
    expect(heroCtaForSlide({ service: 'facial' }, mon).to).toBe(
      '/book/facials/deep-cleansing-facial',
    )
  })
})
