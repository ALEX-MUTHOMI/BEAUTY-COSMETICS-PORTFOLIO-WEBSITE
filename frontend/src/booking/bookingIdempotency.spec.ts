import { describe, expect, it } from 'vitest'
import { buildCheckoutIdempotencyKey, buildHoldIdempotencyKey } from './bookingIdempotency'

describe('bookingIdempotency', () => {
  it('builds stable hold keys for the same slot attempt', () => {
    const input = {
      selectionPublicId: '11111111-1111-4111-8111-111111111111',
      startsAt: '2026-07-15T09:00:00+03:00',
      resourcePublicId: '22222222-2222-4222-8222-222222222222',
      attemptNonce: 'attempt-a',
    }
    expect(buildHoldIdempotencyKey(input)).toBe(buildHoldIdempotencyKey(input))
  })

  it('changes hold keys when the attempt nonce changes', () => {
    const base = {
      selectionPublicId: '11111111-1111-4111-8111-111111111111',
      startsAt: '2026-07-15T09:00:00+03:00',
      resourcePublicId: '22222222-2222-4222-8222-222222222222',
      attemptNonce: 'attempt-a',
    }
    expect(buildHoldIdempotencyKey(base)).not.toBe(
      buildHoldIdempotencyKey({ ...base, attemptNonce: 'attempt-b' }),
    )
  })

  it('keeps checkout keys stable per booking', () => {
    const bookingId = '33333333-3333-4333-8333-333333333333'
    expect(buildCheckoutIdempotencyKey(bookingId)).toBe(buildCheckoutIdempotencyKey(bookingId))
  })
})
