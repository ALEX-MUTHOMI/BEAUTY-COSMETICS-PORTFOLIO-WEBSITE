import { useHead, useRoute, useRuntimeConfig, useSeoMeta } from 'nuxt/app'
import {
  LANDING_ADDRESS_LINES,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
} from './landingContent'
import { getHeroLcpHref, getHeroLcpSrcset } from './heroMedia'

export const LANDING_OG_IMAGE = '/images/hero-makeup.jpg'

const LANDING_TITLE =
  'Shee Aesthetics | Beauty Studio in Meru Town — Facials, Waxing, Massage & Makeup'

const LANDING_DESCRIPTION =
  'Book facials, waxing, massage and makeup at Shee Aesthetics in Meru Town, Meru County, Kenya. Full spa packages Tuesday and Wednesday. Single treatments Mon, Thu to Sat. Pay online to confirm your slot.'

export function useLandingSeo() {
  const config = useRuntimeConfig()
  const route = useRoute()
  const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'
  const canonical = `${siteUrl}${route.path === '/' ? '' : route.path}`
  const ogImage = `${siteUrl}${LANDING_OG_IMAGE}`

  useSeoMeta({
    title: LANDING_TITLE,
    description: LANDING_DESCRIPTION,
    ogTitle: LANDING_TITLE,
    ogDescription: LANDING_DESCRIPTION,
    ogImage,
    ogType: 'website',
    ogLocale: 'en_KE',
    ogSiteName: 'Shee Aesthetics',
    ogUrl: canonical,
    twitterCard: 'summary_large_image',
    twitterTitle: LANDING_TITLE,
    twitterDescription: LANDING_DESCRIPTION,
    twitterImage: ogImage,
    robots: 'index, follow',
  })

  useHead({
    htmlAttrs: { lang: 'en-KE' },
    link: [
      { rel: 'canonical', href: canonical },
      {
        rel: 'preload',
        as: 'image',
        href: getHeroLcpHref(),
        imagesrcset: getHeroLcpSrcset(),
        imagesizes: '100vw',
        fetchpriority: 'high',
      },
    ],
    script: [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'BeautySalon',
          name: 'Shee Aesthetics',
          description: LANDING_DESCRIPTION,
          url: siteUrl,
          image: ogImage,
          address: {
            '@type': 'PostalAddress',
            addressLocality: LANDING_ADDRESS_LINES[0],
            addressRegion: 'Meru County',
            addressCountry: 'KE',
          },
          areaServed: LANDING_LOCATION_LABEL,
          sameAs: [LANDING_INSTAGRAM_URL],
          email: 'bookings@sheeaesthetics.co.ke',
          priceRange: 'KES',
        }),
      },
    ],
  })
}
