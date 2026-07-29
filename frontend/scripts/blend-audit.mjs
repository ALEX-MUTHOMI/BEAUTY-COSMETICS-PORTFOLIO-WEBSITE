import { chromium } from 'playwright'
import { mkdirSync, writeFileSync } from 'fs'

mkdirSync('test-results', { recursive: true })

const devices = [
  { name: 'mobile-390', w: 390, h: 844 },
  { name: 'tablet-768', w: 768, h: 1024 },
  { name: 'desktop-1440', w: 1440, h: 900 },
]

const browser = await chromium.launch({ headless: true })
const results = []

for (const d of devices) {
  const page = await browser.newPage({ viewport: { width: d.w, height: d.h } })
  await page.addInitScript(() => {
    try {
      localStorage.setItem('shee-loader-done', '1')
      sessionStorage.setItem('shee-loader-done', '1')
    } catch {
      /* ignore */
    }
  })
  await page.goto('http://127.0.0.1:3000/', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(500)

  const metrics = await page.evaluate(() => {
    const root = getComputedStyle(document.documentElement)
    const paper = root.getPropertyValue('--color-paper').trim()
    const cardDark = root.getPropertyValue('--color-card-dark').trim()
    const parchment = root.getPropertyValue('--color-parchment').trim()
    const raised = root.getPropertyValue('--color-surface-raised').trim()

    const offer = document.querySelector('.offer')
    const packages = document.querySelector('#packages, .book-visit__stage')
    const path = document.querySelector('.book-visit__path')
    const card = document.querySelector('.mellis-card')
    const atmospheres = {
      offerFixed: !!document.querySelector('.offer__fixed'),
      packagesAtm: !!document.querySelector('.mellis-cta__atmosphere'),
      visitAtm: !!document.querySelector('.book-visit__atmosphere'),
    }

    const box = (el) => {
      if (!el) return null
      const s = getComputedStyle(el)
      return {
        bg: s.backgroundColor,
        bgImage: s.backgroundImage === 'none' ? 'none' : 'set',
      }
    }

    return {
      tokens: { paper, cardDark, parchment, raised },
      atmospheres,
      offer: box(offer),
      path: box(path),
      packages: box(packages),
      card: box(card),
      overflowX:
        Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) -
        document.documentElement.clientWidth,
    }
  })

  await page.locator('#packages, .book-visit__stage').first().scrollIntoViewIfNeeded()
  await page.waitForTimeout(200)
  await page.screenshot({ path: `test-results/blend-${d.name}-packages.png`, fullPage: false })

  await page.locator('.offer').first().scrollIntoViewIfNeeded()
  await page.waitForTimeout(200)
  await page.screenshot({ path: `test-results/blend-${d.name}-offer.png`, fullPage: false })

  await page.goto('http://127.0.0.1:3000/services', { waitUntil: 'networkidle', timeout: 60000 })
  await page.waitForTimeout(300)
  const servicesBg = await page.evaluate(() => {
    const pageEl = document.querySelector('.services-page')
    const card = document.querySelector('.mellis-card')
    return {
      pageBg: pageEl ? getComputedStyle(pageEl).backgroundColor : null,
      cardBg: card ? getComputedStyle(card).backgroundColor : null,
      paper: getComputedStyle(document.documentElement).getPropertyValue('--color-paper').trim(),
    }
  })
  await page.screenshot({ path: `test-results/blend-${d.name}-services.png`, fullPage: false })

  const pass =
    metrics.tokens.paper === '#f3eee9' &&
    metrics.tokens.cardDark === '#171516' &&
    !metrics.atmospheres.offerFixed &&
    !metrics.atmospheres.packagesAtm &&
    !metrics.atmospheres.visitAtm &&
    metrics.overflowX <= 1 &&
    !!metrics.card

  results.push({ device: d.name, pass, ...metrics, servicesBg })
  await page.close()
}

await browser.close()
writeFileSync('test-results/blend-audit.json', JSON.stringify(results, null, 2))
console.log(JSON.stringify(results, null, 2))
console.log(results.every((r) => r.pass) ? 'ALL_PASS' : 'FAIL')
