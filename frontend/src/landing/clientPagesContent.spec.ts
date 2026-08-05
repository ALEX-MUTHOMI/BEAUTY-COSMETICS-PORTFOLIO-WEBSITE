import { describe, expect, it } from 'vitest'

import {
  BOOKING_STATUS_COPY,
  FAQ_ITEMS,
  FAQ_PAGE,
  MELLIS_FLOWER_SRC,
  NOT_FOUND_PAGE,
  assertPlainClientCopy,
  collectClientPageCopy,
} from './clientPagesContent'

/** Em dash, en dash, or spaced hyphen used as a dash. */
const DASH_AS_PUNCTUATION = /[—–]|\s-\s/

const JARGON = /\b(capacity|turnaround|idempotenc|observabilit|shared studio|submit your details|automatically)\b/i

describe('clientPagesContent (plain Mellis copy)', () => {
  it('uses the Mellis flower asset path', () => {
    expect(MELLIS_FLOWER_SRC).toBe('/images/flower.png')
  })

  it('keeps FAQ short, plain, and free of dash punctuation', () => {
    expect(FAQ_PAGE.title).toBe('Questions')
    expect(FAQ_PAGE.lead.length).toBeLessThan(70)
    expect(FAQ_ITEMS.length).toBeGreaterThanOrEqual(5)
    expect(FAQ_ITEMS.length).toBeLessThanOrEqual(6)

    for (const item of FAQ_ITEMS) {
      expect(item.q.length).toBeLessThan(48)
      expect(item.a.length).toBeLessThan(140)
      expect(item.a).not.toMatch(DASH_AS_PUNCTUATION)
      expect(item.q).not.toMatch(DASH_AS_PUNCTUATION)
      expect(item.a).not.toMatch(JARGON)
      expect(assertPlainClientCopy(item.q)).toBe(true)
      expect(assertPlainClientCopy(item.a)).toBe(true)
    }

    expect(assertPlainClientCopy(FAQ_PAGE.lead)).toBe(true)
    expect(assertPlainClientCopy(FAQ_PAGE.asideCopy)).toBe(true)
  })

  it('keeps 404 copy short without over-explaining', () => {
    expect(NOT_FOUND_PAGE.title).toBe('Page not found')
    expect(NOT_FOUND_PAGE.lead.length).toBeLessThan(90)
    expect(NOT_FOUND_PAGE.lead).not.toMatch(DASH_AS_PUNCTUATION)
    expect(assertPlainClientCopy(NOT_FOUND_PAGE.lead)).toBe(true)
  })

  it('keeps booking confirmation and status lines plain', () => {
    const lines = Object.values(BOOKING_STATUS_COPY)
    expect(lines.length).toBeGreaterThan(4)
    for (const line of lines) {
      expect(line).not.toMatch(DASH_AS_PUNCTUATION)
      expect(line.length).toBeLessThan(120)
      expect(assertPlainClientCopy(line)).toBe(true)
    }
    expect(BOOKING_STATUS_COPY.confirmedLead.toLowerCase()).toContain('thank')
    expect(BOOKING_STATUS_COPY.emptyReference).not.toMatch(/[—–]/)
  })

  it('guards every public client-page string against dashes and jargon', () => {
    for (const line of collectClientPageCopy()) {
      expect(line).not.toMatch(DASH_AS_PUNCTUATION)
      expect(line).not.toMatch(JARGON)
      expect(assertPlainClientCopy(line)).toBe(true)
    }
  })
})
