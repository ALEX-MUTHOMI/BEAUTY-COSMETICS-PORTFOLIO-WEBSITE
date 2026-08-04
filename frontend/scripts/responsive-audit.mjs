import { chromium } from 'playwright'

const devices = [
  { name: 'iPhone SE', w: 375, h: 667 },
  { name: 'iPhone 12', w: 390, h: 844 },
  { name: 'Pixel 7', w: 412, h: 915 },
  { name: 'iPad', w: 768, h: 1024 },
  { name: 'iPad landscape', w: 1024, h: 768 },
  { name: 'Desktop', w: 1440, h: 900 },
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

  const metrics = await page.evaluate(() => {
    const header = document.querySelector('.site-header')
    const logo = [...document.querySelectorAll('.site-header__logo')].find(
      (el) => getComputedStyle(el).display !== 'none',
    )
    const welcome = document.querySelector('.welcome-back')
    const heroCta = document.querySelector('.hero__cta')
    const bookBar = document.querySelector('.mobile-book-bar')
    const nav = document.querySelector('.site-header__nav')
    const menu = document.querySelector('.site-header__menu-toggle')
    const hr = header?.getBoundingClientRect()
    const lr = logo?.getBoundingClientRect()
    const wr = welcome?.getBoundingClientRect()
    const logoName = logo?.querySelector('.shee-logo__name')
    const logoColor = logoName
      ? getComputedStyle(logoName).color
      : logo
        ? getComputedStyle(logo).color
        : null
    const headerBg = header ? getComputedStyle(header).backgroundColor : null
    const overHero = header?.classList.contains('site-header--over-hero') ?? false
    const whiteGhostHeader =
      overHero &&
      !!headerBg &&
      (headerBg.includes('255, 255, 255') || headerBg === 'rgb(255, 255, 255)')

    return {
      overflowX:
        Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) -
        document.documentElement.clientWidth,
      headerH: hr ? Math.round(hr.height) : null,
      logoVisible: !!(lr && lr.width > 20 && lr.height > 10),
      logoColor,
      headerBg,
      overHero,
      welcomeOnHero: welcome?.classList.contains('welcome-back--overlay') || false,
      welcomeTop: wr ? Math.round(wr.top) : null,
      welcomeOverlapsLogo:
        wr && lr
          ? !(
              wr.bottom <= lr.top ||
              wr.top >= lr.bottom ||
              wr.right <= lr.left ||
              wr.left >= lr.right
            )
          : false,
      heroCtaDisplay: heroCta ? getComputedStyle(heroCta).display : null,
      bookBarDisplay: bookBar ? getComputedStyle(bookBar).display : null,
      navDisplay: nav ? getComputedStyle(nav).display : null,
      menuDisplay: menu ? getComputedStyle(menu).display : null,
      whiteGhostHeader,
    }
  })

  const pass =
    metrics.overflowX <= 1 &&
    metrics.logoVisible &&
    !metrics.whiteGhostHeader &&
    !(metrics.welcomeOnHero && metrics.welcomeOverlapsLogo)

  results.push({ device: d.name, w: d.w, h: d.h, pass, ...metrics })
  await page.close()
}

await browser.close()
console.log(JSON.stringify(results, null, 2))
const failed = results.filter((r) => !r.pass)
console.log(failed.length ? `FAIL ${failed.map((f) => f.device).join(',')}` : 'ALL_PASS')
