import { describe, expect, it } from 'vitest'
import { normalizeKenyaPhone, validateBookingCustomer } from './bookingCustomer'

describe('bookingCustomer validation', () => {
  it('accepts normalized Kenya phone numbers', () => {
    expect(normalizeKenyaPhone('0712345678')).toBe('+254712345678')
    expect(normalizeKenyaPhone('+254 712 345 678')).toBe('+254712345678')
  })

  it('rejects honeypot submissions', () => {
    expect(
      validateBookingCustomer({
        fullName: 'Grace M',
        email: 'grace@example.com',
        phone: '0712345678',
        honeypot: 'bot filled this',
      }),
    ).toBeNull()
  })

  it('returns sanitized customer payloads', () => {
    expect(
      validateBookingCustomer({
        fullName: '  Grace   M  ',
        email: ' GRACE@EXAMPLE.COM ',
        phone: '0712345678',
        honeypot: '',
      }),
    ).toEqual({
      fullName: 'Grace M',
      email: 'grace@example.com',
      phone: '+254712345678',
    })
  })
})
