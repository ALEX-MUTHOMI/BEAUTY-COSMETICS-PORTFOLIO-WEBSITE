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

    const hydrated = await page.evaluate(() => {
      return {
        hasNuxt: typeof window.__NUXT__ !== 'undefined',
        vueApp: !!(document.querySelector('#__nuxt') as HTMLElement & { __vue_app__?: unknown })?.__vue_app__,
      }
    })
    expect(hydrated.hasNuxt, 'window.__NUXT__ missing — inline bootstrap blocked').toBe(true)
    expect(hydrated.vueApp, 'Vue app not mounted — client bundle failed').toBe(true)

    await expect(page.locator('.site-loader')).toHaveCount(0, { timeout: 5000 })

    await expect(page.getByRole('heading', { name: 'Shee', level: 1 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Your hour to unwind', level: 2 })).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Primary' })).toBeVisible()

    const logoLink = page.getByRole('banner').getByRole('link', { name: /Shee Aesthetics home/i })
    await expect(logoLink).toBeVisible()
    await expect(logoLink.locator('.shee-logo__mark-wrap')).toBeVisible()
    await expect(logoLink.locator('img.shee-logo__mark')).toBeVisible()
    await expect(logoLink.locator('.shee-logo__name')).toHaveText('Shee')

    await expect(page.getByRole('heading', { name: 'Choose online', level: 3 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Clients by Shee', level: 2 })).toBeVisible()
    await expect(page.locator('#our-work .work__tile').count()).resolves.toBeGreaterThanOrEqual(8)
    await expect(page.getByRole('heading', { name: 'Facials, massage, waxing and makeup', level: 2 })).toBeAttached()
    await expect(page.locator('#services .offer__cell')).toHaveCount(4)
    await expect(page.locator('#services .treat-tile')).toHaveCount(0)
    await expect(page.locator('#services .offer__bg')).toBeVisible()
    await expect(page.locator('#services .offer__cta')).toBeVisible()
    await expect(page.getByRole('link', { name: /View packages/i }).first()).toBeVisible()
    await expect(page.locator('#services .offer__board')).toBeVisible()
    await expect(page.locator('#services .offer__name').first()).toHaveText('Facials')

    await page.locator('#visit-path').scrollIntoViewIfNeeded()
    await expect(page.getByRole('heading', { name: 'How would you like to visit?', level: 2 })).toBeVisible()
    await expect(page.getByRole('link', { name: /Full glow days/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Single sessions/i })).toBeVisible()

    await page.locator('#packages').scrollIntoViewIfNeeded()
    await expect(page.getByRole('heading', { name: /Full visits, Tuesday/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Book one specific treatment/i })).toHaveCount(0)
    await expect(page.locator('#packages .mellis-card')).toHaveCount(1)
    await expect(page.locator('#packages .packages__band')).toBeVisible()
    await expect(page.locator('.mellis-card__badge', { hasText: 'Most booked' })).toBeVisible()
    await expect(page.getByRole('link', { name: /See all packages/i })).toBeVisible()

    await expect(page.getByRole('heading', { name: 'What our clients say', level: 2 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Opening Hours', level: 2 })).toBeVisible()
    await expect(page.getByRole('link', { name: /Open in Maps/i })).toBeVisible()
    await expect(page.locator('#visit .visit-map__hours-panel')).toBeVisible()
    await expect(page.locator('#visit .visit-map__frame')).toBeVisible()

    const cspViolations = consoleErrors.filter((e) =>
      /content security policy|refused to execute|refused to load/i.test(e),
    )
    expect(cspViolations, `CSP errors: ${cspViolations.join('; ')}`).toHaveLength(0)
  })

  test('mobile layout keeps book bar and stacks single-column grids', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(BASE_URL, { waitUntil: 'networkidle' })

    await expect(page.locator('.site-loader')).toHaveCount(0, { timeout: 5000 })
    await expect(page.locator('.mobile-book-bar')).toBeVisible()
    await expect(page.locator('.mobile-book-bar').getByRole('link', { name: /Book your visit/i })).toBeVisible()

    await expect(page.locator('#our-work .work__tile').first()).toBeVisible()
    await expect(page.locator('#packages .mellis-card')).toHaveCount(1)
    await expect(page.getByRole('heading', { name: 'What our clients say', level: 2 })).toBeVisible()
    await expect(page.locator('#services .offer__board')).toBeVisible()
    await expect(page.locator('#services .offer__cell')).toHaveCount(4)
    await expect(page.locator('#services .offer__cta')).toBeVisible()
    await expect(page.locator('#visit .visit-map__hours-panel')).toBeVisible()
    await expect(page.locator('#visit .visit-map__frame-wrap')).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Shee', level: 1 })).toBeVisible()
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
