import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'

test.describe('Services page security and IA', () => {
  test('rejects malicious hash fragments without script execution', async ({ page }) => {
    const dialogFired: string[] = []
    page.on('dialog', async (dialog) => {
      dialogFired.push(dialog.message())
      await dialog.dismiss()
    })

    await page.goto(`${BASE_URL}/services#<img src=x onerror=alert(1)>`, {
      waitUntil: 'networkidle',
    })

    await expect(page.getByRole('heading', { name: /How would you like to visit/i })).toBeVisible()
    expect(dialogFired).toHaveLength(0)
    await expect(page.locator('#panel-facials, [id^="panel-"]').first()).toBeVisible()
  })

  test('deep-links waxing tab from allowlisted category hash', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#waxing`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('tab', { name: 'Waxing', selected: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Waxing/i, level: 2 })).toBeVisible()
  })

  test('nav packages and singles route to canonical services anchors', async ({ page }) => {
    await page.goto(BASE_URL, { waitUntil: 'networkidle' })
    await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 5000 })

    await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Packages' }).click()
    await expect(page).toHaveURL(/\/services#full-packages/)
    await expect(page.getByRole('heading', { name: /Complete visits in one booking/i })).toBeVisible()

    await page.goto(BASE_URL, { waitUntil: 'networkidle' })
    await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Singles' }).click()
    await expect(page).toHaveURL(/\/services#single-sessions/)
    await expect(page.getByRole('heading', { name: /^Select a treatment$/i })).toBeVisible()
  })

  test('serves strict security headers on services page', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/services`)
    expect(response.ok()).toBeTruthy()

    const csp = response.headers()['content-security-policy'] || ''
    expect(csp).toContain('script-src')
    expect(csp).not.toMatch(/script-src[^;]*unsafe-inline/)
    expect(response.headers()['x-frame-options']?.toUpperCase()).toBe('DENY')
  })
})
