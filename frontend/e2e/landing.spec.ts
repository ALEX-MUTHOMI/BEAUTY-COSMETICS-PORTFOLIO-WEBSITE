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

    await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 5000 })

    await expect(page.getByRole('heading', { name: 'Shee', level: 1 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Your hour to unwind', level: 2 })).toBeVisible()
    await expect(page.getByRole('navigation', { name: 'Primary' })).toBeVisible()

    const logoLink = page.getByRole('banner').getByRole('link', { name: /Shee Aesthetics home/i })
    await expect(logoLink).toBeVisible()
    await expect(logoLink.locator('.shee-logo__mark-wrap')).toBeVisible()
    await expect(logoLink.locator('img.shee-logo__mark')).toBeVisible()
    await expect(logoLink.locator('.shee-logo__name')).toHaveText('Shee')

    await expect(page.getByRole('heading', { name: 'How booking works', level: 2 })).toBeVisible()
    await expect(page.locator('.steps__compact li')).toHaveCount(3)
    await expect(page.locator('.steps__compact').getByText('Choose your visit')).toBeVisible()
    await expect(page.locator('.steps__compact').getByText('Pay with M-Pesa')).toBeVisible()
    await expect(page.locator('.steps__compact').getByText('Come in glowing')).toBeVisible()
    await expect(page.locator('.steps .steps__cta')).toHaveCount(0)
    await expect(page.locator('.steps img')).toHaveCount(0)
    await expect(page.getByRole('heading', { name: 'Clients by Shee', level: 2 })).toBeVisible()
    await expect(page.locator('#our-work .work__tile').count()).resolves.toBeGreaterThanOrEqual(8)
    await expect(page.getByRole('heading', { name: 'What we offer', level: 2 })).toBeAttached()
    await expect(page.locator('#services .offer__cell')).toHaveCount(4)
    await expect(page.locator('#services .treat-tile')).toHaveCount(0)
    await expect(page.locator('#services .offer__bg')).toBeVisible()
    await expect(page.locator('#services .offer__cta')).toBeVisible()
    await expect(page.getByRole('link', { name: /View packages/i }).first()).toBeVisible()
    await expect(page.locator('#services .offer__board')).toBeVisible()
    await expect(page.locator('#services .offer__name').first()).toHaveText('Facials')

    await page.locator('#visit-path').scrollIntoViewIfNeeded()
    await expect(page.getByRole('heading', { name: 'How would you like to visit?', level: 2 })).toBeVisible()
    await expect(page.locator('#visit-path .book-visit__path')).toBeVisible()
    await expect(page.locator('#visit-path .book-visit__lead')).toHaveCount(0)
    await expect(page.locator('#visit-path .book-visit__ribbon')).toHaveCount(0)
    await expect(page.locator('#visit-path .visit-card').filter({ hasText: 'Full packages' })).toBeVisible()
    await expect(page.locator('#visit-path .visit-card').filter({ hasText: 'Treatments' })).toBeVisible()
    await expect(page.getByRole('link', { name: /Book now/i }).first()).toBeVisible()

    await page.locator('#packages').scrollIntoViewIfNeeded()
    await expect(page.getByRole('heading', { name: 'Full packages', level: 2 })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Classic Full Package/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Book one specific treatment/i })).toHaveCount(0)
    await expect(page.locator('#packages .mellis-card')).toHaveCount(1)
    await expect(page.locator('#packages .packages__band')).toBeVisible()
    await expect(page.locator('.mellis-card__badge', { hasText: 'Most booked' })).toBeVisible()
    await expect(page.getByRole('link', { name: /Book this package/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /See all packages/i })).toBeVisible()

    await expect(page.getByRole('heading', { name: 'What clients say', level: 2 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Visit us', level: 2 })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Opening Hours', level: 3 })).toBeVisible()
    await expect(page.getByRole('link', { name: /Get directions/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Open in Google Maps/i })).toBeVisible()
    await expect(page.locator('#visit .visit-map__card')).toBeVisible()
    await expect(page.locator('#visit .visit-map__map-panel')).toBeVisible()
    await expect(page.locator('#visit .visit-map__frame')).toBeVisible()

    const directions = page.getByRole('link', { name: /Get directions/i })
    await expect(directions).toHaveAttribute('href', /google\.com\/maps\/dir/)
    const openMaps = page.getByRole('link', { name: /Open in Google Maps/i })
    await expect(openMaps).toHaveAttribute('href', /google\.com\/maps\/search/)

    const cspViolations = consoleErrors.filter((e) =>
      /content security policy|refused to execute|refused to load/i.test(e),
    )
    expect(cspViolations, `CSP errors: ${cspViolations.join('; ')}`).toHaveLength(0)
  })

  test('mobile layout keeps book bar and stacks single-column grids', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(BASE_URL, { waitUntil: 'networkidle' })

    await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 5000 })
    await expect(page.locator('.mobile-book-bar')).toBeVisible()
    await expect(page.locator('.mobile-book-bar').getByRole('link', { name: /Book your visit/i })).toBeVisible()

    await expect(page.locator('#our-work .work__tile').first()).toBeVisible()
    await expect(page.locator('#packages .mellis-card')).toHaveCount(1)
    await expect(page.getByRole('heading', { name: 'What clients say', level: 2 })).toBeVisible()
    await expect(page.locator('#services .offer__board')).toBeVisible()
    await expect(page.locator('#services .offer__cell')).toHaveCount(4)
    await expect(page.locator('#services .offer__cta')).toBeVisible()
    await expect(page.locator('#visit .visit-map__card')).toBeVisible()
    await expect(page.locator('#visit .visit-map__map-panel')).toBeVisible()
    await expect(page.locator('#visit .visit-map__frame')).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Shee', level: 1 })).toBeVisible()
  })

  for (const viewport of [
    { width: 375, height: 667, label: 'iPhone SE' },
    { width: 390, height: 844, label: 'iPhone 12' },
  ]) {
    test(`mobile-first hero chrome fits ${viewport.label} (${viewport.width}x${viewport.height})`, async ({
      page,
    }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      await page.goto(BASE_URL, { waitUntil: 'networkidle' })
      await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 5000 })

      const overflowX = await page.evaluate(() => {
        const doc = document.documentElement
        return Math.max(doc.scrollWidth, document.body.scrollWidth) - doc.clientWidth
      })
      expect(overflowX, 'horizontal overflow').toBeLessThanOrEqual(1)

      await expect(page.locator('.mobile-book-bar').getByRole('link', { name: /Book your visit/i })).toBeVisible()
      const heroTitle = page.locator('.hero-handwrite').first()
      await expect(heroTitle).toBeVisible()
      const titleBox = await heroTitle.boundingBox()
      expect(titleBox?.width ?? 0).toBeGreaterThan(40)
      const titleText = (await heroTitle.getAttribute('aria-label')) || ''
      expect(titleText.length).toBeGreaterThan(8)
      await expect(page.locator('.mobile-book-bar')).toBeVisible()
      await expect(page.locator('.hero__dots')).toBeVisible()
      await expect(page.locator('.hero__cta').first()).toBeHidden()

      const menu = page.getByRole('banner').getByRole('button', { name: /menu|open/i })
      await expect(menu).toBeVisible()
      await menu.click()
      await expect(page.locator('#site-header-mobile-nav')).toBeVisible()
      await page.getByRole('button', { name: /Close menu/i }).click()
      await expect(page.locator('#site-header-mobile-nav')).toHaveCount(0)
    })
  }

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
