import { test, expect } from '@playwright/test'

/**
 * Money-path readiness smoke: book UI + Django health when the stack is up.
 * Full hold→STK conversion is covered by Vitest red-team + backend contracts;
 * this e2e stays non-flaky (does not click disabled checkout CTAs).
 */
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const API_URL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

async function apiHealthy(request: import('@playwright/test').APIRequestContext): Promise<boolean> {
  try {
    const res = await request.get(`${API_URL}/health/`, { timeout: 5000 })
    return res.ok()
  } catch {
    return false
  }
}

test.describe('Book money-path smoke (thin client readiness)', () => {
  test('book package path loads against a healthy Django API', async ({ page, request }) => {
    test.skip(!(await apiHealthy(request)), 'Django API not reachable for money-path smoke')

    const response = await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })
    expect(response?.ok()).toBeTruthy()
    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible({
      timeout: 20000,
    })
    await expect(page.getByRole('heading', { name: /Date & time/i })).toBeVisible()
    await expect(page.locator('body')).not.toContainText(/traceback|Internal Server Error/i)

    // Continue stays disabled until a real slot is selected — prove the CTA exists.
    const continueBtn = page.locator('button.book-continue').first()
    await expect(continueBtn).toBeVisible()
    await expect(continueBtn).toBeDisabled()
  })
})
