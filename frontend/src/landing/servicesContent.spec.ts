import { describe, expect, it } from 'vitest'
import {
  SERVICES_PAGE_INTRO,
  serviceCategories,
  validateServiceCategories,
} from './servicesContent'

describe('servicesContent', () => {
  it('defines four service categories with detailed treatments', () => {
    expect(validateServiceCategories(serviceCategories)).toBe(true)
    expect(serviceCategories.map((c) => c.id)).toEqual(['facials', 'massage', 'waxing', 'makeup'])
  })

  it('lists multiple facial types with duration and pricing', () => {
    const facials = serviceCategories.find((c) => c.id === 'facials')
    expect(facials?.treatments.length).toBeGreaterThanOrEqual(4)
    expect(facials?.treatments.some((t) => /deep cleansing/i.test(t.name))).toBe(true)
    expect(facials?.treatments.every((t) => t.price.startsWith('From KES'))).toBe(true)
  })

  it('covers massage, waxing and makeup with bookable singles copy', () => {
    expect(serviceCategories.find((c) => c.id === 'massage')?.treatments.length).toBeGreaterThanOrEqual(3)
    expect(serviceCategories.find((c) => c.id === 'waxing')?.treatments.length).toBeGreaterThanOrEqual(5)
    expect(serviceCategories.find((c) => c.id === 'makeup')?.treatments.length).toBeGreaterThanOrEqual(3)
    expect(SERVICES_PAGE_INTRO.note.toLowerCase()).toMatch(/tue|package/)
  })
})
