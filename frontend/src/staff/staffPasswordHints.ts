/** Plain-language password checks aligned with server validate_staff_password. */

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

/** Map API / server messages to short staff-facing copy. */
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
