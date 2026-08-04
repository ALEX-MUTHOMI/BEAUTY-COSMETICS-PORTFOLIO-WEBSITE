/**
 * 100-client conversion simulation — homepage + catalog + book→slots path.
 *
 * Measured (not gut-feel): SSR conversion surfaces, deep-link integrity,
 * resolve-handoff → calendar open days → availability slots → details chrome.
 * Does NOT fire STK (avoids creating 100 holds); pay-ready = policy + continue chrome.
 *
 * Run from frontend/: node scripts/sim-conversion-100.mjs
 */
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const FRONT = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const API = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'
const TOTAL = Number(process.env.SIM_CLIENTS || 100)
const CONCURRENCY = Number(process.env.SIM_CONCURRENCY || 3)
const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** Cohort mix mirrors prior product audit. */
const COHORT_MIX = [
  { cohort: 'new', weight: 55, intent: 'home_to_book' },
  { cohort: 'returning', weight: 30, intent: 'direct_book' },
  { cohort: 'day_of', weight: 15, intent: 'impulse' },
]

const PACKAGE_PATHS = [
  { path: '/book/package/classic-full-package', handoff: { type: 'package', plan: 'classic-full-package' } },
  { path: '/book/package/glow-package', handoff: { type: 'package', plan: 'glow-package' } },
  { path: '/book/package/relax-package', handoff: { type: 'package', plan: 'relax-package' } },
]

const SINGLE_PATHS = [
  { path: '/book/facials/deep-cleansing-facial', handoff: { type: 'single', category: 'facials', treatment: 'deep-cleansing-facial' } },
  { path: '/book/massage/back-neck-and-shoulders', handoff: { type: 'single', category: 'massage', treatment: 'back-neck-and-shoulders' } },
  { path: '/book/waxing/full-leg', handoff: { type: 'single', category: 'waxing', treatment: 'full-leg' } },
  { path: '/book/makeup/soft-glam', handoff: { type: 'single', category: 'makeup', treatment: 'soft-glam' } },
]

