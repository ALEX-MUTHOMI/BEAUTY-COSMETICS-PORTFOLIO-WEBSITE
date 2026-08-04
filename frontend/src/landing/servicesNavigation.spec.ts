import { describe, expect, it } from 'vitest'
import {
  categoryHrefForSingle,
  isServiceCategoryId,
  isServicesSectionId,
  normalizeServicesHash,
  parseServicesHash,
  SERVICES_ROUTES,
} from './servicesNavigation'

describe('servicesNavigation', () => {
  it('allowlists section hashes for safe scroll targets', () => {
    expect(isServicesSectionId('full-packages')).toBe(true)
    expect(isServicesSectionId('single-sessions')).toBe(true)
    expect(isServicesSectionId('treatments')).toBe(false)
    expect(isServicesSectionId('<script>')).toBe(false)
  })

  it('allowlists category tab ids', () => {
    expect(isServiceCategoryId('waxing')).toBe(true)
    expect(isServiceCategoryId('facials')).toBe(true)
    expect(isServiceCategoryId('../../../etc')).toBe(false)
  })

  it('rejects malicious or encoded hash fragments', () => {
    expect(normalizeServicesHash('<img src=x onerror=alert(1)>')).toBe('')
    expect(normalizeServicesHash('waxing%0a%0d')).toBe('')
    expect(normalizeServicesHash('facials/../../admin')).toBe('facials')
    expect(normalizeServicesHash('javascript:alert(1)')).toBe('')
    expect(parseServicesHash('#<script>alert(1)</script>')).toEqual({})
    expect(parseServicesHash('#waxing?drop=tables')).toEqual({ category: 'waxing' })
  })

  it('maps single treatment names to category deep links', () => {
    expect(categoryHrefForSingle('Waxing')).toBe(`${SERVICES_ROUTES.page}#waxing`)
    expect(categoryHrefForSingle('Massage')).toBe(`${SERVICES_ROUTES.page}#massage`)
    expect(categoryHrefForSingle('Unknown')).toBe(SERVICES_ROUTES.singleSessions)
    expect(categoryHrefForSingle('<script>')).toBe(SERVICES_ROUTES.singleSessions)
  })
})
