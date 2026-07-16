/**
 * Sequential mobile UI simulation — 30 client visits with button presses.
 * Includes cooldown between visits to reduce API 429s.
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const FRONT = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const __dirname = path.dirname(fileURLToPath(import.meta.url))

const PATHS = [
  '/book/package/classic-full-package',
  '/book/facials/deep-cleansing-facial',
  '/book/massage/back-neck-and-shoulders',
  '/book/waxing/brow-shaping',
  '/book/makeup/soft-glam',
  '/book/package/glow-package',
  '/services',
  '/',
  '/book/facials/hydrating-facial',
  '/book/package/relax-package',
]

const visits = Array.from({ length: 30 }, (_, i) => ({
  visit: i + 1,
  path: PATHS[i % PATHS.length],
  name: `Client${i + 1}`,
}))

async function waitForChips(page, seconds = 20) {
  const chips = page.locator('.flo-chip:not([disabled])')
  for (let t = 0; t < seconds; t++) {
    await page.waitForTimeout(1000)
    const n = await chips.count()
    if (n > 0) return n
    // Recover from throttle UX: Retry-After path exposes an actionable Retry CTA.
    if (t === 4 || t === 10) {
      const retry = page.getByRole('button', { name: /Retry availability/i })
      if (await retry.isVisible().catch(() => false)) {
        await retry.click().catch(() => {})
      }
    }
  }
  return 0
}

async function runVisit(browser, client) {
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
  })
  const page = await context.newPage()
  const steps = []
  const note = (step, ok, detail) => steps.push({ step, ok, detail })

  try {
    await page.goto(`${FRONT}${client.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 })
    await page.waitForTimeout(500)

    if (client.path === '/') {
      // SiteLoader clears is-loading after assets + minDuration (≤ ~2s; allow 5s headroom).
      await page.locator('.site-loader').waitFor({ state: 'detached', timeout: 5000 }).catch(() => {})
      await page.waitForFunction(
        () => !document.documentElement.classList.contains('is-loading'),
        { timeout: 5000 },
      ).catch(() => {})
      const stuck = await page.evaluate(() =>
        document.documentElement.classList.contains('is-loading'),
      )
      const heroVisible = await page
        .getByRole('heading', { name: 'Spa Beauty', level: 1 })
        .isVisible()
        .catch(() => false)
      const ctaVisible = await page
        .getByRole('link', { name: /Book your visit/i })
        .first()
        .isVisible()
        .catch(() => false)
      note(
        'home_gate',
        !stuck && heroVisible && ctaVisible,
        stuck ? 'stuck is-loading' : !heroVisible ? 'hero hidden' : ctaVisible ? 'ok' : 'cta hidden',
      )
    } else if (client.path === '/services') {
      await page.getByRole('tab', { name: /Facial/i }).first().click({ timeout: 10000 })
      await page.waitForTimeout(400)
      await page.getByRole('button', { name: /Deep cleansing facial/i }).click({ timeout: 10000 })
      note('select', true, 'deep cleansing')
      await page.getByRole('link', { name: /Book Deep cleansing facial/i }).click({ timeout: 10000 })
      await page.waitForURL((url) => url.pathname.includes('/book/'), { timeout: 15000 })
      note('book_cta', true, page.url())
    }

    if (page.url().includes('/book/')) {
      const n = await waitForChips(page, 12)
      if (!n) {
        const err = await page.locator('.book-error').innerText().catch(() => '')
        note('date_chip', false, err || 'no chips (load/429)')
      } else {
        await page.locator('.flo-chip:not([disabled])').first().click()
        note('date_chip', true, `${n} open`)
        await page.waitForTimeout(1500)
        const slots = page.locator('.flo-slots__btn')
        const sc = await slots.count()
        if (!sc) {
          note('time_slot', false, '0 slots')
        } else {
          await slots.nth(Math.min(4, sc - 1)).click()
          note('time_slot', true, `${sc} slots`)
          const cont = page.getByRole('button', { name: /Continue to checkout/i })
          if (await cont.isEnabled()) {
            await cont.click()
            note('continue', true, 'details')
            await page.waitForTimeout(800)
            const bar = page.locator('.mobile-book-bar')
            const back = page.getByRole('button', { name: /^Back$/i })
            const bb = await back.boundingBox().catch(() => null)
            const barb = await bar.boundingBox().catch(() => null)
            const covered = !!(bb && barb && bb.y + bb.height > barb.y)
            note('sticky_clash', !covered, covered ? 'book bar covers Back' : 'ok')
          } else {
            note('continue', false, 'disabled')
          }
        }
      }
    }

    await context.close()
    return { client, ok: steps.every((s) => s.ok), steps }
  } catch (err) {
    note('exception', false, String(err.message || err).slice(0, 180))
    await context.close().catch(() => {})
    return { client, ok: false, steps }
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true })
  const results = []

  for (const client of visits) {
    const result = await runVisit(browser, client)
    results.push(result)
    const bad = result.steps
      .filter((s) => !s.ok)
      .map((s) => `${s.step}:${s.detail}`)
      .join(' | ')
    console.log(
      `${result.ok ? 'OK  ' : 'FAIL'} #${String(client.visit).padStart(2, '0')} ${client.path} ${bad || 'pass'}`,
    )
    // Cool down between visits so shared-IP read throttles don't starve later clients.
    await new Promise((r) => setTimeout(r, 1200))
  }

  await browser.close()

  const summary = {
    total: results.length,
    ok: results.filter((r) => r.ok).length,
    fail: results.filter((r) => !r.ok).length,
    stepFails: {},
  }
  for (const r of results) {
    for (const s of r.steps) {
      if (!s.ok) summary.stepFails[s.step] = (summary.stepFails[s.step] || 0) + 1
    }
  }

  const out = path.join(__dirname, '../test-results/multi-client-ui-sim.json')
  fs.mkdirSync(path.dirname(out), { recursive: true })
  fs.writeFileSync(
    out,
    JSON.stringify({ generatedAt: new Date().toISOString(), front: FRONT, summary, visits: results }, null, 2),
  )

  console.log('\n=== UI MULTI-CLIENT SUMMARY ===')
  console.log(`Visits: ${summary.total} OK: ${summary.ok} FAIL: ${summary.fail}`)
  console.log('Step failures:', summary.stepFails)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
