import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'

const DASH_AS_PUNCTUATION = /[—–]|\s-\s/

test.describe('Client pages (plain copy + Mellis flower)', () => {
  test('FAQ shows flower accents and short plain copy', async ({ page }) => {
    await page.goto(`${BASE_URL}/faq`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('heading', { name: /^Questions$/i })).toBeVisible()
    await expect(page.getByTestId('mellis-flower').first()).toBeVisible()

    const flowers = page.locator('[data-testid="mellis-flower"]')
    await expect(flowers).toHaveCount(2)
    await expect(flowers.first()).toHaveAttribute('src', /flower\.png/)

    const mainText = await page.locator('main.faq').innerText()
    expect(mainText).not.toMatch(DASH_AS_PUNCTUATION)
    expect(mainText.toLowerCase()).not.toMatch(/capacity|turnaround|shared studio/)
  })

  test('Unknown route shows branded 404 with flower accents', async ({ page }) => {
    await page.goto(`${BASE_URL}/this-route-should-not-exist-12345`, {
      waitUntil: 'domcontentloaded',
    })

    await expect(page.getByRole('heading', { name: /Page not found/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /^Home$/i }).first()).toBeVisible()
    await expect(page.getByTestId('mellis-flower').first()).toBeVisible()

    const mainText = await page.locator('main').first().innerText()
    expect(mainText).not.toMatch(DASH_AS_PUNCTUATION)
  })

  test('Dedicated /404 route shows flower accents', async ({ page }) => {
    await page.goto(`${BASE_URL}/404`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: /Page not found/i })).toBeVisible()
    await expect(page.getByTestId('mellis-flower').first()).toBeVisible()
  })

  test('Confirmation page shows flower accents', async ({ page }) => {
    await page.goto(`${BASE_URL}/booking/confirmation/demo-id/`, {
      waitUntil: 'domcontentloaded',
    })
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    await expect(page.getByTestId('mellis-flower').first()).toBeVisible()
  })
})
