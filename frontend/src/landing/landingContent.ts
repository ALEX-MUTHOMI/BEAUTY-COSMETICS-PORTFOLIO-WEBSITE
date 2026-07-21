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
  image: string
}

export const LANDING_PRIMARY_CTA = 'Book your visit'

export const LANDING_INSTAGRAM_URL = 'https://www.instagram.com/shee_aesthetics/'

export const LANDING_LOCATION_LABEL = 'Meru Town, Meru County'

export const LANDING_ADDRESS_LINES = ['Meru Town', 'Meru County, Kenya'] as const

export const PACKAGE_DAYS = ['Tuesday', 'Wednesday'] as const

export const SINGLE_DAYS_LABEL = 'Mon · Thu – Sat'

export { heroSlides, type HeroSlide } from './heroMedia'

export const flowSteps: FlowStep[] = [
  {
    num: '01',
    title: 'Choose online',
    text: 'Pick a date, treatment or package, then check out.',
    image: '/images/step-meeting.jpg',
  },
  {
    num: '02',
    title: 'Your treatment',
    text: 'Arrive a few minutes early. Your therapist guides each step.',
    image: '/images/step-treatment.jpg',
  },
  {
    num: '03',
    title: 'Leave glowing',
    text: 'Payment confirms your slot. A receipt arrives by email.',
    image: '/images/step-finalizing.jpg',
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

export const packages: LandingPackage[] = [
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
