import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'

test.describe('Book page handoff security', () => {
  test('accepts allowlisted package params and shows selection', async ({ page }) => {
    await page.goto(`${BASE_URL}/book?type=package&plan=classic-full-package`, {
      waitUntil: 'networkidle',
    })

    await expect(page.getByRole('heading', { name: /Choose your date/i })).toBeVisible()
    await expect(page.getByText('Classic Full Package')).toBeVisible()
    await expect(page.getByLabel('Preferred visit date')).toBeVisible()
  })

  test('accepts allowlisted single treatment params', async ({ page }) => {
    await page.goto(
      `${BASE_URL}/book?type=single&category=waxing&treatment=brow-shaping`,
      { waitUntil: 'networkidle' },
    )

    await expect(page.getByText('Brow shaping')).toBeVisible()
    await expect(page.getByText(/Single treatment/i)).toBeVisible()
  })

  test('rejects malicious query params without rendering attacker strings', async ({ page }) => {
    const dialogFired: string[] = []
    page.on('dialog', async (dialog) => {
      dialogFired.push(dialog.message())
      await dialog.dismiss()
    })

    await page.goto(
      `${BASE_URL}/book?type=<script>alert(1)</script>&plan=classic-full-package`,
      { waitUntil: 'networkidle' },
    )

    expect(dialogFired).toHaveLength(0)
    await expect(page.getByRole('heading', { name: /Book your visit/i })).toBeVisible()
    await expect(page.getByText('<script>')).toHaveCount(0)
  })

  test('shows closed package days in calendar (Monday not selectable)', async ({ page }) => {
    await page.goto(
      `${BASE_URL}/book?type=package&plan=classic-full-package`,
      { waitUntil: 'networkidle' },
    )

    await expect(page.getByRole('group', { name: 'Choose your visit date' })).toBeVisible()
    const mondayCell = page.getByRole('button', { name: /Monday.*not available/i }).first()
    await expect(mondayCell).toBeDisabled()
  })

  test('services package CTA links to allowlisted book URL', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#full-packages`, { waitUntil: 'networkidle' })

    const bookLink = page
      .locator('#full-packages')
      .getByRole('link', { name: /Book your visit/i })
      .first()
    await expect(bookLink).toHaveAttribute(
      'href',
      '/book?type=package&plan=classic-full-package',
    )
  })

  test('serves strict security headers on book page', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/book`)
    expect(response.ok()).toBeTruthy()

    const csp = response.headers()['content-security-policy'] || ''
    expect(csp).toContain('script-src')
    expect(csp).not.toMatch(/script-src[^;]*unsafe-inline/)
    expect(response.headers()['x-frame-options']?.toUpperCase()).toBe('DENY')
  })
})
