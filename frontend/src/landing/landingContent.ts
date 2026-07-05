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

export interface HeroSlide {
  image: string
  eyebrow: string
  title: string
  subtitle?: string
  cta: string
  ctaTo: string
}

export interface FlowStep {
  num: string
  title: string
  text: string
  image: string
}

export const PACKAGE_DAYS = ['Tuesday', 'Wednesday'] as const

export const SINGLE_DAYS_LABEL = 'Mon · Thu – Sat'

/** Mellis Home 01 hero — script headline, eyebrow, Discover More */
export const heroSlides: HeroSlide[] = [
  {
    image: '/images/hero-1.jpg',
    eyebrow: 'Ideal place to unwind',
    title: 'Spa Beauty',
    cta: 'Discover More',
    ctaTo: '/#welcome',
  },
  {
    image: '/images/hero-2.jpg',
    eyebrow: 'Ideal place to unwind',
    title: 'Spa Care',
    cta: 'Discover More',
    ctaTo: '/#services',
  },
  {
    image: '/images/hero-3.jpg',
    eyebrow: 'Ideal place to unwind',
    title: 'Treat Yourself',
    cta: 'Discover More',
    ctaTo: '/#welcome',
  },
]

/** Mellis flow copy — short paragraphs under each step */
export const flowSteps: FlowStep[] = [
  {
    num: '01',
    title: 'Meeting',
    text: 'Book your appointment online or by phone. We confirm your date and the treatments in your visit.',
    image: '/images/step-meeting.jpg',
  },
  {
    num: '02',
    title: 'Treatment',
    text: 'Arrive a few minutes early. Your therapist explains each step before your facial, wax, massage or makeup.',
    image: '/images/step-treatment.jpg',
  },
  {
    num: '03',
    title: 'Finalizing',
    text: 'Settle your bill, schedule your next visit if you wish, and leave feeling refreshed.',
    image: '/images/step-finalizing.jpg',
  },
]

export const packageDayHeadline = 'Full Package Days'

export const packageDaySubhead =
  'Tuesdays and Wednesdays are for clients who want the full Shee visit — every treatment in one private room, without rushing between appointments.'

export const packageDayUrgency =
  'We keep these days for packages only. Slots are limited each week.'

export function isPackageDay(day: string): boolean {
  return PACKAGE_DAYS.some((d) => d.toLowerCase() === day.toLowerCase())
}

export const packages: LandingPackage[] = [
  {
    name: 'Classic Full Package',
    text: 'Our most booked visit — arrive once, leave with skin, body and makeup done.',
    price: 'From KES 12,000',
    badge: 'Most booked',
    featured: true,
    daysLabel: 'Tue & Wed only',
    ctaLabel: 'Book Package Day',
    includes: [
      'Deep cleansing facial',
      'Full body waxing',
      '60-minute massage',
      'Event-ready makeup',
      'Private treatment room',
    ],
  },
  {
    name: 'Glow Package',
    text: 'For events and photos — brighten skin, shape brows and finish with soft glam.',
    price: 'From KES 8,500',
    daysLabel: 'Tue & Wed only',
    ctaLabel: 'Book Package Day',
    includes: [
      'Brightening facial',
      'Brow shaping & wax',
      'Soft glam makeup',
      'Skin consultation',
    ],
  },
  {
    name: 'Relax Package',
    text: 'When you need to switch off — massage-led with wax and an express facial.',
    price: 'From KES 7,000',
    daysLabel: 'Tue & Wed only',
    ctaLabel: 'Book Package Day',
    includes: [
      'Deep tissue massage',
      'Back & shoulder wax',
      'Express facial',
      'Aromatherapy finish',
    ],
  },
]

export const singleTreatments: LandingPackage[] = [
  {
    name: 'Facial',
    text: '60 minutes tailored to your skin.',
    price: 'From KES 2,500',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: 'Book Facial',
    includes: ['Skin consultation', 'Cleanse & exfoliation', 'Mask & moisturise'],
  },
  {
    name: 'Massage',
    text: 'Swedish or deep tissue — back, neck and shoulders.',
    price: 'From KES 3,000',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: 'Book Massage',
    includes: ['30 or 60-minute session', 'Aromatherapy oils', 'Pressure to suit you'],
  },
  {
    name: 'Waxing',
    text: 'Face or body — hot wax, neat finish.',
    price: 'From KES 1,200',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: 'Book Waxing',
    includes: ['Brows, underarms or legs', 'After-care advice', 'Sensitive-skin options'],
  },
  {
    name: 'Makeup',
    text: 'Everyday polish or full glam for your occasion.',
    price: 'From KES 4,000',
    daysLabel: SINGLE_DAYS_LABEL,
    ctaLabel: 'Book Makeup',
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
