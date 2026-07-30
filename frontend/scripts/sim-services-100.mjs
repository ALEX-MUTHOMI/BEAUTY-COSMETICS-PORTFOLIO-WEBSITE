/**
 * 100-client services-page UX simulation.
 *
 * Models real client desires: flexibility (path choice, category switch,
 * deep-link resume) and easy booking (one-tap Book → /book/{...} with slots).
 *
 * Layer A — SSR/API scale (100 clients): catalog integrity + resolve→slots.
 * Layer B — Playwright mobile sample (12 clients): real taps on /services.
 *
 * Does NOT fire STK. Run: node scripts/sim-services-100.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const FRONT = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const API = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'
const TOTAL = Number(process.env.SIM_CLIENTS || 100)
const CONCURRENCY = Number(process.env.SIM_CONCURRENCY || 4)
const UI_SAMPLE = Number(process.env.SIM_UI_SAMPLE || 12)
const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** Intent mix: what clients arrive wanting. */
const INTENT_MIX = [
  { intent: 'package_full', weight: 28, pathPref: 'packages' },
  { intent: 'treatment_known', weight: 32, pathPref: 'treatments' },
  { intent: 'browsing', weight: 22, pathPref: 'either' },
  { intent: 'returning_resume', weight: 18, pathPref: 'deep' },
]

const PACKAGE_TARGETS = [
  {
    name: 'Classic Full Package',
    bookPath: '/book/package/classic-full-package',
    handoff: { type: 'package', plan: 'classic-full-package' },
  },
  {
    name: 'Glow Package',
    bookPath: '/book/package/glow-package',
    handoff: { type: 'package', plan: 'glow-package' },
  },
  {
    name: 'Relax Package',
    bookPath: '/book/package/relax-package',
    handoff: { type: 'package', plan: 'relax-package' },
  },
]

const TREATMENT_TARGETS = [
  {
    category: 'facials',
    name: 'Deep cleansing facial',
    tab: /Facial/i,
    bookPath: '/book/facials/deep-cleansing-facial',
    handoff: { type: 'single', category: 'facials', treatment: 'deep-cleansing-facial' },
  },
  {
    category: 'massage',
    name: 'Back, neck & shoulders',
    tab: /Massage/i,
    bookPath: '/book/massage/back-neck-and-shoulders',
    handoff: { type: 'single', category: 'massage', treatment: 'back-neck-and-shoulders' },
  },
  {
    category: 'waxing',
    name: 'Brow shaping',
    tab: /Waxing/i,
    bookPath: '/book/waxing/brow-shaping',
    handoff: { type: 'single', category: 'waxing', treatment: 'brow-shaping' },
  },
  {
    category: 'makeup',
    name: 'Soft glam',
    tab: /Makeup/i,
    bookPath: '/book/makeup/soft-glam',
    handoff: { type: 'single', category: 'makeup', treatment: 'soft-glam' },
  },
]

function buildClients(n) {
  const clients = []
  let id = 1
  for (const row of INTENT_MIX) {
    const count = Math.round((row.weight / 100) * n)
    for (let i = 0; i < count; i++) {
      let target
      if (row.pathPref === 'packages') {
        target = { kind: 'package', ...PACKAGE_TARGETS[id % PACKAGE_TARGETS.length] }
      } else if (row.pathPref === 'treatments' || row.pathPref === 'deep') {
        target = { kind: 'treatment', ...TREATMENT_TARGETS[id % TREATMENT_TARGETS.length] }
      } else {
        target =
          id % 2 === 0
            ? { kind: 'package', ...PACKAGE_TARGETS[id % PACKAGE_TARGETS.length] }
            : { kind: 'treatment', ...TREATMENT_TARGETS[id % TREATMENT_TARGETS.length] }
      }
      clients.push({
        id,
        name: `${row.intent}-${id}`,
        intent: row.intent,
        pathPref: row.pathPref,
        target,
        entry:
          row.intent === 'returning_resume'
            ? `/services#${target.kind === 'treatment' ? target.category : 'full-packages'}`
            : row.intent === 'package_full'
              ? '/services#full-packages'
              : row.intent === 'treatment_known'
                ? `/services#${target.category}`
                : '/services',
      })
      id += 1
    }
  }
  while (clients.length < n) {
    const t = TREATMENT_TARGETS[0]
    clients.push({
      id: clients.length + 1,
      name: `fill-${clients.length + 1}`,
      intent: 'browsing',
      pathPref: 'either',
      target: { kind: 'treatment', ...t },
      entry: '/services',
    })
  }
  return clients.slice(0, n)
}

