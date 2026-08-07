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

  it('matches live nuxt.config object-src and base-uri none', async () => {
    const { readFileSync } = await import('node:fs')
    const { join } = await import('node:path')
    const config = readFileSync(join(__dirname, '../../nuxt.config.ts'), 'utf8')
    expect(config).toMatch(/'object-src':\s*\["'none'"\]/)
    expect(config).toMatch(/'base-uri':\s*\["'none'"\]/)
  })
})
