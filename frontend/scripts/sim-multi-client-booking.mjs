/**
 * Simulate ~30 concurrent-ish client visits:
 * browse pages, resolve handoff, check calendar/availability, press continue-path signals.
 * Run: node scripts/sim-multi-client-booking.mjs
 */

const FRONT = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const API = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

const PERSONAS = [
  { id: 1, name: 'Amina', intent: 'package', path: '/book/package/classic-full-package', handoff: { type: 'package', plan: 'classic-full-package' } },
  { id: 2, name: 'Brian', intent: 'package', path: '/book/package/glow-package', handoff: { type: 'package', plan: 'glow-package' } },
  { id: 3, name: 'Carol', intent: 'package', path: '/book/package/relax-package', handoff: { type: 'package', plan: 'relax-package' } },
  { id: 4, name: 'Diana', intent: 'single', path: '/book/facials/deep-cleansing-facial', handoff: { type: 'single', category: 'facials', treatment: 'deep-cleansing-facial' } },
  { id: 5, name: 'Eli', intent: 'single', path: '/book/massage/back-neck-and-shoulders', handoff: { type: 'single', category: 'massage', treatment: 'back-neck-and-shoulders' } },
  { id: 6, name: 'Faith', intent: 'single', path: '/book/waxing/brow-shaping', handoff: { type: 'single', category: 'waxing', treatment: 'brow-shaping' } },
  { id: 7, name: 'Grace', intent: 'single', path: '/book/makeup/soft-glam', handoff: { type: 'single', category: 'makeup', treatment: 'soft-glam' } },
  { id: 8, name: 'Hassan', intent: 'browse', path: '/services', handoff: null },
  { id: 9, name: 'Ivy', intent: 'home', path: '/', handoff: null },
  { id: 10, name: 'Jake', intent: 'single', path: '/book/facials/brightening-facial', handoff: { type: 'single', category: 'facials', treatment: 'brightening-facial' } },
]

function expandTo30() {
  const out = []
  for (let i = 0; i < 30; i++) {
    const base = PERSONAS[i % PERSONAS.length]
    out.push({ ...base, visit: i + 1, name: `${base.name}#${Math.floor(i / PERSONAS.length) + 1}` })
  }
  return out
}

async function fetchText(url, init) {
  const started = Date.now()
  try {
    const res = await fetch(url, { ...init, redirect: 'follow' })
    const text = await res.text()
    return { ok: res.ok, status: res.status, ms: Date.now() - started, text, url: res.url }
  } catch (err) {
    return { ok: false, status: 0, ms: Date.now() - started, text: '', error: String(err?.message || err), url }
  }
}

async function fetchJson(url) {
  const started = Date.now()
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' } })
    const text = await res.text()
    let json = null
    try { json = JSON.parse(text) } catch { /* ignore */ }
    return { ok: res.ok, status: res.status, ms: Date.now() - started, json, text }
  } catch (err) {
    return { ok: false, status: 0, ms: Date.now() - started, json: null, error: String(err?.message || err) }
  }
}

function qs(params) {
  return new URLSearchParams(params).toString()
}

