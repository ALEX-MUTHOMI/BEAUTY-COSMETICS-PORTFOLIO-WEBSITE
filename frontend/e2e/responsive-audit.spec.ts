import { test, expect } from '@playwright/test'

const DEVICE_VIEWPORTS = [
  { name: 'Samsung Galaxy S20 (360px)', width: 360, height: 800 },
  { name: 'iPhone SE (375px)', width: 375, height: 667 },
  { name: 'iPhone 14 / 15 Pro (393px)', width: 393, height: 852 },
  { name: 'iPhone 15 Pro Max (430px)', width: 430, height: 932 },
  { name: 'iPad Air (820px)', width: 820, height: 1180 },
  { name: 'iPad Pro 11 (834px)', width: 834, height: 1194 },
  { name: 'Small Laptop (1280px)', width: 1280, height: 800 },
  { name: 'Desktop HD (1440px)', width: 1440, height: 900 },
  { name: 'Desktop UltraWide (1920px)', width: 1920, height: 1080 },
]

test.describe('Mobile-First & Cross-Device Responsive Audit', () => {
  for (const vp of DEVICE_VIEWPORTS) {
    test(`Landing Page & Spotlight section at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded' })

      // Wait for Nuxt app hydration & loader dismissal
      await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 7000 })

      // 1. Verify No Horizontal Overflow
      const overflow = await page.evaluate(() => {
        return {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        }
      })
      expect(overflow.hasHorizontalOverflow, `Horizontal scroll overflow detected at ${vp.name}: scrollWidth=${overflow.scrollWidth}, clientWidth=${overflow.clientWidth}`).toBe(false)

      // 2. Verify Therapist Spotlight Section (#behind-the-glow)
      const spotlight = page.locator('#behind-the-glow')
      await expect(spotlight).toBeVisible()

      const photo = spotlight.locator('.glow__photo')
      await expect(photo).toBeVisible()

      const mirror = spotlight.locator('.glow__mirror')
      await expect(mirror).toBeVisible()

      // Verify photo image bounding box fits inside viewport without overflow
      const mirrorBox = await mirror.boundingBox()
      expect(mirrorBox).not.toBeNull()
      if (mirrorBox) {
        expect(mirrorBox.width).toBeLessThanOrEqual(vp.width)
        expect(mirrorBox.x).toBeGreaterThanOrEqual(-1)
      }

      // Verify botanical flower sketch & accent circle
      await expect(spotlight.locator('.glow__flower-sketch')).toBeVisible()
      await expect(spotlight.locator('.glow__accent-circle')).toBeVisible()

      // Verify copy elements
      await expect(spotlight.locator('.glow__heading')).toBeVisible()
      await expect(spotlight.locator('.glow__continue')).toBeVisible()
    })

    test(`Services Page at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await page.goto('http://localhost:3000/services', { waitUntil: 'domcontentloaded' })

      await expect(page.locator('.site-boot-skeleton, .site-loader')).toHaveCount(0, { timeout: 7000 })

      // Verify No Horizontal Overflow on Services Page
      const overflow = await page.evaluate(() => {
        return {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
          hasHorizontalOverflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        }
      })
      expect(overflow.hasHorizontalOverflow, `Horizontal overflow on /services at ${vp.name}`).toBe(false)
    })
  }
})