async function fetchText(url) {
  const started = Date.now()
  try {
    const res = await fetch(url, { redirect: 'follow' })
    const text = await res.text()
    return { ok: res.ok, status: res.status, ms: Date.now() - started, text, finalUrl: res.url }
  } catch (err) {
    return { ok: false, status: 0, ms: Date.now() - started, text: '', error: String(err?.message || err) }
  }
}

async function fetchJson(url) {
  const started = Date.now()
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' } })
    const text = await res.text()
    let json = null
    try {
      json = JSON.parse(text)
    } catch {
      /* ignore */
    }
    return { ok: res.ok, status: res.status, ms: Date.now() - started, json, text }
  } catch (err) {
    return { ok: false, status: 0, ms: Date.now() - started, json: null, error: String(err?.message || err) }
  }
}

function qs(params) {
  return new URLSearchParams(params).toString()
}

/** One-shot services page flexibility / ease audit (SSR). */
function auditServicesHtml(html) {
  const bookHrefs = [...html.matchAll(/href="(\/book\/[^"]+)"/g)].map((m) => m[1])
  const uniqueBook = [...new Set(bookHrefs)]
  const packageBooks = uniqueBook.filter((h) => h.includes('/book/package/'))
  const treatmentBooks = uniqueBook.filter((h) => /\/book\/(facials|massage|waxing|makeup)\//.test(h))

  return {
    httpOk: true,
    hasQuestionHero: /How would you like to visit/i.test(html),
    jargonLeadGone: !/services-hero__lead/.test(html),
    hasPackagesDoor: /services-door--packages/.test(html),
    hasTreatmentsDoor: /services-door--treatments/.test(html),
    doorPhotoGone: !/services-door__media/.test(html),
    boardPhotoGone: !/services-board__photo/.test(html),
    hasCategoryIcons: /services-board__icon/.test(html) || /icon-facial\.png/.test(html),
    hasCategoryTabs: /role="tablist"/.test(html) || /Service categories/.test(html),
    categoryIds: ['facials', 'massage', 'waxing', 'makeup'].filter((id) => html.includes(`tab-${id}`) || html.includes(`#${id}`)),
    bookDeepLinkCount: bookHrefs.length,
    uniqueBookHrefs: uniqueBook,
    packageBookCount: packageBooks.length,
    treatmentBookCount: treatmentBooks.length,
    hasDirectBookCta: /Book<\/|\bBook\b/.test(html) && uniqueBook.length > 0,
    hasStickyBookBar: /mobile-book-bar/.test(html),
    hasSiteLoader: /site-boot-skeleton|SiteLoader|site-loader/.test(html),
    resumeIsOverlayClass: true, // layout-owned; verified in UI layer
    scrollSnapDoors: /scroll-snap/.test(html) || /services-doors/.test(html),
    clutterDaysStrip: /Booking days|Pick your visit type/.test(html),
  }
}

async function runBookFunnel(target) {
  const funnel = {
    land_ok: false,
    resolve_ok: false,
    see_open_days: false,
    open_day_count: 0,
    see_slots: false,
    slot_count: 0,
    details_ready: false,
    throttled: false,
    fail_step: null,
    latencies: {},
  }

  const page = await fetchText(`${FRONT}${target.bookPath}`)
  funnel.latencies.page = page.ms
  if (!page.ok) {
    funnel.fail_step = 'page_load'
    return funnel
  }
  funnel.land_ok = true

  const handoffQ = { type: target.handoff.type }
  if (target.handoff.plan) handoffQ.plan = target.handoff.plan
  if (target.handoff.category) handoffQ.category = target.handoff.category
  if (target.handoff.treatment) handoffQ.treatment = target.handoff.treatment

  const resolved = await fetchJson(`${API}/api/bookings/catalog/resolve-handoff/?${qs(handoffQ)}`)
  funnel.latencies.resolve = resolved.ms
  if (resolved.status === 429) funnel.throttled = true
  const selection = resolved.json?.selection
  if (!resolved.ok || !selection?.public_id) {
    funnel.fail_step = 'resolve_handoff'
    return funnel
  }
  funnel.resolve_ok = true

  const calParams = { selection_type: selection.selection_type }
  if (selection.selection_type === 'full_package') {
    calParams.full_package_public_id = selection.public_id
  } else {
    calParams.service_public_id = selection.public_id
  }

  const calendar = await fetchJson(`${API}/api/bookings/calendar/?${qs(calParams)}`)
  funnel.latencies.calendar = calendar.ms
  if (calendar.status === 429) funnel.throttled = true
  const days = calendar.json?.calendar?.days || calendar.json?.days || []
  const openDays = days.filter((d) => {
    const s = String(d.status || '').toLowerCase()
    return s === 'available' || s === 'open' || d.available === true
  })
  funnel.open_day_count = openDays.length
  if (!calendar.ok || !days.length) {
    funnel.fail_step = 'calendar'
    return funnel
  }
  if (!openDays.length) {
    funnel.fail_step = 'no_open_days'
    return funnel
  }
  funnel.see_open_days = true

  const day = openDays[0]
  const slotsRes = await fetchJson(
    `${API}/api/bookings/availability/?${qs({ ...calParams, start_date: day.date, end_date: day.date })}`,
  )
  funnel.latencies.availability = slotsRes.ms
  if (slotsRes.status === 429) funnel.throttled = true

  let slots = []
  if (Array.isArray(slotsRes.json?.availability)) {
    slots = slotsRes.json.availability.flatMap((row) => (Array.isArray(row?.slots) ? row.slots : []))
  } else if (Array.isArray(slotsRes.json?.slots)) {
    slots = slotsRes.json.slots
  }
  funnel.slot_count = slots.length
  if (!slotsRes.ok) {
    funnel.fail_step = 'availability'
    return funnel
  }
  if (!slots.length) {
    funnel.fail_step = 'empty_slots'
    return funnel
  }
  funnel.see_slots = true

  const policy = await fetchJson(`${API}/api/bookings/policy-acceptance-text/`)
  funnel.latencies.policy = policy.ms
  const bookReload = await fetchText(`${FRONT}${target.bookPath}`)
  funnel.details_ready =
    policy.ok && bookReload.ok && /Continue to checkout/i.test(bookReload.text)
  if (!funnel.details_ready) funnel.fail_step = 'details_chrome'
  return funnel
}

async function runServicesLand(client, servicesAudit) {
  const page = await fetchText(`${FRONT}${client.entry}`)
  const landOk = page.ok && /How would you like to visit/i.test(page.text)
  const hasDoors = /services-door--packages/.test(page.text) && /services-door--treatments/.test(page.text)
  const targetHref = client.target.bookPath
  const hrefPresent = page.text.includes(targetHref) || servicesAudit.uniqueBookHrefs.includes(targetHref)
  // Flexibility: client can reach packages OR treatments from same page
  const flexiblePaths = hasDoors && servicesAudit.packageBookCount >= 1 && servicesAudit.treatmentBookCount >= 1
  // Ease: direct book href exists without intermediate quiz
  const easyBook = hrefPresent || servicesAudit.treatmentBookCount + servicesAudit.packageBookCount >= 4

  return {
    land_ok: landOk,
    flexible_paths: flexiblePaths,
    easy_book_surface: easyBook,
    target_href_on_page: hrefPresent,
    latencies: { services: page.ms },
    fail_step: !landOk ? 'services_land' : !flexiblePaths ? 'inflexible_paths' : null,
  }
}

async function runClient(client, servicesAudit) {
  const started = Date.now()
  const services = await runServicesLand(client, servicesAudit)
  const book = await runBookFunnel(client.target)

  const sawSlots = book.see_slots
  const payReady = sawSlots && book.details_ready && !book.throttled

  // Success = landed services with flexible choice + reached bookable slots for their desire
  const ok =
    services.land_ok &&
    services.flexible_paths &&
    book.land_ok &&
    book.see_open_days &&
    book.see_slots

  return {
    id: client.id,
    name: client.name,
    intent: client.intent,
    entry: client.entry,
    bookPath: client.target.bookPath,
    kind: client.target.kind,
    ok,
    services,
    book,
    metrics: {
      flexible: services.flexible_paths,
      easy_surface: services.easy_book_surface,
      saw_slots: sawSlots,
      pay_ready: payReady,
      throttled: book.throttled || false,
    },
    elapsedMs: Date.now() - started,
  }
}

async function mapPool(items, concurrency, worker) {
  const results = []
  let i = 0
  async function next() {
    while (i < items.length) {
      const idx = i++
      results[idx] = await worker(items[idx], idx)
      await new Promise((r) => setTimeout(r, 60))
    }
  }
  await Promise.all(Array.from({ length: concurrency }, () => next()))
  return results
}

function pct(n, d) {
  if (!d) return 0
  return Math.round((n / d) * 1000) / 10
}

function summarize(results, servicesAudit, uiSample) {
  const total = results.length
  const byIntent = {}
  for (const intent of INTENT_MIX.map((r) => r.intent)) {
    const rows = results.filter((r) => r.intent === intent)
    byIntent[intent] = {
      n: rows.length,
      ok: rows.filter((r) => r.ok).length,
      ok_pct: pct(rows.filter((r) => r.ok).length, rows.length),
      flexible: rows.filter((r) => r.metrics.flexible).length,
      saw_slots: rows.filter((r) => r.metrics.saw_slots).length,
      pay_ready: rows.filter((r) => r.metrics.pay_ready).length,
      throttled: rows.filter((r) => r.metrics.throttled).length,
    }
  }

  const ok = results.filter((r) => r.ok).length
  const flexible = results.filter((r) => r.metrics.flexible).length
  const easy = results.filter((r) => r.metrics.easy_surface).length
  const sawSlots = results.filter((r) => r.metrics.saw_slots).length
  const payReady = results.filter((r) => r.metrics.pay_ready).length
  const throttled = results.filter((r) => r.metrics.throttled).length

  const failSteps = {}
  for (const r of results) {
    const step = r.book.fail_step || r.services.fail_step
    if (step) failSteps[step] = (failSteps[step] || 0) + 1
  }

  const latencies = []
  for (const r of results) {
    for (const v of Object.values({ ...r.services.latencies, ...r.book.latencies })) {
      if (typeof v === 'number') latencies.push(v)
    }
  }
  latencies.sort((a, b) => a - b)
  const p50 = latencies[Math.floor(latencies.length * 0.5)] || 0
  const p95 = latencies[Math.floor(latencies.length * 0.95)] || 0

  /** Product gates for “flexible + easy booking” on services. */
  const gates = {
    flexible_paths_target: 95,
    flexible_paths_actual: pct(flexible, total),
    flexible_paths_pass: pct(flexible, total) >= 95,
    easy_book_surface_target: 90,
    easy_book_surface_actual: pct(easy, total),
    easy_book_surface_pass: pct(easy, total) >= 90,
    see_slots_target: 70,
    see_slots_actual: pct(sawSlots, total),
    see_slots_pass: pct(sawSlots, total) >= 70,
    pay_ready_target: 28,
    pay_ready_actual: pct(payReady, total),
    pay_ready_pass: pct(payReady, total) >= 28,
    low_jargon: servicesAudit.jargonLeadGone && !servicesAudit.clutterDaysStrip,
    no_photo_noise: servicesAudit.doorPhotoGone && servicesAudit.boardPhotoGone,
    dual_path_doors: servicesAudit.hasPackagesDoor && servicesAudit.hasTreatmentsDoor,
    deep_book_links: servicesAudit.uniqueBookHrefs.length >= 5,
  }

  return {
    total,
    ok,
    ok_pct: pct(ok, total),
    funnel: {
      flexible,
      flexible_pct: pct(flexible, total),
      easy_surface: easy,
      easy_surface_pct: pct(easy, total),
      saw_slots: sawSlots,
      saw_slots_pct: pct(sawSlots, total),
      pay_ready: payReady,
      pay_ready_pct: pct(payReady, total),
      throttled,
      throttled_pct: pct(throttled, total),
    },
    gates,
    byIntent,
    failSteps,
    latency: { p50, p95, samples: latencies.length },
    servicesAudit,
    uiSample,
  }
}

async function runUiSample(clients) {
  const sample = clients.slice(0, UI_SAMPLE)
  const results = []
  let browser
  try {
    browser = await chromium.launch({ headless: true })
  } catch (err) {
    return {
      skipped: true,
      reason: String(err?.message || err),
      n: 0,
      ok: 0,
      visits: [],
    }
  }

  for (const client of sample) {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
    })
    const page = await context.newPage()
    const steps = []
    const note = (step, ok, detail) => steps.push({ step, ok, detail })
    const started = Date.now()

    try {
      await page.goto(`${FRONT}${client.entry}`, { waitUntil: 'domcontentloaded', timeout: 35000 })
      await page.locator('.site-loader').waitFor({ state: 'detached', timeout: 6000 }).catch(() => {})
      await page.waitForFunction(
        () => !document.documentElement.classList.contains('is-loading'),
        { timeout: 6000 },
      ).catch(() => {})

      const hero = await page
        .getByRole('heading', { name: /How would you like to visit/i, level: 1 })
        .isVisible()
        .catch(() => false)
      note('hero', hero, hero ? 'question visible' : 'missing h1')

      const doors = page.locator('.services-door')
      const doorCount = await doors.count()
      note('doors', doorCount >= 2, `${doorCount} doors`)

      const overflowX = await page.locator('.services-doors').evaluate((el) => getComputedStyle(el).overflowX)
      note('mobile_scroll_doors', /auto|scroll/.test(overflowX), overflowX)

      const resume = page.locator('.welcome-back--overlay')
      const resumeCount = await resume.count()
      if (resumeCount) {
        const pos = await resume.evaluate((el) => getComputedStyle(el).position)
        note('resume_overlay', pos === 'fixed', pos)
      } else {
        note('resume_overlay', true, 'not present (no prior booking)')
      }

      if (client.target.kind === 'package') {
        await page.locator('.services-door--packages').click({ timeout: 8000 })
        await page.waitForTimeout(400)
        const bookPkg = page.getByRole('link', { name: /Book this package/i }).first()
        await bookPkg.scrollIntoViewIfNeeded()
        const visible = await bookPkg.isVisible().catch(() => false)
        note('package_book_visible', visible, visible ? 'ok' : 'missing')
        if (visible) {
          await bookPkg.click({ timeout: 10000 })
          await page.waitForURL((url) => url.pathname.includes('/book/'), { timeout: 15000 })
          note('reached_book', page.url().includes('/book/'), page.url())
        }
      } else {
        const tab = page.getByRole('tab', { name: client.target.tab }).first()
        await tab.scrollIntoViewIfNeeded()
        await tab.click({ timeout: 10000 })
        await page.waitForTimeout(350)
        const selected = await tab.getAttribute('aria-selected')
        note('category_tab', selected === 'true', client.target.category)

        const boardOverflow = await page
          .locator('.services-board')
          .evaluate((el) => getComputedStyle(el).overflowX)
        note('mobile_scroll_board', /auto|scroll/.test(boardOverflow), boardOverflow)

        const photoNoise = await page.locator('.services-board__photo, .services-panel__photo').count()
        note('no_photo_noise', photoNoise === 0, `${photoNoise} photos`)

        const row = page.locator('.service-treatment').filter({ hasText: new RegExp(client.target.name, 'i') }).first()
        await row.scrollIntoViewIfNeeded()
        const bookLink = row.getByRole('link', { name: /^Book$/i })
        const bookVisible = await bookLink.isVisible().catch(() => false)
        note('row_book', bookVisible, client.target.name)
        if (bookVisible) {
          await bookLink.click({ timeout: 10000 })
          await page.waitForURL((url) => url.pathname.includes('/book/'), { timeout: 15000 })
          note('reached_book', page.url().includes('/book/'), page.url())
        }
      }

      if (page.url().includes('/book/')) {
        const chips = page.locator('.flo-chip:not([disabled])')
        let n = 0
        for (let t = 0; t < 12; t++) {
          await page.waitForTimeout(800)
          n = await chips.count()
          if (n > 0) break
          if (t === 3 || t === 7) {
            const retry = page.getByRole('button', { name: /Retry availability/i })
            if (await retry.isVisible().catch(() => false)) await retry.click().catch(() => {})
          }
        }
        note('date_chips', n > 0, n ? `${n} open` : 'none')
        if (n > 0) {
          await chips.first().click()
          await page.waitForTimeout(1200)
          const slots = page.locator('.flo-slots__btn')
          const sc = await slots.count()
          note('time_slots', sc > 0, `${sc} slots`)
          if (sc > 0) {
            await slots.first().click()
            const cont = page.getByRole('button', { name: /Continue to checkout/i })
            const enabled = await cont.isEnabled().catch(() => false)
            note('continue_enabled', enabled, enabled ? 'pay-ready chrome' : 'disabled')
          }
        }
      }
    } catch (err) {
      note('exception', false, String(err?.message || err).slice(0, 180))
    }

    const ok = steps.filter((s) => s.ok).length >= Math.max(3, steps.length - 1) && steps.some((s) => s.step === 'reached_book' && s.ok)
    results.push({
      id: client.id,
      intent: client.intent,
      entry: client.entry,
      ok,
      elapsedMs: Date.now() - started,
      steps,
    })
    await context.close()
    await new Promise((r) => setTimeout(r, 200))
  }

  await browser.close()
  return {
    skipped: false,
    n: results.length,
    ok: results.filter((r) => r.ok).length,
    ok_pct: pct(results.filter((r) => r.ok).length, results.length),
    visits: results,
  }
}

