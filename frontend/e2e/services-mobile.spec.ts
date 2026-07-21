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
  })

  test('keeps both path tiles in the first viewport', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    const fullPackage = page.getByRole('link', { name: /Package/i }).first()
    const single = page.getByRole('link', { name: /^Singles/i })
    await expect(fullPackage).toBeVisible()
    await expect(single).toBeVisible()

    const viewport = page.viewportSize()
    expect(viewport).toBeTruthy()
    const fullBox = await fullPackage.boundingBox()
    const singleBox = await single.boundingBox()
    expect(fullBox).toBeTruthy()
    expect(singleBox).toBeTruthy()

    // Side-by-side tiles: both visible without scrolling past a full-screen first card
    expect(fullBox!.y + fullBox!.height).toBeLessThanOrEqual(viewport!.height)
    expect(singleBox!.y + singleBox!.height).toBeLessThanOrEqual(viewport!.height)
    expect(Math.abs(fullBox!.y - singleBox!.y)).toBeLessThan(24)
    expect(fullBox!.height).toBeGreaterThanOrEqual(44)
    expect(singleBox!.height).toBeGreaterThanOrEqual(44)
  })

  test('shows 2x2 category tabs under a single singles header', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#single-sessions`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('heading', { name: /^Select a treatment$/i })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Pick your exact treatment/i })).toHaveCount(0)

    const tabs = page.getByRole('tablist', { name: 'Service categories' })
    await tabs.scrollIntoViewIfNeeded()
    const tabCols = await tabs.evaluate((el) => getComputedStyle(el).gridTemplateColumns)
    expect(tabCols.split(' ').length).toBe(2)

    const waxingTab = page.getByRole('tab', { name: 'Waxing' })
    const box = await waxingTab.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
    expect(box?.width ?? 0).toBeGreaterThanOrEqual(44)
  })

  test('tapping a treatment selects it and enables the book CTA', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#waxing`, { waitUntil: 'networkidle' })

    const firstTreatment = page.getByRole('button', { name: /Brow shaping/i }).first()
    await firstTreatment.scrollIntoViewIfNeeded()
    await firstTreatment.click()

    await expect(page.getByText(/You selected/i)).toBeVisible()
    await expect(page.locator('.services-panel__book--ready')).toBeVisible()
  })

  test('waxing tab deep-link selects the waxing category', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#waxing`, { waitUntil: 'networkidle' })

    await expect(page.getByRole('tab', { name: 'Waxing', selected: true })).toBeVisible()
    await expect(page.getByRole('heading', { name: /Waxing/i, level: 2 })).toBeVisible()
  })

  test('path tiles meet minimum touch height', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    const fullPackagePath = page.getByRole('link', { name: /Full package/i })
    const box = await fullPackagePath.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
  })
})
