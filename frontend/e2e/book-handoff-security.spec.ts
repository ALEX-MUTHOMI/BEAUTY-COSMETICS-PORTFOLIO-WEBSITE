import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'

test.describe('Book page handoff security', () => {
  test('accepts allowlisted package path and shows selection', async ({ page }) => {
    await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })

    await expect(page.getByText(/Full package/i).first()).toBeVisible({ timeout: 15000 })
    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Pick your day/i })).toBeVisible()
  })

  test('legacy package query redirects to clean path', async ({ page }) => {
    await page.goto(`${BASE_URL}/book?type=package&plan=classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })
    await expect(page).toHaveURL(/\/book\/package\/classic-full-package\/?$/, { timeout: 15000 })
    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible()
  })

  test('accepts allowlisted single treatment path', async ({ page }) => {
    await page.goto(`${BASE_URL}/book/waxing/brow-shaping`, { waitUntil: 'domcontentloaded' })

    await expect(page.getByText(/Single treatment/i).first()).toBeVisible({ timeout: 15000 })
    await expect(page.getByRole('heading', { name: 'Brow shaping' })).toBeVisible()
  })

  test('rejects malicious path segments without rendering attacker strings', async ({ page }) => {
    const dialogFired: string[] = []
    page.on('dialog', async (dialog) => {
      dialogFired.push(dialog.message())
      await dialog.dismiss()
    })

    await page.goto(`${BASE_URL}/book/%3Cscript%3Ealert(1)%3C%2Fscript%3E/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })

    expect(dialogFired).toHaveLength(0)
    await expect(page).toHaveURL(/\/services\/?/, { timeout: 15000 })
    await expect(page.getByText('<script>')).toHaveCount(0)
  })

  test('bare /book redirects to services', async ({ page }) => {
    await page.goto(`${BASE_URL}/book`, { waitUntil: 'domcontentloaded' })
    await expect(page).toHaveURL(/\/services\/?/, { timeout: 15000 })
  })

  test('package path shows package-day capacity hint', async ({ page }) => {
    await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })

    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible({
      timeout: 15000,
    })
    await expect(page.getByText(/Tue & Wed · limited spots/i).first()).toBeVisible()
    await expect(page.getByText(/up to \d+ clients/i)).toHaveCount(0)
    await expect(page.getByText(/Choose a day, then a time/i)).toBeVisible()
    await expect(page.getByText(/1 Date & time/i)).toBeVisible()
    await expect(page.getByText(/Next open dates/i)).toBeVisible()
    await expect(page.locator('.mobile-book-bar')).toHaveCount(0)
  })

  test('mobile book path hides sticky book bar so checkout actions stay tappable', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(`${BASE_URL}/book/massage/back-neck-and-shoulders`, {
      waitUntil: 'domcontentloaded',
    })
    await expect(page.getByRole('heading', { name: /Back, neck/i })).toBeVisible({
      timeout: 15000,
    })
    await expect(page.locator('.mobile-book-bar')).toHaveCount(0)
  })

  test('services package CTA links to clean book path', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#full-packages`, { waitUntil: 'domcontentloaded' })

    const bookLink = page
      .locator('#full-packages')
      .getByRole('link', { name: /Book (your visit|this package|Classic)/i })
      .first()
    await expect(bookLink).toHaveAttribute('href', '/book/package/classic-full-package', {
      timeout: 15000,
    })
  })

  test('serves strict security headers on book package path', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/book/package/classic-full-package`)
    expect(response.ok()).toBeTruthy()

    const csp = response.headers()['content-security-policy'] || ''
    expect(csp).toContain('script-src')
    expect(csp).not.toMatch(/script-src[^;]*unsafe-inline/)
    expect(response.headers()['x-frame-options']?.toUpperCase()).toBe('DENY')
  })
})
