/**
 * Module: landingContent
 * Additional content helpers for landing pages.
 */
/**
 * @module
 * Contains the main content data and helpers for the landing page.
 * Includes packages, workflow steps, and social contact placeholders.
 */
export interface LandingPackage {
  name: string
  text: string
  price: string
  includes: string[]
  featured?: boolean
  badge?: string
  daysLabel?: string
  ctaLabel?: string
}

export interface FlowStep {
  num: string
  title: string
  text: string
}

export const LANDING_PRIMARY_CTA = 'Book your visit'

export const LANDING_INSTAGRAM_URL = 'https://www.instagram.com/shee_aesthetics/'

/**
 * Public WhatsApp + phone (fail-closed).
 *
 * Set `NUXT_PUBLIC_WHATSAPP_E164` (digits only, e.g. 2547XXXXXXXX) in env /
 * `runtimeConfig.public.whatsappE164`. Until a real number is configured,
 * never render `wa.me` / `tel:` links — the placeholder 254700000000 must
 * never ship as a live CTA.
 *
 * Prefer `useLandingContact()` in Vue SFCs so runtimeConfig wins over
 * build-time defaults. Module constants below are build-time fallbacks for
 * pure helpers (e.g. primaryBookHref) and unit tests.
 */
export const LANDING_CONTACT_PLACEHOLDER_E164 = '254700000000'

/** Normalize raw env/config into E.164 digits or the safe placeholder. */
export function resolveWhatsappE164(raw: unknown): string {
  const digits = String(raw ?? '').replace(/\D/g, '')
  if (digits.length >= 11 && digits !== LANDING_CONTACT_PLACEHOLDER_E164) return digits
  return LANDING_CONTACT_PLACEHOLDER_E164
}

export type LandingContact = {
  e164: string
  isLive: boolean
  phoneDisplay: string
  phoneTel: string
  whatsappUrl: string
}

export function landingContactFromE164(raw: unknown): LandingContact {
  const e164 = resolveWhatsappE164(raw)
  const isLive = e164 !== LANDING_CONTACT_PLACEHOLDER_E164
  return {
    e164,
    isLive,
    phoneDisplay: isLive ? `+${e164}` : 'Meru Town · book online',
    phoneTel: isLive ? `tel:+${e164}` : '',
    whatsappUrl: isLive ? `https://wa.me/${e164}` : '',
  }
}

function readBuildTimeWhatsappE164(): string {
  const fromProcess =
    typeof process !== 'undefined' ? String(process.env.NUXT_PUBLIC_WHATSAPP_E164 || '') : ''
  return resolveWhatsappE164(fromProcess)
}

const _buildContact = landingContactFromE164(readBuildTimeWhatsappE164())

export const LANDING_WHATSAPP_E164 = _buildContact.e164
export const LANDING_CONTACT_IS_LIVE = _buildContact.isLive
export const LANDING_PHONE_DISPLAY = _buildContact.phoneDisplay
export const LANDING_PHONE_TEL = _buildContact.phoneTel
export const LANDING_WHATSAPP_URL = _buildContact.whatsappUrl
export const LANDING_WHATSAPP_LABEL = 'WhatsApp'
export const LANDING_CALL_LABEL = 'Call Shee'

/** Compact price anchors for hero / trust strips (from catalog floors). */
export const LANDING_TREATMENT_FLOOR = 'From KES 1,200'
export const LANDING_PACKAGE_FLOOR = 'From KES 7,000'
export const LANDING_PACKAGE_FLOOR_SHORT = 'KES 7,000'

export const LANDING_PRICE_ANCHOR =
  `Treatments from KES 1,200 · Packages from ${LANDING_PACKAGE_FLOOR_SHORT}`

/** Featured Classic card clarifying line (keeps 12,000; floor stays Relax). */
export const LANDING_FEATURED_PACKAGE_CLARIFIER =
  'Most booked · from KES 12,000 · packages from KES 7,000'

export const LANDING_LOCATION_LABEL = 'Meru Town, Meru County'

/** Meet Shee — compact Get to know us → Clients by Shee. */
export const GLOW_SECTION_EYEBROW = 'Get to know us'
export const GLOW_SECTION_HEADING = 'Meet your therapist'
export const GLOW_SECTION_TEXT =
  'Shee welcomes you in Meru Town for facials, waxing, massage, and makeup — calm, private, and easy to book.'
export const GLOW_ARTIST_NAME = 'Shee'
export const GLOW_ARTIST_LINE = 'Beauty artist · Meru Town'
export const GLOW_CONTINUE_LABEL = 'See her work'
export const GLOW_CONTINUE_HASH = '#our-work'

export const LANDING_ADDRESS_LINES = ['Meru Town', 'Meru County, Kenya'] as const

export type LandingClientReview = {
  name: string
  text: string
  visitLabel: string
  service: 'facial' | 'waxing' | 'makeup' | 'massage'
}

