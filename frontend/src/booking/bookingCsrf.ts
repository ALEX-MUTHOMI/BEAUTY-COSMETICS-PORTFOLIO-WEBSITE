/**
 * Module: bookingCsrf
 * CSRF protection and handling.
 */
import { trimApiBaseUrl } from './bookingApi'
import { resolveTrustedApiBaseUrl } from './bookingApiBaseTrust'

const CSRF_COOKIE = 'csrftoken'
const CSRF_BOOTSTRAP_TIMEOUT_MS = 10_000

function readCsrfCookie(): string {
  if (typeof document === 'undefined') return ''
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${CSRF_COOKIE}=([^;]+)`))
  return match?.[1] ? decodeURIComponent(match[1]) : ''
}

/** Same-origin relative base when the API host is an internal Docker service name. */
export function bookingApiBase(apiBaseUrl: string): string {
  const trusted = resolveTrustedApiBaseUrl(apiBaseUrl)
  if (!trusted.ok) return ''
  try {
    const parsed = new URL(trusted.origin)
    if (['web', 'backend', 'django'].includes(parsed.hostname)) {
      return ''
    }
  } catch {
    return ''
  }
  return trimApiBaseUrl(trusted.origin)
}

export type EnsureCsrfOptions = {
  /** Staff login must not trust a Nuxt-origin cookie — always hit API JSON. */
  forceRefresh?: boolean
  timeoutMs?: number
  fetcher?: typeof fetch
}

/** Bootstrap Django CSRF for credentialed POSTs to the bookings API. */
export async function ensureBookingCsrfToken(
  apiBaseUrl: string,
  options: EnsureCsrfOptions = {},
): Promise<string | null> {
  const forceRefresh = Boolean(options.forceRefresh)
  if (!forceRefresh) {
    const existing = readCsrfCookie()
    if (existing) return existing
  }

  const base = bookingApiBase(apiBaseUrl)
  const fetcher = options.fetcher ?? fetch
  const timeoutMs = options.timeoutMs ?? CSRF_BOOTSTRAP_TIMEOUT_MS
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetcher(`${base}/api/csrf/`, {
      method: 'GET',
      credentials: 'include',
      signal: controller.signal,
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return null
    const payload: unknown = await response.json()
    if (!payload || typeof payload !== 'object') return null
    const token = String((payload as { csrf_token?: unknown }).csrf_token ?? '')
    return token || (!forceRefresh ? readCsrfCookie() : null) || null
  } catch {
    return null
  } finally {
    clearTimeout(timeoutId)
  }
}

