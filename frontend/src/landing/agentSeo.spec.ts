import { describe, expect, it } from 'vitest'

import {
  buildFaqPageJsonLd,
  buildServicesOfferCatalogJsonLd,
  localBusinessNap,
} from './agentSeo'

describe('agentSeo JSON-LD', () => {
  const siteUrl = 'https://sheeaesthetics.co.ke'

  it('keeps LocalBusiness NAP consistent for Meru', () => {
    const nap = localBusinessNap(siteUrl)
    expect(nap['@type']).toBe('BeautySalon')
    expect(nap.address.addressLocality).toBe('Meru')
    expect(nap.address.addressRegion).toBe('Meru County')
    expect(nap.address.addressCountry).toBe('KE')
    expect(nap.areaServed).toMatch(/Meru/)
  })

  it('builds FAQPage entities from FAQ_ITEMS', () => {
    const faq = buildFaqPageJsonLd(siteUrl)
    expect(faq['@type']).toBe('FAQPage')
    expect(faq.mainEntity.length).toBeGreaterThanOrEqual(5)
    expect(faq.mainEntity[0]?.['@type']).toBe('Question')
    expect(JSON.stringify(faq)).toMatch(/Shee Aesthetics/)
    expect(JSON.stringify(faq)).toMatch(/Meru/)
  })

  it('builds OfferCatalog with Service offers for Meru salon', () => {
    const catalog = buildServicesOfferCatalogJsonLd(siteUrl)
    expect(catalog['@type']).toBe('OfferCatalog')
    expect(catalog.itemListElement.length).toBeGreaterThan(10)
    expect(JSON.stringify(catalog)).toMatch(/facial|Facial/i)
    expect(JSON.stringify(catalog)).toMatch(/wax/i)
    expect(catalog.provider.address.addressLocality).toBe('Meru')
  })
})
