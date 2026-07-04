export interface LandingPackage {
  name: string
  text: string
  price: string
  includes: string[]
  featured?: boolean
  badge?: string
}

export const PACKAGE_DAYS = ['Tuesday', 'Wednesday'] as const

export const packageDayHeadline = 'Book Your Full Package Day'

export const packageDaySubhead =
  'Tuesdays and Wednesdays are reserved for full packages only — facial, waxing, massage and makeup in one private visit. Limited slots each week.'

export const packageDayUrgency =
  'These two days fill fast. If you want the full Shee experience, book Tue or Wed — singles are Mon, Thu–Sat.'

export function isPackageDay(day: string): boolean {
  return PACKAGE_DAYS.some((d) => d.toLowerCase() === day.toLowerCase())
}

export const packages: LandingPackage[] = [
  {
    name: 'Classic Full Package',
    text: 'Our signature full-day ritual — arrive once, leave fully done.',
    price: 'From KES 12,000',
    badge: 'Most booked',
    featured: true,
    includes: [
      'Deep cleansing facial',
      'Full body waxing',
      '60-min massage',
      'Event-ready makeup',
      'Private treatment room',
    ],
  },
  {
    name: 'Glow Package',
    text: 'Brighten, shape and glam — perfect before an event.',
    price: 'From KES 8,500',
    includes: [
      'Brightening facial',
      'Brow shaping & wax',
      'Soft glam makeup',
      'Skin consultation',
    ],
  },
  {
    name: 'Relax Package',
    text: 'Release tension and refresh — massage-led with express facial.',
    price: 'From KES 7,000',
    includes: [
      'Deep tissue massage',
      'Back & shoulder wax',
      'Express facial',
      'Aromatherapy finish',
    ],
  },
]

/** Reject copy that could break out of text nodes if ever user-sourced later. */
export function assertSafeDisplayText(value: string): boolean {
  return !/[<>]/.test(value) && !/javascript:/i.test(value)
}

export function validateLandingPackages(list: LandingPackage[]): boolean {
  return (
    list.length >= 3 &&
    list.some((p) => p.featured) &&
    list.every(
      (p) =>
        p.includes.length >= 3 &&
        assertSafeDisplayText(p.name) &&
        assertSafeDisplayText(p.text) &&
        p.includes.every(assertSafeDisplayText),
    )
  )
}
