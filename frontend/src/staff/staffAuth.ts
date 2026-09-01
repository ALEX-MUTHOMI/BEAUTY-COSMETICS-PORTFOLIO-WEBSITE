/**
 * @module staffAuth
 * Authentication and authorization logic for staff members.
 */
export interface StaffLoginPayload {
  email: string
  password: string
  csrfToken: string
  turnstileToken?: string
}

export interface StaffLoginResult {
  ok: boolean
  nextPath: string
  message: string
  displayName: string
  /** Availability / session — show Retry, never treat as bad password. */
  retryable?: boolean
}

const GENERIC_LOGIN_ERROR = 'Invalid credentials.'
const RATE_LIMIT_ERROR = 'Please try again later.'
/** Network / abort — desk may be down or the browser could not reach the API. */
const DESK_UNREACHABLE_ERROR = 'Could not reach the desk. Refresh and try again.'
/** Redis/throttle/admission 503 — distinct from invalid credentials and from 429. */
const DESK_UNAVAILABLE_ERROR = 'Desk temporarily unavailable. Try again in a moment.'
/**
 * CSRF/session 403 — not an auth oracle (never "invalid credentials").
 * Often host mismatch (localhost vs 127.0.0.1) with SameSite=Strict cookies.
 */
const SESSION_REFRESH_ERROR = 'Sign-in session expired. Refresh the page and try again.'
const DEFAULT_NEXT_PATH = '/staff/dashboard'
/** Fail closed so the desk never sticks on “Signing in…” forever. */
const LOGIN_FETCH_TIMEOUT_MS = 15_000

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, '')
}

function publicApiBaseUrl(apiBaseUrl: string): string {
  try {
    const parsed = new URL(apiBaseUrl)
    if (['web', 'backend', 'django'].includes(parsed.hostname)) {
      return ''
    }
  } catch {
    return ''
  }
  return trimTrailingSlash(apiBaseUrl)
}

function sanitizeNextPath(nextPath?: string): string {
  if (
    !nextPath ||
    !nextPath.startsWith('/') ||
    nextPath.startsWith('//') ||
    !nextPath.startsWith('/staff/') ||
    /[\r\n]/.test(nextPath)
  ) {
    return DEFAULT_NEXT_PATH
  }
  return nextPath
}

export function buildStaffLoginUrl(apiBaseUrl: string): string {
  return `${publicApiBaseUrl(apiBaseUrl)}/api/staff/auth/login/`
}

export function buildStaffGoogleLoginUrl(apiBaseUrl: string, nextPath = DEFAULT_NEXT_PATH): string {
  const baseUrl = publicApiBaseUrl(apiBaseUrl)
  const query = new URLSearchParams({ next: sanitizeNextPath(nextPath) }).toString()
  if (!baseUrl) {
    return `/api/staff/auth/google/start/?${query}`
  }
  return `${baseUrl}/api/staff/auth/google/start/?${query}`
}

export function buildStaffAppleLoginUrl(apiBaseUrl: string, nextPath = DEFAULT_NEXT_PATH): string {
  const baseUrl = publicApiBaseUrl(apiBaseUrl)
  const query = new URLSearchParams({ next: sanitizeNextPath(nextPath) }).toString()
  if (!baseUrl) {
    return `/api/staff/auth/apple/start/?${query}`
  }
  return `${baseUrl}/api/staff/auth/apple/start/?${query}`
}

/**
 * Map HTTP status → staff-facing message without credential enumeration.
 * 403 is CSRF/session (retry refresh), not "desk down" and not bad password.
 * 503 is availability; 429 is rate limit — both retryable, neither is invalid creds.
 */
function failureMessageForStatus(status: number): { message: string; retryable: boolean } {
  if (status === 429) return { message: RATE_LIMIT_ERROR, retryable: true }
  if (status === 503) return { message: DESK_UNAVAILABLE_ERROR, retryable: true }
  if (status === 403) return { message: SESSION_REFRESH_ERROR, retryable: true }
  return { message: GENERIC_LOGIN_ERROR, retryable: false }
}

/** True when portal origin host ≠ API host (breaks SameSite=Strict CSRF cookies). */
export function staffApiHostMismatch(apiBaseUrl: string, pageHostname?: string): boolean {
  if (typeof pageHostname !== 'string' || !pageHostname) return false
  try {
    const apiHost = new URL(apiBaseUrl).hostname
    if (!apiHost || ['web', 'backend', 'django'].includes(apiHost)) return false
    return apiHost !== pageHostname
  } catch {
    return false
  }
}

