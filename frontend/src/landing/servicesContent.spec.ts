import { describe, expect, it } from 'vitest'
import {
  FLUID_CARD_GROWTH_CONTRACT,
  PORTRAIT_PACKAGE_CARD_CONTRACT,
  SERVICE_DISTINCT_TILES_CONTRACT,
  SERVICES_CITATION_LINE,
  SERVICES_PAGE_INTRO,
  TREATMENT_TAB_ARCHITECTURE_CONTRACT,
  getSingleTreatmentHighlights,
  serviceCategories,
  validateFluidCardGrowth,
  validatePortraitPackageCard,
  validateServiceCategories,
  validateServiceDistinctTiles,
  validateTreatmentTabArchitecture,
} from './servicesContent'
import { bookHrefForTreatment } from './bookingHandoff'
import { SERVICE_CATEGORY_IDS } from './servicesNavigation'

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
    expect(SERVICES_PAGE_INTRO.title).toMatch(/how would you like to visit/i)
    expect(SERVICES_PAGE_INTRO).not.toHaveProperty('lead')
    expect(SERVICES_PAGE_INTRO).not.toHaveProperty('note')
    expect(SERVICES_CITATION_LINE).toMatch(/Shee Aesthetics/)
    expect(SERVICES_CITATION_LINE).toMatch(/Meru/)
  })

  it('surfaces one directly-bookable specific treatment per category', () => {
    const highlights = getSingleTreatmentHighlights()
    expect(highlights).toHaveLength(serviceCategories.length)
    expect(highlights.map((h) => h.category)).toEqual([...SERVICE_CATEGORY_IDS])

    for (const highlight of highlights) {
      const category = serviceCategories.find((c) => c.id === highlight.category)
      expect(category?.treatments.some((t) => t.name === highlight.name)).toBe(true)

      // Each highlight must deep-link to a clean /book/{category}/{treatment} path,
      // never fall back to the generic services entry.
      const href = bookHrefForTreatment(highlight.category, highlight.name)
      expect(href.startsWith(`/book/${highlight.category}/`)).toBe(true)
    }
  })

  it('enforces slender portrait package card proportions and vertical offer list', () => {
    expect(validatePortraitPackageCard(PORTRAIT_PACKAGE_CARD_CONTRACT)).toBe(true)
    expect(PORTRAIT_PACKAGE_CARD_CONTRACT.cardAspectMode).toBe('portrait')
    expect(PORTRAIT_PACKAGE_CARD_CONTRACT.isSingleColumnOffers).toBe(true)
    expect(PORTRAIT_PACKAGE_CARD_CONTRACT.minCardHeightDesktop).toBe('28rem')
  })

  it('enforces distinct treatment tiles and mobile tab wrap architecture', () => {
    expect(validateServiceDistinctTiles(SERVICE_DISTINCT_TILES_CONTRACT)).toBe(true)
    expect(validateTreatmentTabArchitecture(TREATMENT_TAB_ARCHITECTURE_CONTRACT)).toBe(true)
    expect(TREATMENT_TAB_ARCHITECTURE_CONTRACT.tabWrapMode).toBe('wrap')
    expect(validateFluidCardGrowth(FLUID_CARD_GROWTH_CONTRACT)).toBe(true)
  })
})
