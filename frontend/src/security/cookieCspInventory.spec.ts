import { readFileSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

/**
 * Origin cookie + CSP inventory — must stay aligned with Cloudflare Client-Side Security
 * script/cookie monitoring once the zone is orange-clouded.
 */
describe('origin cookie and CSP inventory', () => {
  const nuxtConfig = readFileSync(join(__dirname, '../../nuxt.config.ts'), 'utf8')
  const csurf = readFileSync(join(__dirname, '../../src/booking/bookingCsrf.ts'), 'utf8')

  it('enables nonce CSP with strict-dynamic and closes object/base vectors', () => {
    expect(nuxtConfig).toContain("nonce: true")
    expect(nuxtConfig).toContain("'strict-dynamic'")
    expect(nuxtConfig).toContain("'nonce-{{nonce}}'")
    expect(nuxtConfig).toContain("'object-src'")
    expect(nuxtConfig).toContain("'base-uri'")
    expect(nuxtConfig).toContain("'none'")
    expect(nuxtConfig).not.toMatch(/script-src:[\s\S]*'unsafe-inline'/)
  })

  it('documents expected first-party cookie names for CF cookie monitor', () => {
    // Django API origin
    expect(csurf).toContain("CSRF_COOKIE = 'csrftoken'")
    // Nuxt-origin csurf (separate from Django booking CSRF)
    expect(nuxtConfig).toMatch(/csurf:/)
    expect(nuxtConfig).toMatch(/sameSite:\s*'strict'/)
    // Inventory comment contract for operators
    const inventory = [
      'csrftoken',
      'sessionid',
      'remembered-device',
      'nuxt-csurf',
    ]
    expect(inventory.length).toBe(4)
  })

  it('allowlists only Turnstile + Insights third-party scripts in script-src', () => {
    expect(nuxtConfig).toContain('https://challenges.cloudflare.com/turnstile/')
    expect(nuxtConfig).toContain('https://static.cloudflareinsights.com')
  })

  it('ships Permissions-Policy and env-gated CSP report-only hooks', () => {
    expect(nuxtConfig).toMatch(/permissionsPolicy:\s*\{/)
    expect(nuxtConfig).toContain('NUXT_PUBLIC_CSP_REPORT_ONLY')
    expect(nuxtConfig).toContain('NUXT_PUBLIC_TRUSTED_TYPES_PREP')
  })
})
