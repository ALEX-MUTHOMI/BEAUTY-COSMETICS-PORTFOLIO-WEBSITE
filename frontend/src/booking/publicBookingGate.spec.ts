import { describe, expect, it } from 'vitest'

import { isPublicBookingEnabled } from './publicBookingGate'

describe('publicBookingGate', () => {
  it('is fail-closed unless explicitly true', () => {
    expect(isPublicBookingEnabled(undefined)).toBe(false)
    expect(isPublicBookingEnabled(null)).toBe(false)
    expect(isPublicBookingEnabled('')).toBe(false)
    expect(isPublicBookingEnabled('false')).toBe(false)
    expect(isPublicBookingEnabled('true')).toBe(true)
    expect(isPublicBookingEnabled(true)).toBe(true)
  })
})
