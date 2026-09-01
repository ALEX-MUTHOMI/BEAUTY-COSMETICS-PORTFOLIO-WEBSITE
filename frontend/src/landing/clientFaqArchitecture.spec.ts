import { describe, expect, it } from 'vitest'
import {
  CLIENT_FAQ_ITEMS,
  FAQ_CATEGORIES,
  filterFaqItems,
  validateClientFaqItems,
} from './clientFaqArchitecture'

describe('clientFaqArchitecture', () => {
  it('defines structured client FAQ items covering core client concerns', () => {
    expect(CLIENT_FAQ_ITEMS.length).toBeGreaterThanOrEqual(5)
    expect(validateClientFaqItems(CLIENT_FAQ_ITEMS)).toBe(true)
  })

  it('provides category options for interactive FAQ filtering', () => {
    expect(FAQ_CATEGORIES.map((c) => c.id)).toContain('all')
    expect(FAQ_CATEGORIES.map((c) => c.id)).toContain('packages')
    expect(FAQ_CATEGORIES.map((c) => c.id)).toContain('payment')
  })

  it('filters FAQ items by selected category correctly', () => {
    const packagesOnly = filterFaqItems(CLIENT_FAQ_ITEMS, 'packages')
    expect(packagesOnly.every((i) => i.category === 'packages')).toBe(true)
    expect(packagesOnly.length).toBeGreaterThan(0)

    const all = filterFaqItems(CLIENT_FAQ_ITEMS, 'all')
    expect(all).toHaveLength(CLIENT_FAQ_ITEMS.length)
  })

  it('includes clear M-Pesa payment and Tue/Wed package answers', () => {
    const mpesaItem = CLIENT_FAQ_ITEMS.find((i) => i.id === 'faq-mpesa')
    expect(mpesaItem?.answer.toLowerCase()).toContain('m-pesa')

    const daysItem = CLIENT_FAQ_ITEMS.find((i) => i.id === 'faq-days')
    expect(daysItem?.answer.toLowerCase()).toContain('tuesdays')
  })
})
