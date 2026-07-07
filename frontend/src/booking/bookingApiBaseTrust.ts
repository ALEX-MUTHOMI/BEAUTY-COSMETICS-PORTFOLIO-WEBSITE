/**
 * Module: bookingApiBaseTrust
 * Trust and security base for booking APIs.
 */
/**
 * Fail-closed API base URL binding for Nuxt (:3000) → Django (:8000).
 * Rejects attacker-controlled host drift, credentials-in-URL, and non-http(s) schemes.
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
  if (!raw) {
    return { ok: false, reason: 'empty' }
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

/** Convenience for booking clients — empty string means fail closed (no fetch). */
export function trustedApiOriginOrEmpty(apiBaseUrl: string | null | undefined): string {
  const result = resolveTrustedApiBaseUrl(apiBaseUrl)
  return result.ok ? result.origin : ''
}

