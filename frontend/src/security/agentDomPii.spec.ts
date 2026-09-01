/**
 * Agent / DOM PII red-team — booking + staff modules must not leave plaintext
 * email/phone in Web Storage, and staff list fixtures must not dump contact
 * without an explicit reveal gate.
 */
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

const SRC_ROOT = join(__dirname, '..')
const BOOKING_DIR = join(SRC_ROOT, 'booking')
const STAFF_DIR = join(SRC_ROOT, 'staff')

const PLAINTEXT_EMAIL = /[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}/i
const KENYA_PHONE_PLAIN = /\+?2547\d{8}|07\d{8}/

function listSourceFiles(dir: string): string[] {
  const out: string[] = []
  for (const entry of readdirSync(dir)) {
    const absolute = join(dir, entry)
    const stats = statSync(absolute)
    if (stats.isDirectory()) {
      if (entry === 'node_modules') continue
      out.push(...listSourceFiles(absolute))
      continue
    }
    if (/\.(ts|vue)$/.test(entry) && !entry.endsWith('.spec.ts')) out.push(absolute)
  }
  return out
}

describe('agent / DOM PII storage contracts', () => {
  it('booking modules never write plaintext email/phone into localStorage or sessionStorage', () => {
    const files = listSourceFiles(BOOKING_DIR)
    expect(files.length).toBeGreaterThan(5)

    for (const file of files) {
      const text = readFileSync(file, 'utf8')
      if (!/localStorage|sessionStorage/.test(text)) continue

      expect(text).not.toMatch(
        /(?:local|session)Storage\.setItem\([^)]*(?:email|phone|fullName|full_name)/i,
      )

      const setItemBlocks = text.matchAll(/(?:local|session)Storage\.setItem\(([^)]+)\)/g)
      for (const match of setItemBlocks) {
        const args = match[1] ?? ''
        expect(args).not.toMatch(PLAINTEXT_EMAIL)
        expect(args).not.toMatch(KENYA_PHONE_PLAIN)
      }
    }
  })

  it('staff modules keep contact reveal gated (no raw email/phone dump in list templates)', () => {
    const staffVue = listSourceFiles(STAFF_DIR).filter((f) => f.endsWith('.vue'))
    for (const file of staffVue) {
      const text = readFileSync(file, 'utf8')
      const base = file.replace(/\\/g, '/')
      if (/ContactReveal|Login|Password/i.test(base)) continue

      // List/desk panels may bind redacted fields; must not interpolate raw customer email/phone props.
      expect(text).not.toMatch(/\{\{\s*[^}]*(?:customer\.email|client\.email|booking\.email)\s*\}\}/i)
      expect(text).not.toMatch(/\{\{\s*[^}]*(?:customer\.phone|client\.phone|booking\.phone)\s*\}\}/i)
    }
  })

  it('hand-off storage keys stay slug-only (no PII key names)', () => {
    const handoff = readFileSync(join(SRC_ROOT, 'landing/bookingHandoff.ts'), 'utf8')
    expect(handoff).toMatch(/BOOK_HANDOFF_STORAGE_KEY/)
    expect(handoff).not.toMatch(/localStorage\.setItem\([^)]*email/i)
    expect(handoff).not.toMatch(/localStorage\.setItem\([^)]*phone/i)
  })
})
