import { chromium } from 'playwright'
import { mkdirSync, writeFileSync } from 'fs'

mkdirSync('test-results', { recursive: true })

const devices = [
  { name: 'iPhone12', w: 390, h: 844 },
  { name: 'iPad', w: 768, h: 1024 },
  { name: 'Desktop', w: 1440, h: 900 },
]

const draft = {
  type: 'package',
  plan: 'classic-full-package',
}

const browser = await chromium.launch({ headless: true })
const results = []

for (const d of devices) {
  const page = await browser.newPage({ viewport: { width: d.w, height: d.h } })
  await page.addInitScript((payload) => {
    try {
      localStorage.setItem('shee-loader-done', '1')
      sessionStorage.setItem('shee-loader-done', '1')
      localStorage.setItem('shee-last-book-handoff-v1', JSON.stringify(payload))
    } catch {
      /* ignore */
    }
  }, draft)
  await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(400)
  const m = await page.evaluate(() => {
    const welcome = document.querySelector('.welcome-back')
    const logo = [...document.querySelectorAll('.site-header__logo')].find(
      (el) => getComputedStyle(el).display !== 'none',
    )
    const header = document.querySelector('.site-header')
    const lr = logo?.getBoundingClientRect()
    const wr = welcome?.getBoundingClientRect()
    const headerBg = header ? getComputedStyle(header).backgroundColor : null
    const overHero = header?.classList.contains('site-header--over-hero')
    const whiteGhost = overHero && headerBg && headerBg.includes('255, 255, 255')
    const name = logo?.querySelector('.shee-logo__name')
    return {
      hasWelcome: !!welcome,
      welcomeOnHero: welcome?.classList.contains('welcome-back--hero') || false,
      welcomeText: welcome?.textContent?.replace(/\s+/g, ' ').trim(),
      welcomeTop: wr ? Math.round(wr.top) : null,
      welcomeW: wr ? Math.round(wr.width) : null,
      overlapsLogo:
        wr && lr
          ? !(
              wr.bottom <= lr.top ||
              wr.top >= lr.bottom ||
              wr.right <= lr.left ||
              wr.left >= lr.right
            )
          : false,
      logoColor: name ? getComputedStyle(name).color : null,
      headerBg,
      whiteGhostHeader: !!whiteGhost,
      overflowX:
        Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) -
        document.documentElement.clientWidth,
    }
  })
  const shot = `test-results/audit-${d.name}-welcome.png`
  await page.screenshot({ path: shot, fullPage: false })
  const pass =
    m.hasWelcome &&
    m.welcomeOnHero &&
    !m.whiteGhostHeader &&
    !m.overlapsLogo &&
    m.overflowX <= 1
  results.push({ device: d.name, pass, shot, ...m })
  await page.close()
}

{
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } })
  await page.addInitScript(() => {
    try {
      localStorage.removeItem('shee-loader-done')
      sessionStorage.removeItem('shee-loader-done')
    } catch {
      /* ignore */
    }
  })
  await page.goto('http://127.0.0.1:3000/', { waitUntil: 'domcontentloaded', timeout: 60000 })
  await page.waitForTimeout(80)
  const sk = await page.evaluate(() => {
    const loader = document.querySelector('.site-loader')
    return {
      loaderPresent: !!loader,
      loaderText: loader?.textContent?.replace(/\s+/g, ' ').trim().slice(0, 240) || null,
      classes: loader?.className || null,
      hasHero: !!loader?.querySelector('.site-loader__hero'),
      hasStudio: !!loader?.querySelector('[data-skel="studio"], .site-loader__studio'),
      sectionLabels: [...(loader?.querySelectorAll('[data-label], .site-loader__label') || [])]
        .map((el) => el.textContent?.trim())
        .filter(Boolean),
      htmlSnippet: loader?.innerHTML?.replace(/\s+/g, ' ').slice(0, 500) || null,
    }
  })
  await page.screenshot({ path: 'test-results/audit-skeleton.png', fullPage: false })
  results.push({ device: 'skeleton-390', pass: sk.loaderPresent, ...sk })
  await page.close()
}

await browser.close()
writeFileSync('test-results/responsive-welcome-audit.json', JSON.stringify(results, null, 2))
console.log(JSON.stringify(results, null, 2))
const failed = results.filter((r) => r.pass === false)
console.log(failed.length ? `FAIL ${failed.map((f) => f.device).join(',')}` : 'OK')
