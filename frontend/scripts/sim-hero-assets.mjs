/**
 * Concurrent visit smoke for homepage + hero images.
 *
 * Models ~100 concurrent visitors in under a minute with a bounded
 * in-flight pool (default 40) so we measure delivery under load without
 * a pure thundering-herd that only measures Node queue depth.
 *
 * Each visit: GET `/` + first-paint mobile heroes (makeup + facial @ 960w).
 *
 * Pass bar: 0 failures, image p95 < 2s, wall < 60s.
 *
 * Usage:
 *   node scripts/sim-hero-assets.mjs
 *   node scripts/sim-hero-assets.mjs --base http://127.0.0.1:3000 --clients 100 --concurrency 40
 *   node scripts/sim-hero-assets.mjs --full
 */
import { performance } from 'node:perf_hooks'

const args = process.argv.slice(2)
function flag(name, fallback) {
  const i = args.indexOf(`--${name}`)
  if (i === -1) return fallback
  return args[i + 1] ?? fallback
}
function hasFlag(name) {
  return args.includes(`--${name}`)
}

const base = String(flag('base', 'http://127.0.0.1:3000')).replace(/\/$/, '')
const clients = Number(flag('clients', '100'))
const concurrency = Math.max(1, Number(flag('concurrency', '40')))
const p95LimitMs = Number(flag('p95', '2000'))
const full = hasFlag('full')

const firstPaintImages = ['/images/hero-makeup-960.jpg', '/images/hero-facial-960.jpg']

const fullImages = [
  '/images/hero-makeup-960.jpg',
  '/images/hero-facial-960.jpg',
  '/images/hero-massage-960.jpg',
  '/images/hero-waxing-960.jpg',
  '/images/hero-makeup.jpg',
  '/images/hero-facial.jpg',
  '/images/hero-massage.jpg',
  '/images/hero-waxing.jpg',
]

const imagePaths = full ? fullImages : firstPaintImages

async function hit(path, { expectBytes = 1_000 } = {}) {
  const started = performance.now()
  const res = await fetch(`${base}${path}`, {
    headers: { Accept: path.endsWith('.jpg') ? 'image/*,*/*' : 'text/html,*/*' },
  })
  const buf = await res.arrayBuffer()
  return {
    path,
    ok: res.ok && buf.byteLength > expectBytes,
    status: res.status,
    bytes: buf.byteLength,
    ms: performance.now() - started,
  }
}

async function runVisit() {
  const results = [await hit('/', { expectBytes: 500 })]
  for (const path of imagePaths) {
    results.push(await hit(path, { expectBytes: 5_000 }))
  }
  return results
}

async function mapPool(count, poolSize, worker) {
  const out = []
  let next = 0
  async function slot() {
    while (next < count) {
      const i = next
      next += 1
      out[i] = await worker(i)
    }
  }
  await Promise.all(Array.from({ length: Math.min(poolSize, count) }, () => slot()))
  return out
}

function percentile(sortedMs, p) {
  if (!sortedMs.length) return 0
  const idx = Math.min(sortedMs.length - 1, Math.floor(sortedMs.length * p))
  return sortedMs[idx]
}

async function main() {
  console.log(
    `Hero asset sim → ${base} · ${clients} visits · concurrency ${concurrency} · homepage + ${imagePaths.length} images${full ? ' (full)' : ' (first-paint)'}`,
  )

  const started = performance.now()
  const visitBatches = await mapPool(clients, concurrency, () => runVisit())
  const elapsed = performance.now() - started
  const results = visitBatches.flat()

  const html = results.filter((r) => r.path === '/')
  const images = results.filter((r) => r.path !== '/')
  const ok = results.filter((r) => r.ok).length
  const fail = results.length - ok
  const imageMs = images.map((r) => r.ms).sort((a, b) => a - b)
  const p95 = percentile(imageMs, 0.95)
  const avgBytes = images.reduce((s, r) => s + r.bytes, 0) / Math.max(1, images.length)

  console.log(`requests=${results.length} ok=${ok} fail=${fail}`)
  console.log(
    `html_ok=${html.filter((r) => r.ok).length}/${html.length} images_ok=${images.filter((r) => r.ok).length}/${images.length}`,
  )
  console.log(
    `wall_ms=${elapsed.toFixed(0)} image_p95_ms=${p95.toFixed(0)} avg_image_bytes=${Math.round(avgBytes)}`,
  )

  if (fail > 0) {
    const sample = results.filter((r) => !r.ok).slice(0, 8)
    console.error('failures', sample)
    process.exit(1)
  }
  if (p95 > p95LimitMs) {
    console.error(`image p95 ${p95.toFixed(0)}ms exceeds limit ${p95LimitMs}ms`)
    process.exit(1)
  }
  if (elapsed > 60_000) {
    console.error(`wall ${elapsed.toFixed(0)}ms exceeds 60s`)
    process.exit(1)
  }
  console.log('PASS')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