async function runClient(client) {
  const steps = []
  const fail = (step, detail) => {
    steps.push({ step, ok: false, detail })
  }
  const pass = (step, detail) => {
    steps.push({ step, ok: true, detail })
  }

  // 1) Land on entry page
  const page = await fetchText(`${FRONT}${client.path}`)
  if (!page.ok) {
    fail('page_load', `${page.status} ${page.error || ''}`.trim())
    return { client, ok: false, steps }
  }
  // SSR may still include html.is-loading (SiteLoader owns clearing it client-side).
  // Gate failure on missing hero/marketing chrome, not on the class string in HTML/CSS.
  const hasHomeChrome =
    /Shee|Your hour to unwind|Book your visit|Shee Aesthetics/i.test(page.text)
  const hasBookChrome =
    /Pick your day|Next open dates|How would you like to visit|Spa Beauty|Shee/i.test(page.text)
  if (client.path === '/' && !hasHomeChrome) {
    fail('home_visible', 'home hero/CTA chrome missing from SSR HTML')
  } else if (!hasBookChrome && client.intent !== 'browse') {
    fail('page_content', 'expected booking/marketing chrome missing')
  } else {
    pass('page_load', `${page.status} in ${page.ms}ms`)
  }

  // 2) Generic CTA surfaces (services / home)
  if (client.intent === 'browse' || client.intent === 'home') {
    const services = await fetchText(`${FRONT}/services`)
    if (services.ok && /Select a treatment|Complete visits in one booking|How would you like to visit/i.test(services.text)) {
      pass('browse_services', `${services.ms}ms`)
    } else {
      fail('browse_services', `${services.status}`)
    }
    return { client, ok: steps.every((s) => s.ok), steps }
  }

  // 3) Resolve handoff + calendar + slots (availability check)
  const handoffQ = { type: client.handoff.type }
  if (client.handoff.plan) handoffQ.plan = client.handoff.plan
  if (client.handoff.category) handoffQ.category = client.handoff.category
  if (client.handoff.treatment) handoffQ.treatment = client.handoff.treatment

  const resolved = await fetchJson(`${API}/api/bookings/catalog/resolve-handoff/?${qs(handoffQ)}`)
  const selection = resolved.json?.selection
  if (!resolved.ok || !selection?.public_id) {
    const hint = resolved.text?.slice(0, 120) || resolved.error || ''
    fail('resolve_handoff', `${resolved.status} ${hint}`.trim())
    return { client, ok: false, steps }
  }
  pass('resolve_handoff', selection.name || selection.public_id)

  const calParams = {
    selection_type: selection.selection_type,
  }
  if (selection.selection_type === 'full_package') {
    calParams.full_package_public_id = selection.public_id
  } else {
    calParams.service_public_id = selection.public_id
  }

  const calendar = await fetchJson(`${API}/api/bookings/calendar/?${qs(calParams)}`)
  const days = calendar.json?.calendar?.days || calendar.json?.days || []
  const available = days.filter((d) => d.status === 'available')
  if (!calendar.ok || !days.length) {
    fail('calendar', `${calendar.status} days=${days.length}`)
    return { client, ok: false, steps }
  }
  pass('calendar', `${available.length}/${days.length} open days · ${calendar.ms}ms`)

  if (!available.length) {
    fail('pick_day', 'no available days in window')
    return { client, ok: false, steps }
  }

  // Simulate impatient clients retrying calendar (governor pressure)
  if (client.visit % 5 === 0) {
    const burst = await Promise.all([
      fetchJson(`${API}/api/bookings/calendar/?${qs(calParams)}`),
      fetchJson(`${API}/api/bookings/calendar/?${qs(calParams)}`),
      fetchJson(`${API}/api/bookings/calendar/?${qs(calParams)}`),
    ])
    const burstOk = burst.filter((b) => b.ok).length
    pass('calendar_burst', `${burstOk}/3 rapid reloads ok`)
  }

  const day = available[client.visit % available.length]
  const slotParams = {
    ...calParams,
    start_date: day.date,
    end_date: day.date,
  }
  const slotsRes = await fetchJson(`${API}/api/bookings/availability/?${qs(slotParams)}`)
  // Shape: { availability: [{ date, slots: [...] }] }
  let normalized = []
  if (Array.isArray(slotsRes.json?.availability)) {
    normalized = slotsRes.json.availability.flatMap((row) =>
      Array.isArray(row?.slots) ? row.slots : [],
    )
  } else if (Array.isArray(slotsRes.json?.slots)) {
    normalized = slotsRes.json.slots
  } else if (Array.isArray(slotsRes.json)) {
    normalized = slotsRes.json
  }

  if (!slotsRes.ok) {
    fail('availability', `${slotsRes.status}`)
    return { client, ok: false, steps }
  }
  if (!normalized.length) {
    // still count calendar success; empty slots is a product signal
    fail('pick_slot', `0 slots on ${day.date}`)
    return { client, ok: false, steps }
  }
  pass('pick_slot', `${normalized.length} slots on ${day.date} · picked index ${client.visit % normalized.length}`)

  // 4) Policy text (details step readiness)
  const policy = await fetchJson(`${API}/api/bookings/policy-acceptance-text/`)
  if (policy.ok && (policy.json?.text || policy.json?.policy_text || policy.text.length > 20)) {
    pass('policy', `${policy.ms}ms`)
  } else {
    fail('policy', `${policy.status}`)
  }

  // 5) Simulate "button press" on continue by reloading book page after selection (SSR path)
  const bookReload = await fetchText(`${FRONT}${client.path}`)
  if (bookReload.ok && /Continue to checkout|Pick your day|Next open dates/i.test(bookReload.text)) {
    pass('continue_chrome', `book UI markers present · ${bookReload.ms}ms`)
  } else {
    fail('continue_chrome', 'book CTA chrome missing on reload')
  }

  return { client, ok: steps.every((s) => s.ok), steps }
}

