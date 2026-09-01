import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const FRONTEND_ROOT = join(__dirname, '../..')
const FORBIDDEN_SERVER_DIRS = ['server/api', 'server/routes', 'server/middleware']
const MONEY_WRITE_PATHS = [
  '/api/bookings/holds/',
  '/api/bookings/checkout/',
  '/api/bookings/checkout/mpesa/stk/',
]

function listFiles(dir: string): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir)) {
    const absolute = join(dir, entry)
    const stats = statSync(absolute)
    if (stats.isDirectory()) {
      if (entry === 'node_modules' || entry === '.nuxt' || entry === 'dist') continue
      out.push(...listFiles(absolute))
      continue
    }
    if (/\.(ts|vue|js|mjs)$/.test(entry) && !entry.endsWith('.spec.ts')) out.push(absolute)
  }
  return out
}

describe('thin Django client contracts', () => {
  it('does not add Nuxt server routes that would proxy auth or PII', () => {
    for (const rel of FORBIDDEN_SERVER_DIRS) {
      const absolute = join(FRONTEND_ROOT, rel)
      let existsAsDir = false
      try {
        existsAsDir = statSync(absolute).isDirectory()
      } catch {
        existsAsDir = false
      }
      expect(existsAsDir).toBe(false)
    }
  })

  it('keeps guest money writes on Django /api/bookings paths', () => {
    const writeApi = readFileSync(join(__dirname, 'bookingWriteApi.ts'), 'utf8')
    for (const path of MONEY_WRITE_PATHS) {
      expect(writeApi).toContain(path)
    }
    expect(writeApi).not.toMatch(/\/api\/checkout\/sessions\/.+\/mpesa\/stk/)
  })

  it('never stores email or phone keys in localStorage helpers under booking/', () => {
    const files = listFiles(join(__dirname))
    for (const file of files) {
      const text = readFileSync(file, 'utf8')
      if (!text.includes('localStorage')) continue
      expect(text).not.toMatch(/localStorage\.setItem\([^)]*(email|phone|full_name)/i)
    }
  })
})
