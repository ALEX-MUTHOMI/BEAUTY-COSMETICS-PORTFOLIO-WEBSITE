import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'

test.describe('Client pages', () => {
  test('FAQ page renders', async ({ page }) => {
    await page.goto(`${BASE_URL}/faq`, { waitUntil: 'networkidle' })
    await expect(page.getByRole('heading', { name: /Frequently Asked Questions/i })).toBeVisible()
  })

  test('Unknown route renders branded 404', async ({ page }) => {
    await page.goto(`${BASE_URL}/this-route-should-not-exist-12345`, { waitUntil: 'domcontentloaded' })
    await expect(page.getByRole('heading', { name: /Page not found/i })).toBeVisible()
    await expect(page.getByRole('link', { name: /Home/i })).toBeVisible()
  })
})
