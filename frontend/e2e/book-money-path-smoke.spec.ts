import { test, expect } from '@playwright/test'

/**
 * Money-path smoke against a live stack (fake M-Pesa provider).
 * Skips cleanly when API/FE are unreachable so CSP-only CI jobs stay green.
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

test.describe('Book money-path smoke (hold → checkout → STK → status)', () => {
  test('guest can reach status after fake STK when API is up', async ({ page, request }) => {
    test.skip(!(await apiHealthy(request)), 'Django API not reachable for money-path smoke')

    await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })
    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible({
      timeout: 20000,
    })

    // Pick first available day button if calendar rendered.
    const dayButton = page.locator('[data-book-day], button[data-date], .book-day').first()
    if (await dayButton.count()) {
      await dayButton.click()
    }

    const slotButton = page.locator('[data-book-slot], button[data-starts-at], .book-slot').first()
    if (await slotButton.count()) {
      await slotButton.click()
    }

    const continueBtn = page.getByRole('button', { name: /continue|checkout|next/i }).first()
    if (await continueBtn.count()) {
      await continueBtn.click()
    }

    // Customer panel — fill only if visible (path may already be mid-checkout).
    const name = page.getByLabel(/full name|name/i).first()
    if (await name.isVisible().catch(() => false)) {
      await name.fill('Playwright Smoke Guest')
      await page.getByLabel(/^email$/i).first().fill('playwright-smoke@example.com')
      const emailConfirm = page.getByLabel(/confirm email|email confirm/i).first()
      if (await emailConfirm.count()) {
        await emailConfirm.fill('playwright-smoke@example.com')
      }
      await page.getByLabel(/phone/i).first().fill('0712345678')
      const pay = page.getByRole('button', { name: /pay|stk|mpesa|hold|confirm/i }).first()
      await pay.click()
    }

    // Success path lands on status or confirmation with a public booking id.
    await expect(page).toHaveURL(/\/booking\/(status|confirmation)\//, { timeout: 45000 })
    await expect(page.locator('body')).not.toContainText(/traceback|Internal Server Error/i)
  })
})