/** Meru client stories — honesty framing; no stock reviewer photos. */
export const landingClientReviews: LandingClientReview[] = [
  {
    name: 'Wanjiku M.',
    text: 'I booked a deep cleansing facial on Thursday and left with calm, clear skin. The therapist explained every step and the room was spotless — I already rebooked for next month.',
    visitLabel: 'Facial · Meru client',
    service: 'facial',
  },
  {
    name: 'Amina K.',
    text: 'Came for a full-leg wax before an event. Quick, neat, and barely any irritation after. Shee made it feel private and professional — I will not go anywhere else in Meru.',
    visitLabel: 'Waxing · Meru client',
    service: 'waxing',
  },
  {
    name: 'Sharon O.',
    text: 'Had soft glam makeup for a wedding. It stayed on through tears, dancing, and photos. Guests kept asking who did my face — booking online was easy too.',
    visitLabel: 'Makeup · Meru client',
    service: 'makeup',
  },
]

export const PACKAGE_DAYS = ['Tuesday', 'Wednesday'] as const

export const SINGLE_DAYS_LABEL = 'Mon · Thu – Sat'

export { heroSlides, type HeroSlide } from './heroMedia'

export const flowSteps: FlowStep[] = [
  {
    num: '01',
    title: 'Choose your visit',
    text: 'Pick a date, treatment or package online.',
  },
  {
    num: '02',
    title: 'Pay with M-Pesa',
    text: 'Checkout locks your slot. A receipt arrives by email.',
  },
  {
    num: '03',
    title: 'Come in glowing',
    text: 'Arrive a few minutes early — we take it from there.',
  },
]

export const packageDayHeadline = 'Full Package Days'

export const packageDaySubhead =
  'Tuesdays and Wednesdays for full visits — facial, wax, massage and makeup in one booking.'

export const packageDayUrgency =
  'Package days only. Slots are limited each week.'

export function isPackageDay(day: string): boolean {
  return PACKAGE_DAYS.some((d) => d.toLowerCase() === day.toLowerCase())
}

export const PACKAGE_BOOK_CTA = 'Book this package'

/** Display order on /services: Glow · Classic (Most booked, center) · Relax */
export const packages: LandingPackage[] = [
  {
    name: 'Glow Package',
    text: 'For events and photos. Brighten skin, shape brows and finish with soft glam.',
    price: 'From KES 8,500',
    daysLabel: 'Tue & Wed only',
    ctaLabel: PACKAGE_BOOK_CTA,
    includes: [
      'Brightening facial',
      'Brow shaping & wax',
      'Soft glam makeup',
      'Skin consultation',
    ],
  },
  {
    name: 'Classic Full Package',
    text: 'Our most booked visit. Arrive once, leave with skin, body and makeup done.',
    price: 'From KES 12,000',
    badge: 'Most booked',
    featured: true,
    daysLabel: 'Tue & Wed only',
    ctaLabel: PACKAGE_BOOK_CTA,
    includes: [
      'Deep cleansing facial',
      'Full body waxing',
      '60-minute massage',
      'Event-ready makeup',
    ],
  },
  {
    name: 'Relax Package',
    text: 'When you need to switch off. Massage-led with wax and an express facial.',
    price: 'From KES 7,000',
    daysLabel: 'Tue & Wed only',
    ctaLabel: PACKAGE_BOOK_CTA,
    includes: [
      'Deep tissue massage',
      'Back & shoulder wax',
      'Express facial',
      'Aromatherapy finish',
    ],
  },
]

/** Homepage shows featured packages only — full catalog lives on /services. */
export function getFeaturedPackages(list: LandingPackage[] = packages): LandingPackage[] {
  const featured = list.filter((p) => p.featured)
  return featured.length > 0 ? featured : list.slice(0, 1)
}

/** Shared place query for Maps search / directions / embed (no API key). */
const LANDING_MAPS_PLACE_QUERY = 'Shee+Aesthetics+Meru+Town+Kenya'

/** Opens the place card in Google Maps (mobile app or web). */
export const LANDING_MAPS_URL =
  `https://www.google.com/maps/search/?api=1&query=${LANDING_MAPS_PLACE_QUERY}`

/** Turn-by-turn directions to the studio — preferred client CTA. */
export const LANDING_MAPS_DIRECTIONS_URL =
  `https://www.google.com/maps/dir/?api=1&destination=${LANDING_MAPS_PLACE_QUERY}`

/** Light embed for the homepage visit band (no API key). */
export const LANDING_MAPS_EMBED_URL =
  `https://maps.google.com/maps?q=${LANDING_MAPS_PLACE_QUERY}&hl=en&z=16&output=embed`

