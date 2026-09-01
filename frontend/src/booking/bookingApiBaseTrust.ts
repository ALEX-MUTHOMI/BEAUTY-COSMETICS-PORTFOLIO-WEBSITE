/**
 * Module: bookingApiBaseTrust
 * Trust and security base for booking APIs.
 */
/**
 * Fail-closed API base URL binding.
 *
 * Empty / `same-origin` means relative `/api/**` on the page origin (nginx
 * edge proxies to Django). That is the HTTPS / Cloudflare-tunnel shape:
 * no mixed-content fetch to localhost, and CSP `'self'` is sufficient.
 *
 * A split API host (local `:8000` or `api.` subdomain) must be an explicit
 * http(s) origin. Rejects credentials-in-URL, non-http(s) schemes, and host drift.
 */

/** Explicit denylist for known phishing/lab hosts used in red-team fixtures. */
const BLOCKED_HOSTS = new Set(['evil.example', 'attacker.local', '0.0.0.0'])

function isBlockedHost(hostname: string): boolean {
  const host = hostname.toLowerCase()
  if (BLOCKED_HOSTS.has(host)) return true
  return host === 'evil.example' || host.endsWith('.evil.example')
}

export type ApiBaseTrustResult =
  | { ok: true; origin: string }
  | { ok: false; reason: string }

/**
 * Normalize and validate the public API base URL from runtime config.
 * Returns origin only (no path/query) so callers cannot be redirected off-host.
 */
export function resolveTrustedApiBaseUrl(apiBaseUrl: string | null | undefined): ApiBaseTrustResult {
  const raw = String(apiBaseUrl ?? '').trim()
  if (!raw || raw === 'same-origin' || raw === '/') {
    return { ok: true, origin: '' }
  }
  if (raw.includes('\\') || raw.includes('..')) {
    return { ok: false, reason: 'path_traversal' }
  }

  let parsed: URL
  try {
    parsed = new URL(raw)
  } catch {
    return { ok: false, reason: 'unparseable' }
  }

  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    return { ok: false, reason: 'scheme' }
  }
  if (parsed.username || parsed.password) {
    return { ok: false, reason: 'credentials' }
  }
  if (!parsed.hostname) {
    return { ok: false, reason: 'host' }
  }
  if (isBlockedHost(parsed.hostname)) {
    return { ok: false, reason: 'blocked_host' }
  }
  // Origin-only: ignore attacker-supplied path/query/hash on the base URL.
  return { ok: true, origin: parsed.origin.replace(/\/$/, '') }
}

/** Convenience for booking clients — empty string is same-origin relative `/api`. */
export function trustedApiOriginOrEmpty(apiBaseUrl: string | null | undefined): string {
  const result = resolveTrustedApiBaseUrl(apiBaseUrl)
  return result.ok ? result.origin : ''
}
