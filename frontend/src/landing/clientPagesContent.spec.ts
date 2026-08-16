import { describe, expect, it } from 'vitest'

import {
  BOOKING_STATUS_COPY,
  CUSTOMER_SUPPORT_PAGE,
  FAQ_CATEGORIES,
  FAQ_ITEMS,
  FAQ_PAGE,
  MELLIS_FLOWER_SRC,
  NOT_FOUND_PAGE,
  SERVER_ERROR_PAGE,
  TERMS_SECTIONS,
  assertPlainClientCopy,
  collectClientPageCopy,
} from './clientPagesContent'

/** Em dash, en dash, or spaced hyphen used as a dash. */
const DASH_AS_PUNCTUATION = /[—–]|\s-\s/

const JARGON = /\b(capacity|turnaround|idempotenc|observabilit|shared studio|submit your details|automatically)\b/i

describe('clientPagesContent (natural human copy & contracts)', () => {
  it('uses the Mellis flower asset path', () => {
    expect(MELLIS_FLOWER_SRC).toBe('/images/flower.png')
  })

  it('keeps FAQ short, natural, and structured with categories', () => {
    expect(FAQ_PAGE.title).toBe('Frequently asked questions')
    expect(FAQ_CATEGORIES.length).toBeGreaterThanOrEqual(4)
    expect(FAQ_ITEMS.length).toBeGreaterThanOrEqual(6)

    for (const item of FAQ_ITEMS) {
      expect(item.q.length).toBeLessThan(70)
      expect(item.a.length).toBeLessThan(200)
      expect(item.a).not.toMatch(DASH_AS_PUNCTUATION)
      expect(item.q).not.toMatch(DASH_AS_PUNCTUATION)
      expect(item.a).not.toMatch(JARGON)
      expect(assertPlainClientCopy(item.q)).toBe(true)
      expect(assertPlainClientCopy(item.a)).toBe(true)
      expect(item.category).toBeTruthy()
    }

    expect(assertPlainClientCopy(FAQ_PAGE.lead)).toBe(true)
    expect(assertPlainClientCopy(FAQ_PAGE.asideCopy)).toBe(true)
  })

  it('provides 404 and 503 error page copy', () => {
    expect(NOT_FOUND_PAGE.title).toBe('Page not found')
    expect(NOT_FOUND_PAGE.lead.length).toBeLessThan(90)
    expect(NOT_FOUND_PAGE.lead).not.toMatch(DASH_AS_PUNCTUATION)
    expect(assertPlainClientCopy(NOT_FOUND_PAGE.lead)).toBe(true)

    expect(SERVER_ERROR_PAGE.title).toBe('Connection interrupted')
    expect(SERVER_ERROR_PAGE.retryButton).toBe('Try again')
    expect(assertPlainClientCopy(SERVER_ERROR_PAGE.lead)).toBe(true)
  })

  it('provides customer contact and studio details', () => {
    expect(CUSTOMER_SUPPORT_PAGE.title).toBe('Get in touch')
    expect(CUSTOMER_SUPPORT_PAGE.studioAddress).toContain('Meru Town')
    expect(CUSTOMER_SUPPORT_PAGE.email).toBe('bookings@sheeaesthetics.co.ke')
    expect(CUSTOMER_SUPPORT_PAGE.whatsappE164).toBe('254712345678')
    expect(assertPlainClientCopy(CUSTOMER_SUPPORT_PAGE.lead)).toBe(true)
  })

  it('provides 5 structured Terms of Service sections without corporate badges', () => {
    expect(TERMS_SECTIONS).toHaveLength(5)
    TERMS_SECTIONS.forEach((section) => {
      expect(section.title).toBeTruthy()
      expect(section.points.length).toBeGreaterThanOrEqual(3)
    })
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

  it('guards public client-page strings against dashes and jargon', () => {
    for (const line of collectClientPageCopy()) {
      expect(line).not.toMatch(DASH_AS_PUNCTUATION)
      expect(line).not.toMatch(JARGON)
      expect(assertPlainClientCopy(line)).toBe(true)
    }
  })
})