export const singleTreatments: LandingPackage[] = [
  {
    name: 'Facial',
    text: '60 minutes tailored to your skin.',
    price: 'From KES 2,500',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: LANDING_PRIMARY_CTA,
    includes: ['Skin consultation', 'Cleanse & exfoliation', 'Mask & moisturise'],
  },
  {
    name: 'Massage',
    text: 'Swedish or deep tissue. Back, neck and shoulders.',
    price: 'From KES 3,000',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: LANDING_PRIMARY_CTA,
    includes: ['30 or 60-minute session', 'Aromatherapy oils', 'Pressure to suit you'],
  },
  {
    name: 'Waxing',
    text: 'Face or body. Hot wax, neat finish.',
    price: 'From KES 1,200',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: LANDING_PRIMARY_CTA,
    includes: ['Brows, underarms or legs', 'After-care advice', 'Sensitive-skin options'],
  },
  {
    name: 'Makeup',
    text: 'Everyday polish or full glam for your occasion.',
    price: 'From KES 4,000',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: LANDING_PRIMARY_CTA,
    includes: ['Skin prep', 'Lash-friendly products', 'Touch-up tips'],
  },
]

export const bookingSteps = flowSteps

/** Reject copy that could break out of text nodes if ever user-sourced later. */
export function assertSafeDisplayText(value: string): boolean {
  return !/[<>]/.test(value) && !/javascript:/i.test(value)
}

export function validateTreatmentCards(list: LandingPackage[]): boolean {
  return (
    list.length >= 1 &&
    list.every(
      (p) =>
        p.includes.length >= 3 &&
        assertSafeDisplayText(p.name) &&
        assertSafeDisplayText(p.text) &&
        p.includes.every(assertSafeDisplayText),
    )
  )
}

export function validateLandingPackages(list: LandingPackage[]): boolean {
  return (
    list.length >= 3 &&
    list.some((p) => p.featured) &&
    validateTreatmentCards(list)
  )
}

/* ------------------------------------------------------------------ */
/* Design System Tokens, B&W Aesthetics & Loader Timing Contracts     */
/* ------------------------------------------------------------------ */

export function loaderSafetyTimeoutMs(minDuration: number): number {
  return minDuration + 1200
}

export interface MellisTypographyTokens {
  display: string
  script: string
  body: string
}

export interface MellisColorPalette {
  canvasPaper: string
  surfaceRaised: string
  cardDarkObsidian: string
  cardLightPorcelain: string
  ink: string
  muted: string
  roseGold: string
  roseGoldDark: string
}

export const MELLIS_TYPOGRAPHY: MellisTypographyTokens = {
  display: "var(--font-display, 'Fraunces', 'Libre Baskerville', serif)",
  script: "var(--font-script, 'Parisienne', cursive)",
  body: "var(--font-body, 'Manrope', sans-serif)",
}

export const MELLIS_PALETTE: MellisColorPalette = {
  canvasPaper: '#e5e1dc',
  surfaceRaised: '#ebe7e3',
  cardDarkObsidian: '#1e191b',
  cardLightPorcelain: '#fcf8f5',
  ink: '#2c2c30',
  muted: '#6e6764',
  roseGold: '#b07a71',
  roseGoldDark: '#965f57',
}

export function validateMellisDesignSystem(
  typography: MellisTypographyTokens = MELLIS_TYPOGRAPHY,
  palette: MellisColorPalette = MELLIS_PALETTE,
): boolean {
  return (
    typography.display.includes('font-display') &&
    typography.body.includes('font-body') &&
    palette.canvasPaper === '#e5e1dc' &&
    palette.cardDarkObsidian === '#1e191b' &&
    palette.cardLightPorcelain === '#fcf8f5'
  )
}

export const BW_MAKEUP_FILTER_STAGE = 'grayscale(1) contrast(1.22) brightness(0.78)'
export const BW_MAKEUP_FILTER_VISIT = 'grayscale(1) contrast(1.15) brightness(0.65)'
export const BLACK_FLOWER_PATTERN_URL = '/images/flower.png'

export interface FeaturedDarkCardCanvas {
  background: string
  patternUrl: string
  borderColor: string
  topBorder: string
  titleColor: string
  priceColor: string
}

export const FEATURED_CARD_DARK_CANVAS: FeaturedDarkCardCanvas = {
  background:
    'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(222, 150, 141, 0.15), transparent 60%), linear-gradient(165deg, #241d1f 0%, #1a1516 50%, #120e0f 100%)',
  patternUrl: BLACK_FLOWER_PATTERN_URL,
  borderColor: 'rgba(222, 150, 141, 0.35)',
  topBorder: '4px solid var(--color-rose)',
  titleColor: '#fcf8f5',
  priceColor: '#f0b8ac',
}

export function validateBwMakeupFilter(filter: string): boolean {
  return typeof filter === 'string' && filter.includes('grayscale(1)')
}

export function validateFeaturedDarkCardCanvas(
  canvas: FeaturedDarkCardCanvas = FEATURED_CARD_DARK_CANVAS,
): boolean {
  return (
    typeof canvas === 'object' &&
    canvas.background.includes('#120e0f') &&
    canvas.patternUrl === BLACK_FLOWER_PATTERN_URL &&
    canvas.titleColor === '#fcf8f5'
  )
}

