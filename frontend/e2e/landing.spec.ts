import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'

test.describe('Shee Aesthetics landing page', () => {
  test('hydrates and reveals homepage content after loader', async ({ page }) => {
    const consoleErrors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') consoleErrors.push(msg.text())
    })
    page.on('pageerror', (err) => consoleErrors.push(err.message))

    await page.goto(BASE_URL, { waitUntil: 'networkidle' })

    // Vue must hydrate — Nuxt bootstrap present
    const hydrated = await page.evaluate(() => {
      return {
        hasNuxt: typeof window.__NUXT__ !== 'undefined',
        vueApp: !!(document.querySelector('#__nuxt') as HTMLElement & { __vue_app__?: unknown })?.__vue_app__,
      }
    })
    expect(hydrated.hasNuxt, 'window.__NUXT__ missing — inline bootstrap blocked').toBe(true)
    expect(hydrated.vueApp, 'Vue app not mounted — client bundle failed').toBe(true)

    // Loader must not block the page indefinitely
    await expect(page.locator('.site-loader')).toHaveCount(0, { timeout: 8000 })

    // Core Mellis sections visible
    await expect(page.getByRole('heading', { name: 'Spa Beauty', level: 1 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Welcome to Shee Aesthetics', level: 2 })).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Primary' })).toBeVisible()

    // Brand lockup: logo mark beside wordmark (header instance)
    const logoLink = page.getByRole('banner').getByRole('link', { name: /Shee Aesthetics home/i })
    await expect(logoLink).toBeVisible()
    await expect(logoLink.locator('img.shee-logo__mark')).toBeVisible()
    await expect(logoLink.locator('.shee-logo__name')).toHaveText('Shee')

    // Mellis flow + package cards at bottom
    await expect(page.getByRole('heading', { name: 'Meeting', level: 3 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'What We\'re Offering', level: 2 })).toBeVisible()

    await page.locator('#packages').scrollIntoViewIfNeeded()
    await expect(page.getByRole('heading', { name: /Full Packages — Tuesday/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Book One Service at a Time/i })).toBeVisible()
    await expect(page.getByText(/Most booked/i)).toBeVisible()

    // No CSP violations in console
    const cspViolations = consoleErrors.filter((e) =>
      /content security policy|refused to execute|refused to load/i.test(e),
    )
    expect(cspViolations, `CSP errors: ${cspViolations.join('; ')}`).toHaveLength(0)
  })

  test('serves strict security headers with nonce-aware CSP', async ({ request }) => {
    const response = await request.get(BASE_URL)
    expect(response.ok()).toBeTruthy()

    const csp = response.headers()['content-security-policy'] || ''
    expect(csp).toContain('script-src')
    expect(csp).toContain("'self'")
    expect(csp).toMatch(/nonce-[A-Za-z0-9+/=]+/)
    expect(csp).not.toMatch(/script-src[^;]*unsafe-inline/)
    expect(csp).toMatch(/object-src[^;]*'none'/)
    expect(csp).toMatch(/base-uri[^;]*'none'/)
    expect(csp).toMatch(/frame-ancestors[^;]*'self'/)

    const xfo = response.headers()['x-frame-options']
    expect(xfo?.toUpperCase()).toBe('DENY')

    const xcto = response.headers()['x-content-type-options']
    expect(xcto?.toLowerCase()).toBe('nosniff')
  })

  test('does not expose server secrets in public HTML', async ({ page }) => {
    await page.goto(BASE_URL)
    const html = await page.content()

    expect(html).not.toMatch(/NUXT_TURNSTILE_SECRET/i)
    expect(html).not.toMatch(/DARAJA/i)
    expect(html).not.toMatch(/SECRET_KEY/i)
    expect(html).not.toMatch(/password\s*[:=]\s*['"][^'"]+['"]/i)
  })
})
