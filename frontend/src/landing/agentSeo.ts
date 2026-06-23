/**
 * Module: agentSeo
 * SEO utilities and configuration for landing.
 */
/**
 * Agent / AEO JSON-LD helpers — citation-friendly schemas for marketing pages.
 * Money-path and staff routes stay noindex; do not emit schemas there.
 */
import { FAQ_ITEMS } from './clientPagesContent'
import {
  LANDING_ADDRESS_LINES,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  packages,
} from './landingContent'
import { serviceCategories } from './servicesContent'

export function localBusinessNap(siteUrl: string) {
  return {
    '@type': 'BeautySalon',
    '@id': `${siteUrl}/#salon`,
    name: 'Shee Aesthetics',
    url: siteUrl,
    address: {
      '@type': 'PostalAddress',
      streetAddress: LANDING_ADDRESS_LINES[0],
      addressLocality: 'Meru',
      addressRegion: 'Meru County',
      addressCountry: 'KE',
    },
    areaServed: LANDING_LOCATION_LABEL,
    sameAs: [LANDING_INSTAGRAM_URL],
    email: 'bookings@sheeaesthetics.co.ke',
    priceRange: 'KES',
  }
}

export function buildFaqPageJsonLd(siteUrl: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: FAQ_ITEMS.map((item) => ({
      '@type': 'Question',
      name: item.q,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.a,
      },
    })),
    about: localBusinessNap(siteUrl),
  }
}

export function buildServicesOfferCatalogJsonLd(siteUrl: string) {
  const offerItems = [
    ...packages.map((pkg) => ({
      '@type': 'Offer',
      name: pkg.name,
      description: pkg.text,
      priceCurrency: 'KES',
      url: `${siteUrl}/services`,
      availability: 'https://schema.org/InStock',
    })),
    ...serviceCategories.flatMap((category) =>
      category.treatments.map((treatment) => ({
        '@type': 'Offer',
        itemOffered: {
          '@type': 'Service',
          name: treatment.name,
          description: treatment.description,
          provider: { '@id': `${siteUrl}/#salon` },
          areaServed: LANDING_LOCATION_LABEL,
          serviceType: category.name,
        },
        priceCurrency: 'KES',
        url: `${siteUrl}/services`,
      })),
    ),
  ]

  return {
    '@context': 'https://schema.org',
    '@type': 'OfferCatalog',
    name: 'Shee Aesthetics services — Meru Town',
    description:
      'Facials, waxing, massage, makeup and full packages at Shee Aesthetics beauty salon in Meru Town, Meru County, Kenya.',
    url: `${siteUrl}/services`,
    provider: localBusinessNap(siteUrl),
    itemListElement: offerItems,
  }
}

