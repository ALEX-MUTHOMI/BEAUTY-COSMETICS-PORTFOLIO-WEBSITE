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
}

const GENERIC_LOGIN_ERROR = 'Invalid credentials.'
const DEFAULT_NEXT_PATH = '/staff/dashboard'

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

export async function staffPasswordLogin(
  apiBaseUrl: string,
  payload: StaffLoginPayload,
  fetcher: typeof fetch = fetch,
): Promise<StaffLoginResult> {
  const response = await fetcher(buildStaffLoginUrl(apiBaseUrl), {
    method: 'POST',
    credentials: 'include',
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

  if (!response.ok) {
    return { ok: false, nextPath: '', message: GENERIC_LOGIN_ERROR }
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

  return {
    ok: true,
    nextPath,
    message: 'Signed in.',
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

export { sanitizeNextPath }