export async function staffPasswordLogin(
  apiBaseUrl: string,
  payload: StaffLoginPayload,
  fetcher: typeof fetch = fetch,
): Promise<StaffLoginResult> {
  let response: Response
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), LOGIN_FETCH_TIMEOUT_MS)
  try {
    response = await fetcher(buildStaffLoginUrl(apiBaseUrl), {
      method: 'POST',
      credentials: 'include',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': payload.csrfToken,
      },
      body: JSON.stringify({
        email: payload.email.trim().toLowerCase(),
        password: payload.password,
        turnstile_token: payload.turnstileToken || '',
      }),
    })
  } catch {
    return {
      ok: false,
      nextPath: '',
      message: DESK_UNREACHABLE_ERROR,
      displayName: '',
      retryable: true,
    }
  } finally {
    clearTimeout(timeoutId)
  }

  if (!response.ok) {
    const failure = failureMessageForStatus(response.status)
    return {
      ok: false,
      nextPath: '',
      message: failure.message,
      displayName: '',
      retryable: failure.retryable,
    }
  }

  let data: unknown = {}
  try {
    data = await response.json()
  } catch {
    data = {}
  }

  const nextPath =
    typeof data === 'object' && data !== null && 'next' in data && typeof data.next === 'string'
      ? sanitizeNextPath(data.next)
      : DEFAULT_NEXT_PATH
  const displayName =
    typeof data === 'object' && data !== null && 'display_name' in data && typeof data.display_name === 'string'
      ? data.display_name
      : ''

  return {
    ok: true,
    nextPath,
    message: 'Signed in.',
    displayName,
  }
}

export async function fetchStaffOAuthProviders(
  apiBaseUrl: string,
  fetcher: typeof fetch = fetch,
): Promise<{ google: boolean; apple: boolean }> {
  try {
    const response = await fetcher(`${publicApiBaseUrl(apiBaseUrl)}/api/staff/auth/providers/`, {
      credentials: 'include',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      return { google: false, apple: false }
    }
    const data = (await response.json()) as { google?: unknown; apple?: unknown }
    return {
      google: Boolean(data.google),
      apple: Boolean(data.apple),
    }
  } catch {
    return { google: false, apple: false }
  }
}

export function storageContainsStaffSecrets(storage: Storage): boolean {
  for (let index = 0; index < storage.length; index += 1) {
    const key = storage.key(index) || ''
    const value = storage.getItem(key) || ''
    if (/staff|token|session|password|checkoutrequest|merchantrequest/i.test(`${key}:${value}`)) {
      return true
    }
  }
  return false
}

export async function requestStaffPasswordReset(
  apiBaseUrl: string,
  email: string,
  csrfToken: string,
  fetcher: typeof fetch = fetch,
): Promise<{ ok: boolean; message: string }> {
  const response = await fetcher(`${publicApiBaseUrl(apiBaseUrl)}/api/staff/auth/password-reset/request/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
    body: JSON.stringify({ email: email.trim().toLowerCase() }),
  })
  return {
    ok: response.ok,
    message: 'If the account exists, reset instructions have been sent.',
  }
}

export async function confirmStaffPasswordReset(
  apiBaseUrl: string,
  token: string,
  newPassword: string,
  csrfToken: string,
  fetcher: typeof fetch = fetch,
): Promise<{ ok: boolean; message: string }> {
  const response = await fetcher(`${publicApiBaseUrl(apiBaseUrl)}/api/staff/auth/password-reset/confirm/`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      Accept: 'application/json',
    },
    body: JSON.stringify({ token: token.trim(), new_password: newPassword }),
  })
  if (!response.ok) {
    return { ok: false, message: 'Password reset request is invalid or expired.' }
  }
  return { ok: true, message: 'Password reset complete. You can sign in with your new password.' }
}

export {
  sanitizeNextPath,
  DESK_UNREACHABLE_ERROR,
  DESK_UNAVAILABLE_ERROR,
  SESSION_REFRESH_ERROR,
  RATE_LIMIT_ERROR,
  GENERIC_LOGIN_ERROR,
}
