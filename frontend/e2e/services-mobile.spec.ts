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
  })

  test('uses single-column package grids and 2x2 category tabs', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#single-sessions`, { waitUntil: 'networkidle' })

    const singlesGrid = page.locator('.services-packages__grid--singles')
    await singlesGrid.scrollIntoViewIfNeeded()
    const gridCols = await singlesGrid.evaluate((el) => getComputedStyle(el).gridTemplateColumns)
    expect(gridCols.split(' ').length).toBe(1)

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

  test('single card details link opens allowlisted waxing tab', async ({ page }) => {
    await page.goto(`${BASE_URL}/services#single-sessions`, { waitUntil: 'networkidle' })

    const waxingCard = page.locator('.mellis-card').filter({
      has: page.getByRole('heading', { name: 'Waxing', level: 3 }),
    })
    await waxingCard.getByRole('link', { name: /See all options and prices/i }).click()
    await expect(page).toHaveURL(/#waxing/)
    await expect(page.getByRole('tab', { name: 'Waxing', selected: true })).toBeVisible()
  })

  test('path cards meet minimum touch height', async ({ page }) => {
    await page.goto(`${BASE_URL}/services`, { waitUntil: 'networkidle' })

    const fullPackagePath = page.getByRole('link', { name: /Full package/i })
    const box = await fullPackagePath.boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(52)
  })
})
