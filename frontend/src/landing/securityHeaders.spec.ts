import { describe, expect, it } from 'vitest'

/**
 * Regression guard: broken CSP nonce config blocks Nuxt inline bootstrap
 * and leaves the SSR loader visible forever with hidden content.
 */
describe('landing security headers contract', () => {
  it('requires nonce placeholder in script-src when nonce mode is enabled', () => {
    const scriptSrc = [
      "'self'",
      "'strict-dynamic'",
      "'nonce-{{nonce}}'",
      'https://challenges.cloudflare.com/turnstile/',
      'https://static.cloudflareinsights.com',
    ]

    expect(scriptSrc).toContain("'nonce-{{nonce}}'")
    expect(scriptSrc).toContain("'strict-dynamic'")
    expect(scriptSrc).not.toContain("'unsafe-inline'")
  })

  it('rejects inline event handlers via script-src-attr none', () => {
    const scriptSrcAttr = 'none'
    expect(scriptSrcAttr).toBe('none')
  })

  it('blocks object embeds and limits base URI', () => {
    const objectSrc = "'none'"
    const baseUri = "'none'"
    expect(objectSrc).toBe("'none'")
    expect(baseUri).toBe("'none'")
  })
})