// --- main ---
const servicesPage = await fetchText(`${FRONT}/services`)
if (!servicesPage.ok) {
  console.error('Services unreachable', servicesPage.status, servicesPage.error)
  process.exit(2)
}
const servicesAudit = auditServicesHtml(servicesPage.text)
servicesAudit.servicesMs = servicesPage.ms

const clients = buildClients(TOTAL)
console.log(`Services UX sim n=${clients.length} FRONT=${FRONT} API=${API} concurrency=${CONCURRENCY} uiSample=${UI_SAMPLE}`)
const started = Date.now()
const results = await mapPool(clients, CONCURRENCY, (c) => runClient(c, servicesAudit))
console.log('Layer A (SSR+API) done — starting Layer B (Playwright mobile sample)…')
const uiSample = await runUiSample(clients)
const summary = summarize(results, servicesAudit, {
  skipped: uiSample.skipped,
  reason: uiSample.reason,
  n: uiSample.n,
  ok: uiSample.ok,
  ok_pct: uiSample.ok_pct,
})

/** Engineer findings derived from gates + fail steps. */
const findings = []
if (!summary.gates.dual_path_doors) {
  findings.push({
    severity: 'P0',
    area: 'Flexibility',
    finding: 'Packages / Treatments path doors missing from services SSR.',
    action: 'Restore twin doors so clients can choose visit type in one tap.',
  })
}
if (!summary.gates.low_jargon) {
  findings.push({
    severity: 'P1',
    area: 'Ease',
    finding: 'Jargon / day strips still present in hero.',
    action: 'Keep hero to question + cards only.',
  })
}
if (!summary.gates.no_photo_noise) {
  findings.push({
    severity: 'P1',
    area: 'Ease',
    finding: 'Photo-heavy category/door media still in SSR.',
    action: 'Prefer icon/typography cards; clients already know the service.',
  })
}
if (!summary.gates.deep_book_links) {
  findings.push({
    severity: 'P0',
    area: 'Ease',
    finding: `Only ${servicesAudit.uniqueBookHrefs.length} unique /book deep links on services.`,
    action: 'Every package + treatment row must deep-link to /book/...',
  })
}
if (!summary.gates.see_slots_pass) {
  findings.push({
    severity: 'P0',
    area: 'Booking completion',
    finding: `Only ${summary.funnel.saw_slots_pct}% of clients saw open slots (target ≥70%).`,
    action: 'Investigate calendar/availability for empty days and 429s.',
  })
}
if (summary.funnel.throttled_pct > 5) {
  findings.push({
    severity: 'P1',
    area: 'Reliability',
    finding: `${summary.funnel.throttled_pct}% hit API throttle during sim.`,
    action: 'Backoff + Retry UX on book calendar; raise burst allowance for browse.',
  })
}
if (uiSample.skipped) {
  findings.push({
    severity: 'P2',
    area: 'Coverage',
    finding: `Playwright UI sample skipped: ${uiSample.reason}`,
    action: 'Run npx playwright install chromium and re-sim.',
  })
} else if ((uiSample.ok_pct || 0) < 75) {
  findings.push({
    severity: 'P0',
    area: 'Mobile interaction',
    finding: `UI sample success ${uiSample.ok_pct}% (n=${uiSample.n}).`,
    action: 'Fix tap path: doors → category → row Book → /book chips.',
  })
}
if (!findings.length) {
  findings.push({
    severity: 'OK',
    area: 'Services UX',
    finding: 'Gates passed for flexible dual-path + easy deep-link booking at simulated load.',
    action: 'Monitor slot fill rate and keep resume as overlay.',
  })
}