function buildClients(n) {
  const clients = []
  let id = 1
  for (const row of COHORT_MIX) {
    const count = Math.round((row.weight / 100) * n)
    for (let i = 0; i < count; i++) {
      const pkg = PACKAGE_PATHS[id % PACKAGE_PATHS.length]
      const single = SINGLE_PATHS[id % SINGLE_PATHS.length]
      let bookTarget = id % 2 === 0 ? pkg : single
      if (row.cohort === 'day_of') bookTarget = single
      if (row.cohort === 'returning' && i % 3 === 0) bookTarget = pkg
      clients.push({
        id,
        name: `${row.cohort}-${id}`,
        cohort: row.cohort,
        intent: row.intent,
        bookPath: bookTarget.path,
        handoff: bookTarget.handoff,
      })
      id += 1
    }
  }
  while (clients.length < n) {
    const pkg = PACKAGE_PATHS[0]
    clients.push({
      id: clients.length + 1,
      name: `fill-${clients.length + 1}`,
      cohort: 'new',
      intent: 'home_to_book',
      bookPath: pkg.path,
      handoff: pkg.handoff,
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

/** One-shot homepage product surface audit (SSR). */
function auditHomepageHtml(html) {
  const deepBookCtas = [...html.matchAll(/href="(\/book\/[^"]+)"/g)].map((m) => m[1])
  const uniqueBook = [...new Set(deepBookCtas)]
  return {
    httpOk: true,
    hasHeroBookDeepLink: /hero__cta[^>]*>[\s\S]*?href="\/book\//.test(html) || /href="\/book\/[^"]+"[^>]*hero__cta/.test(html) || /class="[^"]*hero__cta[^"]*"[^>]*href="\/book\//.test(html) || (html.includes('hero__cta') && html.includes('/book/package/')),
    headerBookIsDeepLink: /site-header__cta"[^>]*href="\/book\//.test(html) || /href="\/book\/[^"]+"[^>]*site-header__cta/.test(html),
    stickyBookIsDeepLink: /mobile-book-bar__cta[\s\S]{0,200}href="\/book\//.test(html) || /href="\/book\/[^"]+"[^>]*mobile-book-bar__cta/.test(html),
    bookDeepLinkCount: deepBookCtas.length,
    uniqueBookHrefs: uniqueBook,
    hasServicesCatalogLink: html.includes('/services#full-packages'),
    hasPriceFloor: html.includes('Packages from KES 7,000') || html.includes('packages from KES 7,000'),
    hasClassic12k: html.includes('12,000'),
    hasPriceClarifier: html.includes('Most booked') && html.includes('12,000') && html.includes('7,000'),
    hasWhatsAppMe: /wa\.me\/\d+/.test(html),
    hasPlaceholderWa: html.includes('254700000000'),
    hasPendingPhoneCopy: /book online/i.test(html),
    whatsappE164Public: (() => {
      const m = html.match(/whatsappE164:"([^"]*)"/)
      return m ? m[1] : null
    })(),
  }
}

async function runBookFunnel(client) {
  const funnel = {
    land_ok: false,
    deep_link_ok: false,
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

  const page = await fetchText(`${FRONT}${client.bookPath}`)
  funnel.latencies.page = page.ms
  if (!page.ok) {
    funnel.fail_step = 'page_load'
    return funnel
  }
  funnel.land_ok = true
  funnel.deep_link_ok = /Next open dates|Continue to checkout|Date &amp; time|Date & time/i.test(page.text)

  const handoffQ = { type: client.handoff.type }
  if (client.handoff.plan) handoffQ.plan = client.handoff.plan
  if (client.handoff.category) handoffQ.category = client.handoff.category
  if (client.handoff.treatment) handoffQ.treatment = client.handoff.treatment

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
  const available = days.filter((d) => d.status === 'available' || d.status === 'open' || d.open === true || d.label === 'OPEN')
  // API may use status: 'available'
  const openDays = days.filter((d) => {
    const s = String(d.status || '').toLowerCase()
    return s === 'available' || s === 'open' || d.available === true
  })
  funnel.open_day_count = openDays.length || available.length
  if (!calendar.ok || !days.length) {
    funnel.fail_step = 'calendar'
    return funnel
  }
  if (!funnel.open_day_count) {
    funnel.fail_step = 'no_open_days'
    return funnel
  }
  funnel.see_open_days = true

  const day = (openDays.length ? openDays : available)[client.id % (openDays.length || available.length)]
  const slotParams = { ...calParams, start_date: day.date, end_date: day.date }
  const slotsRes = await fetchJson(`${API}/api/bookings/availability/?${qs(slotParams)}`)
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
  const bookReload = await fetchText(`${FRONT}${client.bookPath}`)
  const detailsReady =
    policy.ok &&
    bookReload.ok &&
    /Continue to checkout/i.test(bookReload.text)
  funnel.details_ready = detailsReady
  if (!detailsReady) funnel.fail_step = 'details_chrome'
  return funnel
}

async function runHomeSurface(client, homeAudit) {
  const home = await fetchText(`${FRONT}/`)
  const ok = home.ok && /Shee|Book this visit|Book your visit/i.test(home.text)
  const deep =
    home.ok &&
    (/href="\/book\//.test(home.text) || homeAudit.bookDeepLinkCount > 0)
  const wouldTapBook = ok && deep && (homeAudit.headerBookIsDeepLink || homeAudit.hasHeroBookDeepLink || deep)
  // Impulse clients need WA; measured live/fail-closed
  const impulseContact = homeAudit.hasWhatsAppMe && !homeAudit.hasPlaceholderWa
  return {
    land_ok: ok,
    deep_link_ok: deep,
    would_tap_book: wouldTapBook,
    impulse_contact_ok: client.cohort === 'day_of' ? impulseContact : true,
    wa_live: homeAudit.hasWhatsAppMe,
    latencies: { home: home.ms },
    fail_step: !ok ? 'home_land' : !deep ? 'home_deep_link' : null,
  }
}

async function runClient(client, homeAudit) {
  const started = Date.now()
  const home = await runHomeSurface(client, homeAudit)

  // All cohorts that book also exercise the book funnel (product truth).
  const book = await runBookFunnel(client)

  const tappedBook = home.would_tap_book
  const sawSlots = book.see_slots
  // Modeled pay-ready: reached selectable slots + details chrome (no STK fired)
  const payReady = sawSlots && book.details_ready && !book.throttled

  let ok = false
  if (client.cohort === 'day_of') {
    ok = home.land_ok && (home.impulse_contact_ok || tappedBook) && (sawSlots || home.impulse_contact_ok)
  } else if (client.cohort === 'returning') {
    ok = book.land_ok && book.see_open_days && book.see_slots
  } else {
    ok = tappedBook && book.see_open_days && book.see_slots
  }

  return {
    id: client.id,
    name: client.name,
    cohort: client.cohort,
    intent: client.intent,
    bookPath: client.bookPath,
    ok,
    home,
    book,
    metrics: {
      tapped_book: tappedBook,
      saw_open_days: book.see_open_days,
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
      // Gentle pacing to keep 429 noise down for measurement quality
      await new Promise((r) => setTimeout(r, 80))
    }
  }
  await Promise.all(Array.from({ length: concurrency }, () => next()))
  return results
}

function pct(n, d) {
  if (!d) return 0
  return Math.round((n / d) * 1000) / 10
}

function summarize(results, homeAudit) {
  const total = results.length
  const byCohort = {}
  for (const c of ['new', 'returning', 'day_of']) {
    const rows = results.filter((r) => r.cohort === c)
    byCohort[c] = {
      n: rows.length,
      ok: rows.filter((r) => r.ok).length,
      tapped_book: rows.filter((r) => r.metrics.tapped_book).length,
      saw_slots: rows.filter((r) => r.metrics.saw_slots).length,
      pay_ready: rows.filter((r) => r.metrics.pay_ready).length,
      throttled: rows.filter((r) => r.metrics.throttled).length,
    }
  }

  const tapped = results.filter((r) => r.metrics.tapped_book).length
  const sawSlots = results.filter((r) => r.metrics.saw_slots).length
  const payReady = results.filter((r) => r.metrics.pay_ready).length
  const throttled = results.filter((r) => r.metrics.throttled).length
  const ok = results.filter((r) => r.ok).length

  const failSteps = {}
  for (const r of results) {
    const step = r.book.fail_step || r.home.fail_step
    if (step) failSteps[step] = (failSteps[step] || 0) + 1
  }

  const latencies = []
  for (const r of results) {
    for (const v of Object.values({ ...r.home.latencies, ...r.book.latencies })) {
      if (typeof v === 'number') latencies.push(v)
    }
  }
  latencies.sort((a, b) => a - b)
  const p50 = latencies[Math.floor(latencies.length * 0.5)] || 0
  const p95 = latencies[Math.floor(latencies.length * 0.95)] || 0

  return {
    total,
    ok,
    ok_pct: pct(ok, total),
    funnel: {
      tapped_book: tapped,
      tapped_book_pct: pct(tapped, total),
      saw_slots: sawSlots,
      saw_slots_pct: pct(sawSlots, total),
      pay_ready: payReady,
      pay_ready_pct: pct(payReady, total),
      throttled,
      throttled_pct: pct(throttled, total),
    },
    gates: {
      see_open_slots_target: 70,
      see_open_slots_actual: pct(sawSlots, total),
      see_open_slots_pass: pct(sawSlots, total) >= 70,
      tap_book_target: 65,
      tap_book_actual: pct(tapped, total),
      tap_book_pass: pct(tapped, total) >= 65,
      pay_ready_target: 28,
      pay_ready_actual: pct(payReady, total),
      pay_ready_pass: pct(payReady, total) >= 28,
      wa_live: homeAudit.hasWhatsAppMe && !homeAudit.hasPlaceholderWa,
      deep_link_live: homeAudit.headerBookIsDeepLink || homeAudit.bookDeepLinkCount > 0,
    },
    byCohort,
    failSteps,
    latency: { p50, p95, samples: latencies.length },
    homeAudit,
  }
}

const homePage = await fetchText(`${FRONT}/`)
if (!homePage.ok) {
  console.error('Homepage unreachable', homePage.status, homePage.error)
  process.exit(2)
}
const homeAudit = auditHomepageHtml(homePage.text)
homeAudit.homeMs = homePage.ms

const clients = buildClients(TOTAL)
console.log(`Conversion sim n=${clients.length} FRONT=${FRONT} API=${API} concurrency=${CONCURRENCY}`)
const started = Date.now()
const results = await mapPool(clients, CONCURRENCY, (c) => runClient(c, homeAudit))
const summary = summarize(results, homeAudit)
const report = {
  generatedAt: new Date().toISOString(),
  title: 'Shee Aesthetics — 100-client conversion simulation',
  front: FRONT,
  api: API,
  elapsedMs: Date.now() - started,
  concurrency: CONCURRENCY,
  method:
    'SSR homepage surface audit + per-client home land + API resolve→calendar→availability→details chrome. No STK holds created.',
  summary,
  visits: results,
}

const outDir = path.join(__dirname, '../test-results')
fs.mkdirSync(outDir, { recursive: true })
const outPath = path.join(outDir, 'conversion-100-sim.json')
fs.writeFileSync(outPath, JSON.stringify(report, null, 2))

console.log('\n=== CONVERSION 100-CLIENT SIM ===')
console.log(JSON.stringify(summary.funnel, null, 2))
console.log('Gates:', summary.gates)
console.log('Cohorts:', summary.byCohort)
console.log('Fail steps:', summary.failSteps)
console.log(`Latency p50=${summary.latency.p50}ms p95=${summary.latency.p95}ms`)
console.log(`Home deepLinks=${homeAudit.bookDeepLinkCount} clarifier=${homeAudit.hasPriceClarifier} wa=${homeAudit.hasWhatsAppMe}`)
console.log(`Wrote ${outPath}`)

process.exit(summary.ok_pct < 40 ? 1 : 0)
