/**
 * @module bookingCustomer
 * Manages customer data for booking.
 */
export interface BookingCustomerInput {
  fullName: string
  email: string
  phone: string
}

export interface BookingCustomerValidation {
  fullName: string
  email: string
  emailConfirm: string
  phone: string
  honeypot: string
}

const NAME_RE = /^[\p{L}\p{M}' .-]{2,80}$/u
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function normalizeKenyaPhone(raw: string): string | null {
  const compact = raw.replace(/[\s()-]/g, '')
  if (/^\+254\d{9}$/.test(compact)) return compact
  if (/^254\d{9}$/.test(compact)) return `+${compact}`
  if (/^0\d{9}$/.test(compact)) return `+254${compact.slice(1)}`
  if (/^\d{9}$/.test(compact)) return `+254${compact}`
  return null
}

export function validateBookingCustomer(input: BookingCustomerValidation): BookingCustomerInput | null {
  if (input.honeypot.trim()) return null

  const fullName = input.fullName.trim().replace(/\s+/g, ' ')
  const email = input.email.trim().toLowerCase()
  const emailConfirm = input.emailConfirm.trim().toLowerCase()
  const phone = normalizeKenyaPhone(input.phone)

  if (!NAME_RE.test(fullName)) return null
  if (!EMAIL_RE.test(email) || email.length > 254) return null
  if (email !== emailConfirm) return null
  if (!phone) return null

  return { fullName, email, phone }
}