const report = {
  generatedAt: new Date().toISOString(),
  title: 'Shee Aesthetics — 100-client services booking UX simulation',
  thesis:
    'A client on /services needs flexibility (packages vs treatments, category switch, deep-link entry) and an easy time booking (one-tap Book → open slots → continue). This sim measures both.',
  front: FRONT,
  api: API,
  elapsedMs: Date.now() - started,
  concurrency: CONCURRENCY,
  method:
    'Layer A: SSR services audit + 100× resolve→calendar→availability (no STK). Layer B: Playwright mobile taps on a client sample.',
  summary,
  findings,
  uiVisits: uiSample.visits || [],
  visits: results,
}

const outDir = path.join(__dirname, '../test-results')
fs.mkdirSync(outDir, { recursive: true })
const outPath = path.join(outDir, 'services-100-sim.json')
fs.writeFileSync(outPath, JSON.stringify(report, null, 2))

console.log('\n=== SERVICES 100-CLIENT UX SIM ===')
console.log(JSON.stringify(summary.funnel, null, 2))
console.log('Gates:', summary.gates)
console.log('By intent:', summary.byIntent)
console.log('Fail steps:', summary.failSteps)
console.log('UI sample:', { skipped: uiSample.skipped, n: uiSample.n, ok: uiSample.ok, ok_pct: uiSample.ok_pct })
console.log('Findings:', findings)
console.log(`Latency p50=${summary.latency.p50}ms p95=${summary.latency.p95}ms`)
console.log(`Wrote ${outPath}`)

const criticalFail = findings.some((f) => f.severity === 'P0')
process.exit(criticalFail && summary.ok_pct < 50 ? 1 : 0)
