/**
 * @module staffUxHelpers
 * UI helpers and utilities for staff interface.
 */
/**
 * Consolidated Staff UX Helpers & Status Copy
 * Combines greeting, date, password hints, and friendly status copy.
 */

/* ------------------------------------------------------------------ */
/* 1. Nairobi Local Business Date                                      */
/* ------------------------------------------------------------------ */

/** Calendar date in Africa/Nairobi (desk business TZ), YYYY-MM-DD. */
export function staffLocalDateIso(now: Date = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Africa/Nairobi',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(now)
}

/* ------------------------------------------------------------------ */
/* 2. Staff Desk Greetings & Storage                                   */
/* ------------------------------------------------------------------ */

const GREET_STORAGE_KEY = 'shee.desk.greet'

export function firstNameFromDisplay(value: string): string {
  const cleaned = String(value || '')
    .replace(/[^a-zA-Z0-9 ._-]+/g, ' ')
    .trim()
  if (!cleaned) return ''
  const first = cleaned.split(/[\s._-]+/).find(Boolean) || ''
  if (!first) return ''
  return first.charAt(0).toUpperCase() + first.slice(1).toLowerCase()
}

export function firstNameFromEmail(email: string): string {
  const local = String(email || '').split('@', 1)[0] || ''
  return firstNameFromDisplay(local)
}

export function readStoredGreetName(storage: Storage = localStorage): string {
  try {
    return firstNameFromDisplay(storage.getItem(GREET_STORAGE_KEY) || '')
  } catch {
    return ''
  }
}

export function writeStoredGreetName(name: string, storage: Storage = localStorage): void {
  const safe = firstNameFromDisplay(name)
  if (!safe) return
  try {
    storage.setItem(GREET_STORAGE_KEY, safe.slice(0, 32))
  } catch {
    // Ignore quota / private-mode failures.
  }
}

export function timeOfDayLede(_now = new Date()): string {
  return ''
}

export function welcomeHeadline(storedName: string, typedEmail: string): string {
  const live = firstNameFromEmail(typedEmail)
  if (live) return `Welcome back, ${live}`
  const remembered = firstNameFromDisplay(storedName)
  if (remembered) return `Welcome back, ${remembered}`
  return 'Welcome back'
}

export { GREET_STORAGE_KEY }

/* ------------------------------------------------------------------ */
/* 3. Password Hints & Validation                                     */
/* ------------------------------------------------------------------ */

const MIN_LENGTH = 15

const COMMON_FRAGMENTS = [
  'password',
  'password123',
  'beauty123',
  'qwerty',
  'letmein',
  '123456',
  'makeup',
]

export function normalizePasswordHintInput(value: string): string {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

export function clientStaffPasswordHint(
  password: string,
  options: { email?: string; confirm?: string } = {},
): string | null {
  const value = String(password || '')
  if (!value) return null
  if (value.length < MIN_LENGTH) {
    return 'Use at least 15 characters.'
  }

  const compact = normalizePasswordHintInput(value)
  if (COMMON_FRAGMENTS.some((fragment) => compact.includes(normalizePasswordHintInput(fragment)))) {
    return 'That password is too common.'
  }

  const emailLocal = (String(options.email || '').split('@', 1)[0] ?? '').trim()
  const emailNorm = normalizePasswordHintInput(emailLocal)
  if (emailNorm.length >= 4 && compact.includes(emailNorm)) {
    return 'Don’t use your name or email in the password.'
  }

  if (typeof options.confirm === 'string' && options.confirm.length > 0 && options.confirm !== value) {
    return 'Passwords don’t match.'
  }

  return null
}

export function mapStaffPasswordApiMessage(raw: string): string {
  const text = String(raw || '').toLowerCase()
  if (!text) return 'We could not update the password. Please try again.'
  if (text.includes('15') || text.includes('at least')) return 'Use at least 15 characters.'
  if (text.includes('common')) return 'That password is too common.'
  if (text.includes('predictable')) return 'That password is too easy to guess.'
  if (text.includes('account details') || text.includes('derived') || text.includes('email')) {
    return 'Don’t use your name or email in the password.'
  }
  if (text.includes('match')) return 'Passwords don’t match.'
  if (text.includes('invalid') || text.includes('expired')) {
    return 'This reset link is invalid or expired.'
  }
  if (/traceback|exception|hmac|token_hash|challenge|validator/i.test(text)) {
    return 'We could not update the password. Please try again.'
  }
  return String(raw || '').slice(0, 160)
}

/* ------------------------------------------------------------------ */
/* 4. Status Copy & Desensitization                                   */
/* ------------------------------------------------------------------ */

const STATUS_COPY: Record<string, string> = {
  payment_pending: 'Awaiting payment',
  success: 'Payment confirmed',
  paid: 'Payment confirmed',
  failed: 'Payment failed',
  payment_failed: 'Payment failed',
  manual_review: 'Needs attention',
  pending_review: 'Needs attention',
  confirmed: 'Booking confirmed',
  held: 'Awaiting customer payment',
  reschedule_requested: 'Reschedule requested',
  reschedule_held: 'Reschedule in progress',
  completed: 'Service completed',
  late: 'Client running late',
  no_show: 'Client did not attend',
  checked_in: 'Client checked in',
  in_progress: 'In service',
  not_issued: 'Receipt not issued yet',
  issued: 'Receipt ready',
  sent: 'Sent',
  retry_scheduled: 'Retry scheduled',
  failed_final: 'Needs attention',
  full_package: 'Full-package day',
  normal: 'Service day',
  closed: 'Closed',
  not_started: 'Not started',
  requested: 'Reschedule requested',
  none: 'No move needed',
}

export function dayCapacityBanner(dayType: string, maxClients: number): string {
  const normalized = String(dayType || '').toLowerCase()
  if (normalized.includes('closed') || maxClients <= 0) {
    return 'Closed today — no client bookings.'
  }
  if (normalized.includes('full') || normalized.includes('package')) {
    return `Full-package day — up to ${maxClients || 3} clients.`
  }
  return `Service day — up to ${maxClients || 5} clients.`
}

const INTERNAL_WORDS = /\b(ledger|checkout session|correlation|provider payload|merchantrequest|checkoutrequest)\b/i

export function friendlyStatus(value?: string): string {
  const normalized = String(value || '').trim().toLowerCase()
  return STATUS_COPY[normalized] || 'Needs attention'
}

export function receiptChipStatus(value?: string): string {
  const normalized = String(value || '').trim().toLowerCase()
  if (!normalized || normalized === 'not_issued') return 'not_issued'
  if (normalized === 'paid' || normalized === 'generated' || normalized === 'ready') return 'issued'
  return normalized
}

export function isReceiptIssued(value?: string): boolean {
  return receiptChipStatus(value) !== 'not_issued'
}

export function containsInternalJargon(value: string): boolean {
  return INTERNAL_WORDS.test(value)
}

export function safeDisplayText(value: unknown, fallback = 'Not available'): string {
  const text = String(value || '').replace(/[<>{}`]/g, '').replace(/\s+/g, ' ').trim()
  if (!text || INTERNAL_WORDS.test(text)) {
    return fallback
  }
  return text.slice(0, 120)
}

export function isPublicBookingReference(value: string): boolean {
  return /^[0-9a-f-]{32,36}$/i.test(value) || /^[A-Z0-9-]{6,64}$/i.test(value)
}
