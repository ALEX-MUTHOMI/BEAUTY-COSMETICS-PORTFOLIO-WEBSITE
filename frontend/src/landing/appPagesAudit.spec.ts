import { describe, expect, it } from 'vitest'
import { APP_ROUTES_AUDIT, validateAllRoutesAudit } from './appPagesAudit'

describe('appPagesAudit', () => {
  it('validates that all core application pages are defined and responsive', () => {
    expect(validateAllRoutesAudit(APP_ROUTES_AUDIT)).toBe(true)
    expect(APP_ROUTES_AUDIT.length).toBeGreaterThanOrEqual(6)
  })

  it('ensures each route is linked to Mellis theme architecture', () => {
    for (const route of APP_ROUTES_AUDIT) {
      expect(route.hasMellisLockup).toBe(true)
      expect(route.isResponsive).toBe(true)
    }
  })
})
