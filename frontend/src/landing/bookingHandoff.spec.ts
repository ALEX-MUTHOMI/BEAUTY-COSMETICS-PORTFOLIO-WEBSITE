import { describe, expect, it } from 'vitest'
import {
  bookHrefForPackageName,
  bookHrefForTreatment,
  buildBookHref,
  canonicalBookPath,
  normalizeBookQueryToken,
  parseBookHandoffQuery,
  parseBookPathParams,
} from './bookingHandoff'

describe('bookingHandoff', () => {
  it('builds allowlisted package handoff path URLs', () => {
    expect(bookHrefForPackageName('Classic Full Package')).toBe(
      '/book/package/classic-full-package',
    )
    expect(buildBookHref({ type: 'package', plan: 'glow-package' })).toBe(
      '/book/package/glow-package',
    )
  })

  it('builds allowlisted single treatment handoff path URLs', () => {
    expect(bookHrefForTreatment('waxing', 'Brow shaping')).toBe(
      '/book/waxing/brow-shaping',
    )
    expect(bookHrefForTreatment('facials', null)).toBe('/services')
  })

  it('parses valid path params into resolved selection', () => {
    expect(
      parseBookPathParams({
        category: 'waxing',
        treatment: 'brow-shaping',
      }),
    ).toMatchObject({
      type: 'single',
      category: 'waxing',
      treatment: 'brow-shaping',
      treatmentName: 'Brow shaping',
    })
    expect(parseBookPathParams({ plan: 'classic-full-package' })).toMatchObject({
      type: 'package',
      plan: 'classic-full-package',
      planName: 'Classic Full Package',
    })
  })

  it('parses valid legacy query params into resolved selection', () => {
    expect(
      parseBookHandoffQuery({
        type: 'single',
        category: 'waxing',
        treatment: 'brow-shaping',
      }),
    ).toMatchObject({
      type: 'single',
      category: 'waxing',
      treatment: 'brow-shaping',
      treatmentName: 'Brow shaping',
    })
  })

  it('rejects category-only single query (must pick a treatment)', () => {
    expect(parseBookHandoffQuery({ type: 'single', category: 'facials' })).toBeNull()
  })

  it('rejects malicious or mismatched path/query tokens', () => {
    expect(normalizeBookQueryToken('<script>alert(1)</script>')).toBe('')
    expect(normalizeBookQueryToken('javascript:alert(1)')).toBe('')
    expect(parseBookHandoffQuery({ type: 'package', plan: 'not-a-plan' })).toBeNull()
    expect(parseBookPathParams({ plan: 'not-a-plan' })).toBeNull()
    expect(
      parseBookHandoffQuery({
        type: 'single',
        category: 'facials',
        treatment: 'brow-shaping',
      }),
    ).toBeNull()
    expect(
      parseBookPathParams({
        category: 'facials',
        treatment: 'brow-shaping',
      }),
    ).toBeNull()
    expect(parseBookHandoffQuery({ type: 'drop-tables', plan: 'classic-full-package' })).toBeNull()
    expect(parseBookHandoffQuery({ type: 'single', category: 'waxing%0a%0d' })).toBeNull()
    expect(
      parseBookPathParams({
        category: '../admin',
        treatment: 'brow-shaping',
      }),
    ).toBeNull()
  })

  it('maps legacy query handoffs to canonical clean paths', () => {
    const handoff = parseBookHandoffQuery({
      type: 'package',
      plan: 'classic-full-package',
    })
    expect(handoff).not.toBeNull()
    expect(canonicalBookPath(handoff!)).toBe('/book/package/classic-full-package')
  })

  it('accepts optional ISO dates only', () => {
    expect(
      parseBookPathParams({
        plan: 'classic-full-package',
        date: '2026-07-07',
      }),
    ).toMatchObject({ date: '2026-07-07' })
    expect(
      parseBookHandoffQuery({
        type: 'package',
        plan: 'classic-full-package',
        date: '2026-13-40',
      })?.date,
    ).toBeUndefined()
  })
})