async function mapPool(items, concurrency, worker) {
  const results = []
  let i = 0
  async function next() {
    while (i < items.length) {
      const idx = i++
      results[idx] = await worker(items[idx], idx)
    }
  }
  await Promise.all(Array.from({ length: concurrency }, () => next()))
  return results
}

function summarize(results) {
  const total = results.length
  const ok = results.filter((r) => r.ok).length
  const stepFails = {}
  const latencies = []
  for (const r of results) {
    for (const s of r.steps) {
      if (!s.ok) stepFails[s.step] = (stepFails[s.step] || 0) + 1
      const m = String(s.detail || '').match(/(\d+)ms/)
      if (m) latencies.push(Number(m[1]))
    }
  }
  latencies.sort((a, b) => a - b)
  const p50 = latencies[Math.floor(latencies.length * 0.5)] || 0
  const p95 = latencies[Math.floor(latencies.length * 0.95)] || 0
  return { total, ok, fail: total - ok, stepFails, p50, p95 }
}

const clients = expandTo30()
console.log(`Simulating ${clients.length} client visits against FRONT=${FRONT} API=${API}`)
const started = Date.now()

// Wave 1: sequential-ish realism (concurrency 4)
const wave1 = await mapPool(clients.slice(0, 20), 4, runClient)
// Wave 2: rush hour burst (concurrency 10)
const wave2 = await mapPool(clients.slice(20), 10, runClient)
const results = [...wave1, ...wave2]
const summary = summarize(results)

const report = {
  generatedAt: new Date().toISOString(),
  front: FRONT,
  api: API,
  elapsedMs: Date.now() - started,
  summary,
  visits: results.map((r) => ({
    visit: r.client.visit,
    name: r.client.name,
    intent: r.client.intent,
    path: r.client.path,
    ok: r.ok,
    steps: r.steps,
  })),
}

const outPath = new URL('../test-results/multi-client-sim.json', import.meta.url)
const fs = await import('node:fs')
fs.mkdirSync(new URL('../test-results/', import.meta.url), { recursive: true })
fs.writeFileSync(outPath, JSON.stringify(report, null, 2))

console.log('\n=== MULTI-CLIENT SIM SUMMARY ===')
console.log(`Visits: ${summary.total}  OK: ${summary.ok}  FAIL: ${summary.fail}`)
console.log(`Elapsed: ${report.elapsedMs}ms  page/api latency p50=${summary.p50}ms p95=${summary.p95}ms`)
console.log('Step failures:', summary.stepFails)
console.log(`Report: ${outPath.pathname}`)

// Print per-visit one-liners
for (const r of results) {
  const mark = r.ok ? 'OK ' : 'FAIL'
  const bad = r.steps.filter((s) => !s.ok).map((s) => s.step).join(',')
  console.log(`${mark} #${String(r.client.visit).padStart(2, '0')} ${r.client.name.padEnd(12)} ${r.client.intent.padEnd(7)} ${bad || 'all-steps-pass'}`)
}

process.exit(summary.fail > summary.total * 0.5 ? 1 : 0)
