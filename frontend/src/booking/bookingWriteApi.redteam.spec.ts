import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { createBookingHold } from './bookingWriteApi'
import type { BookingSlot, ResolvedSelection } from './bookingPublicApi'

const selection: ResolvedSelection = {
  selectionType: 'normal',
  publicId: '11111111-1111-4111-8111-111111111111',
  slug: 'soft-glam',
  name: 'Soft glam',
  durationMinutes: 60,
}

const slot: BookingSlot = {
  startsAt: '2026-07-15T09:00:00+03:00',
  endsAt: '2026-07-15T10:00:00+03:00',
  durationMinutes: 60,
  bufferMinutes: 0,
  resourcePublicId: '22222222-2222-4222-8222-222222222222',
  servicePublicId: '11111111-1111-4111-8111-111111111111',
}

describe('bookingWriteApi hold body — mass assignment / bot red team', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('never sends price/amount fields even if a bot tries to inject via customer object shape', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 201,
      json: async () => ({
        booking: {
          booking_public_id: '33333333-3333-4333-8333-333333333333',
          status: 'held',
          hold_expires_at: '2026-07-15T09:10:00+03:00',
          hold_ttl_minutes: 10,
          next_action: 'checkout_required',
        },
      }),
    })

    await createBookingHold(
      'https://api.example.com',
      selection,
      slot,
      { fullName: 'Grace M', email: 'grace@example.com', phone: '+254712345678' },
      'hold:attempt-1',
      'csrf-token',
      { turnstileToken: 'token-abc' },
    )

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const body = JSON.parse(String(init.body)) as Record<string, unknown>
    expect(body).not.toHaveProperty('amount')
    expect(body).not.toHaveProperty('price')
    expect(body).not.toHaveProperty('currency')
    expect(body).not.toHaveProperty('total_amount')
    expect(body.turnstile_token).toBe('token-abc')
    expect(body.idempotency_key).toBe('hold:attempt-1')
    expect(init.headers).toEqual(
      expect.objectContaining({
        'X-CSRFToken': 'csrf-token',
        'Content-Type': 'application/json',
      }),
    )
  })

  it('always includes turnstile_token (empty string) so abuse-mode server gate cannot be omitted', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Booking request could not be accepted.' }),
    })

    await createBookingHold(
      'https://api.example.com',
      selection,
      slot,
      { fullName: 'Grace M', email: 'grace@example.com', phone: '+254712345678' },
      'hold:attempt-2',
      'csrf-token',
    )

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    const body = JSON.parse(String(init.body)) as Record<string, unknown>
    expect(body).toHaveProperty('turnstile_token', '')
  })
})
