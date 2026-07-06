import { describe, expect, it } from 'vitest'
import {
  bookHrefForPackageName,
  bookHrefForTreatment,
  buildBookHref,
  normalizeBookQueryToken,
  parseBookHandoffQuery,
} from './bookingHandoff'

describe('bookingHandoff', () => {
  it('builds allowlisted package handoff URLs', () => {
    expect(bookHrefForPackageName('Classic Full Package')).toBe(
      '/book?type=package&plan=classic-full-package',
    )
    expect(buildBookHref({ type: 'package', plan: 'glow-package' })).toBe(
      '/book?type=package&plan=glow-package',
    )
  })

  it('builds allowlisted single treatment handoff URLs', () => {
    expect(bookHrefForTreatment('waxing', 'Brow shaping')).toBe(
      '/book?type=single&category=waxing&treatment=brow-shaping',
    )
    expect(bookHrefForTreatment('facials', null)).toBe('/book?type=single&category=facials')
  })

  it('parses valid query params into resolved selection', () => {
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

  it('rejects malicious or mismatched query tokens', () => {
    expect(normalizeBookQueryToken('<script>alert(1)</script>')).toBe('')
    expect(normalizeBookQueryToken('javascript:alert(1)')).toBe('')
    expect(parseBookHandoffQuery({ type: 'package', plan: 'not-a-plan' })).toBeNull()
    expect(
      parseBookHandoffQuery({
        type: 'single',
        category: 'facials',
        treatment: 'brow-shaping',
      }),
    ).toBeNull()
    expect(parseBookHandoffQuery({ type: 'drop-tables', plan: 'classic-full-package' })).toBeNull()
    expect(parseBookHandoffQuery({ type: 'single', category: 'waxing%0a%0d' })).toBeNull()
  })

  it('accepts optional ISO dates only', () => {
    expect(
      parseBookHandoffQuery({
        type: 'package',
        plan: 'classic-full-package',
        date: '2026-07-07',
      }),
    ).toMatchObject({ date: '2026-07-07' })
    expect(
      parseBookHandoffQuery({
        type: 'package',
        plan: 'classic-full-package',
        date: '2026-13-40',
      }),
    ).toMatchObject({ type: 'package', plan: 'classic-full-package' })
    expect(
      parseBookHandoffQuery({
        type: 'package',
        plan: 'classic-full-package',
        date: '2026-13-40',
      })?.date,
    ).toBeUndefined()
  })
})
