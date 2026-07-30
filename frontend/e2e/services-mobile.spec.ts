import { test, expect } from '@playwright/test'

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000'
const MOBILE_VIEWPORT = { width: 390, height: 844 }

test.describe('Services page mobile UX', () => {
  test.use({ viewport: MOBILE_VIEWPORT })

  test('shows fixed book bar and readable hero on small screens', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    await expect(page.locator('.mobile-book-bar')).toBeVisible()
    await expect(page.getByRole('heading', { name: /How would you like to visit/i, level: 1 })).toBeVisible()
    await expect(page.getByRole('note', { name: 'Booking days' })).toBeVisible()
    await expect(page.locator('.services-chooser')).toBeVisible()
    await expect(page.locator('.services-hero__photo')).toBeVisible()
  })

  test('shows package and treatment path doors', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    const packagesDoor = page.locator('.services-door--packages')
    const treatmentsDoor = page.locator('.services-door--treatments')
    await expect(packagesDoor).toBeVisible()
    await expect(treatmentsDoor).toBeVisible()
    await expect(packagesDoor.getByText('Packages')).toBeVisible()
    await expect(treatmentsDoor.getByText('Treatments')).toBeVisible()

    const box = await packagesDoor.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
  })

  test('shows 2x2 category board under treatments header', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#single-sessions`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('heading', { name: /^Choose a treatment$/i })).toBeVisible()

    const board = page.getByRole('tablist', { name: 'Service categories' })
    await board.scrollIntoViewIfNeeded()
    const tabCols = await board.evaluate((el) => getComputedStyle(el).gridTemplateColumns)
    expect(tabCols.split(' ').length).toBe(2)

    const waxingTab = page.getByRole('tab', { name: /Waxing/i })
    const box = await waxingTab.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
    expect(box?.width ?? 0).toBeGreaterThanOrEqual(44)
  })

  test('treatment rows expose direct book links', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#waxing`, { waitUntil: 'networkidle' })

    const browRow = page.locator('.service-treatment').filter({ hasText: /Brow shaping/i }).first()
    await browRow.scrollIntoViewIfNeeded()
    await expect(browRow).toBeVisible()
    const bookLink = browRow.getByRole('link', { name: /^Book$/i })
    await expect(bookLink).toBeVisible()
    await expect(bookLink).toHaveAttribute('href', /\/book\//)
  })

  test('waxing tab deep-link selects the waxing category', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#waxing`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('tab', { name: /Waxing/i, selected: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Waxing/i, level: 2 })).toBeVisible()
  })

  test('path doors meet minimum touch height', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    const packagesDoor = page.locator('.services-door--packages')
    const box = await packagesDoor.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
  })
})
