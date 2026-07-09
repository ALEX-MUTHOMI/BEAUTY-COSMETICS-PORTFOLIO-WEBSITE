import { trimApiBaseUrl } from './bookingApi'

const CSRF_COOKIE = 'csrftoken'

function readCsrfCookie(): string {
  if (typeof document === 'undefined') return ''
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${CSRF_COOKIE}=([^;]+)`))
  return match?.[1] ? decodeURIComponent(match[1]) : ''
}

/** Same-origin relative base when the API host is an internal Docker service name. */
export function bookingApiBase(apiBaseUrl: string): string {
  try {
    const parsed = new URL(apiBaseUrl)
    if (['web', 'backend', 'django'].includes(parsed.hostname)) {
      return ''
    }
  } catch {
    return ''
  }
  return trimApiBaseUrl(apiBaseUrl)
}

/** Bootstrap Django CSRF for credentialed POSTs to the bookings API. */
export async function ensureBookingCsrfToken(apiBaseUrl: string): Promise<string | null> {
  const existing = readCsrfCookie()
  if (existing) return existing

  const base = bookingApiBase(apiBaseUrl)
  try {
    const response = await fetch(`${base}/api/csrf/`, {
      method: 'GET',
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return null
    const payload: unknown = await response.json()
    if (!payload || typeof payload !== 'object') return null
    const token = String((payload as { csrf_token?: unknown }).csrf_token ?? '')
    return token || readCsrfCookie() || null
  } catch {
    return null
  }
}
