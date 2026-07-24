import { describe, expect, it } from 'vitest'

import { primaryBookHref, primaryBookHrefKind } from './primaryBookHref'
import { LANDING_WHATSAPP_URL } from './landingContent'
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

  it('routes Tuesday and Wednesday to packages', () => {
    const tue = new Date('2026-07-21T10:00:00+03:00')
    const wed = new Date('2026-07-22T10:00:00+03:00')
    expect(primaryBookHref(tue)).toBe(SERVICES_ROUTES.fullPackages)
    expect(primaryBookHref(wed)).toBe(SERVICES_ROUTES.fullPackages)
  })

  it('routes Mon and Thu–Sat to treatments', () => {
    const mon = new Date('2026-07-20T10:00:00+03:00')
    const thu = new Date('2026-07-23T10:00:00+03:00')
    expect(primaryBookHref(mon)).toBe(SERVICES_ROUTES.singleSessions)
    expect(primaryBookHref(thu)).toBe(SERVICES_ROUTES.singleSessions)
  })
})
