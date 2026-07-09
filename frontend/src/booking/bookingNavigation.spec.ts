import { describe, expect, it } from 'vitest'
import { resolveSafeBookingStatusPath } from './bookingNavigation'

const BOOKING_ID = '11111111-1111-4111-8111-111111111111'

describe('resolveSafeBookingStatusPath — open redirect red team', () => {
  it('accepts the canonical same-app status path', () => {
    expect(resolveSafeBookingStatusPath(`/booking/status/${BOOKING_ID}/`, BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
  })

  it('rejects absolute https phishing redirects', () => {
    expect(resolveSafeBookingStatusPath('https://evil.example/phish', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
  })

  it('rejects protocol-relative and backslash host tricks', () => {
    expect(resolveSafeBookingStatusPath('//evil.example/phish', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
    expect(resolveSafeBookingStatusPath('/\\evil.example/phish', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
  })

  it('rejects path traversal and mismatched booking ids', () => {
    expect(resolveSafeBookingStatusPath('/booking/status/../admin', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
    expect(
      resolveSafeBookingStatusPath(
        '/booking/status/22222222-2222-4222-8222-222222222222/',
        BOOKING_ID,
      ),
    ).toBe(`/booking/status/${BOOKING_ID}/`)
  })

  it('falls back to /book when booking id is not a uuid', () => {
    expect(resolveSafeBookingStatusPath('/booking/status/not-a-uuid/', 'not-a-uuid')).toBe('/book')
  })

  it('rejects javascript: and data: open-redirect payloads', () => {
    expect(resolveSafeBookingStatusPath('javascript:alert(1)', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
    expect(resolveSafeBookingStatusPath('data:text/html,phish', BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
  })

  it('rejects encoded traversal and query-string host smuggling', () => {
    expect(resolveSafeBookingStatusPath(`/booking/status/${BOOKING_ID}/?next=//evil`, BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
    expect(resolveSafeBookingStatusPath(`/booking/status/%2e%2e/${BOOKING_ID}/`, BOOKING_ID)).toBe(
      `/booking/status/${BOOKING_ID}/`,
    )
  })
})
