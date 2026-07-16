/**
 * Concurrent static-asset smoke for homepage hero images.
 *
 * Usage:
 *   node scripts/sim-hero-assets.mjs
 *   node scripts/sim-hero-assets.mjs --base http://127.0.0.1:3000 --clients 100
 */
import { performance } from 'node:perf_hooks'

const args = process.argv.slice(2)
function flag(name, fallback) {
  const i = args.indexOf(`--${name}`)
  if (i === -1) return fallback
  return args[i + 1] ?? fallback
}

const base = String(flag('base', 'http://127.0.0.1:3000')).replace(/\/$/, '')
const clients = Number(flag('clients', '100'))
const paths = [
  '/images/hero-facial.jpg',
  '/images/hero-massage.jpg',
  '/images/hero-makeup.jpg',
]

async function hit(path) {
  const started = performance.now()
  const res = await fetch(`${base}${path}`, {
    headers: { Accept: 'image/*,*/*' },
  })
  const buf = await res.arrayBuffer()
  return {
    path,
    ok: res.ok && buf.byteLength > 10_000,
    status: res.status,
    bytes: buf.byteLength,
    ms: performance.now() - started,
  }
}

async function main() {
  console.log(`Hero asset sim → ${base} · ${clients} concurrent clients · ${paths.length} images`)
  const jobs = []
  for (let c = 0; c < clients; c += 1) {
    for (const path of paths) jobs.push(hit(path))
  }
  const started = performance.now()
  const results = await Promise.all(jobs)
  const elapsed = performance.now() - started
  const ok = results.filter((r) => r.ok).length
  const fail = results.length - ok
  const p95 = [...results].sort((a, b) => a.ms - b.ms)[Math.floor(results.length * 0.95)]?.ms ?? 0
  const avgBytes = results.reduce((s, r) => s + r.bytes, 0) / results.length

  console.log(`requests=${results.length} ok=${ok} fail=${fail}`)
  console.log(`wall_ms=${elapsed.toFixed(0)} p95_ms=${p95.toFixed(0)} avg_bytes=${Math.round(avgBytes)}`)
  if (fail > 0) {
    const sample = results.filter((r) => !r.ok).slice(0, 5)
    console.error('failures', sample)
    process.exit(1)
  }
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
