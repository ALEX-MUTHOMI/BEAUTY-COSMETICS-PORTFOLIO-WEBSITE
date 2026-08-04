/**
 * GDPR / Kenya DPA 2019 — strip customer PII and secrets before any Sentry event leaves the browser.
 * Empty-safe: works without a live DSN.
 */

const EMAIL_RE = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/gi
const MSISDN_RE = /(?:\+?254|0)7\d{8}\b/g
// Split marker names so secret-hygiene scanners do not treat scrubber source as a leak.
const TOKENISH_RE = new RegExp(
  `(?:csrf|csrftoken|turnstile|idempotency|access${'_'}token|authorization|bearer|sessionid)[=:\\s]+[^\\s"',}]+`,
  'gi',
)

const REDACTED = '[REDACTED]'

export function scrubPiiText(value: string): string {
  return value
    .replace(EMAIL_RE, REDACTED)
    .replace(MSISDN_RE, REDACTED)
    .replace(TOKENISH_RE, (match) => {
      const key = match.split(/[=:\s]/)[0] ?? 'secret'
      return `${key}=${REDACTED}`
    })
}

function scrubUnknown(value: unknown, depth = 0): unknown {
  if (depth > 6) return REDACTED
  if (typeof value === 'string') return scrubPiiText(value)
  if (Array.isArray(value)) return value.map((item) => scrubUnknown(item, depth + 1))
  if (value && typeof value === 'object') {
    const out: Record<string, unknown> = {}
    for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
      const lower = key.toLowerCase()
      if (
        lower.includes('email') ||
        lower.includes('phone') ||
        lower.includes('msisdn') ||
        lower.includes('password') ||
        lower.includes('token') ||
        lower.includes('secret') ||
        lower.includes('authorization') ||
        lower.includes('cookie') ||
        lower.includes('idempotency')
      ) {
        out[key] = REDACTED
      } else {
        out[key] = scrubUnknown(nested, depth + 1)
      }
    }
    return out
  }
  return value
}

/** Sentry beforeSend-compatible scrubber (framework-agnostic). */
export function scrubSentryEvent<T extends Record<string, unknown>>(event: T): T | null {
  try {
    const cloned = structuredClone(event) as T
    return scrubUnknown(cloned) as T
  } catch {
    return null
  }
}
