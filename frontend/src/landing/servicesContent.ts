import {
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
  SINGLE_DAYS_LABEL,
  assertSafeDisplayText,
} from './landingContent'
import { SERVICES_ROUTES, type ServiceCategoryId } from './servicesNavigation'

export interface ServiceTreatment {
  name: string
  description: string
  duration: string
  price: string
  highlights: string[]
}

export interface ServiceCategory {
  id: string
  name: string
  cardTitle: string
  intro: string
  image: string
  icon: string
  imageAlt: string
  daysNote: string
  treatments: ServiceTreatment[]
}

export const SERVICES_PAGE_INTRO = {
  eyebrow: LANDING_LOCATION_LABEL,
  title: 'How would you like to visit?',
  lead: 'Every visit is in a private, calm room.',
}

export const serviceCategories: ServiceCategory[] = [
  {
    id: 'facials',
    name: 'Facial care',
    cardTitle: 'Facial Care',
    intro:
      'Skin-first facials tailored to your type — from deep cleanse to brightening and hydration. We start with a consultation so every step suits you.',
    image: '/images/service-facial.jpg',
    icon: '/images/icon-facial.png',
    imageAlt: 'Client receiving a relaxing facial treatment',
    daysNote: SINGLE_DAYS_LABEL,
    treatments: [
      {
        name: 'Deep cleansing facial',
        description:
          'Thorough cleanse, steam, exfoliation and extractions where needed. Finishes with a calming mask and moisturiser.',
        duration: '60 min',
        price: 'From KES 2,500',
        highlights: ['Skin analysis', 'Steam & extractions', 'Custom mask'],
      },
      {
        name: 'Brightening facial',
        description:
          'For dull or uneven tone. Gentle exfoliation and brightening actives to revive tired skin before events.',
        duration: '60 min',
        price: 'From KES 3,000',
        highlights: ['Tone correction', 'Vitamin-rich serums', 'SPF finish'],
      },
      {
        name: 'Hydrating facial',
        description:
          'Quenches dry or dehydrated skin with layered hydration, massage and a rich moisture barrier.',
        duration: '60 min',
        price: 'From KES 2,800',
        highlights: ['Hyaluronic boost', 'Face & neck massage', 'Barrier repair'],
      },
      {
        name: 'Express facial',
        description:
          'When time is short. Cleanse, exfoliate, mask and go — ideal between full package days or before makeup.',
        duration: '30 min',
        price: 'From KES 1,800',
        highlights: ['Quick refresh', 'No downtime', 'Makeup-ready skin'],
      },
      {
        name: 'Anti-ageing rejuvenation',
        description:
          'Firming massage, targeted serums and a lifting mask to soften fine lines and restore radiance.',
        duration: '75 min',
        price: 'From KES 3,500',
        highlights: ['Lifting massage', 'Collagen-focused care', 'Neck & décolletage'],
      },
    ],
  },
  {
    id: 'massage',
    name: 'Massage',
    cardTitle: 'Massages',
    intro:
      'Swedish and deep tissue work for back, neck and shoulders — or a full-body reset when you need to switch off.',
    image: '/images/service-massage.jpg',
    icon: '/images/icon-massage.png',
    imageAlt: 'Therapist performing a back massage',
    daysNote: SINGLE_DAYS_LABEL,
    treatments: [
      {
        name: 'Swedish massage',
        description:
          'Long, flowing strokes to ease tension and improve circulation. Pressure adjusted to your comfort.',
        duration: '30 or 60 min',
        price: 'From KES 3,000',
        highlights: ['Full back & shoulders', 'Aromatherapy oils', 'Gentle pressure'],
      },
      {
        name: 'Deep tissue massage',
        description:
          'Focused work on knots and tight muscle groups. Best for desk strain, post-workout soreness or chronic tension.',
        duration: '60 min',
        price: 'From KES 3,500',
        highlights: ['Targeted knots', 'Slow, firm pressure', 'After-care stretches'],
      },
      {
        name: 'Back, neck & shoulders',
        description:
          'Our most booked add-on. Concentrated relief where stress tends to sit — perfect on its own or with a facial.',
        duration: '30 min',
        price: 'From KES 2,200',
        highlights: ['Upper body focus', 'Hot towel finish', 'Quick turnaround'],
      },
      {
        name: 'Hot stone massage',
        description:
          'Heated stones melt tension while therapist works through back and shoulders. Deeply relaxing.',
        duration: '60 min',
        price: 'From KES 4,000',
        highlights: ['Heated basalt stones', 'Deep heat therapy', 'Aromatherapy blend'],
      },
    ],
  },
  {
    id: 'waxing',
    name: 'Waxing',
    cardTitle: 'Waxing',
    intro:
      'Face and body waxing with hot wax for a clean, lasting finish. Sensitive-skin options and after-care guidance included.',
    image: '/images/service-waxing.jpg',
    icon: '/images/icon-waxing.png',
    imageAlt: 'Professional waxing treatment setup',
    daysNote: SINGLE_DAYS_LABEL,
    treatments: [
      {
        name: 'Brow shaping',
        description:
          'Define and tidy brows with wax and precision tweezing. We map to your face shape for a natural arch.',
        duration: '20 min',
        price: 'From KES 800',
        highlights: ['Shape mapping', 'Wax & tweeze', 'Soothing balm'],
      },
      {
        name: 'Upper lip & chin',
        description: 'Quick facial wax for smooth, makeup-ready skin.',
        duration: '15 min',
        price: 'From KES 600',
        highlights: ['Hot wax', 'Sensitive options', 'Post-wax care'],
      },
      {
        name: 'Underarms',
        description: 'Clean, neat underarm wax with minimal discomfort and tidy regrowth.',
        duration: '15 min',
        price: 'From KES 1,200',
        highlights: ['Hot wax', 'Ingrown prevention tips', 'Soothing finish'],
      },
      {
        name: 'Half leg',
        description: 'Knee to ankle for smooth legs without the full session.',
        duration: '30 min',
        price: 'From KES 1,500',
        highlights: ['Strip & hot wax', 'Even finish', 'Moisturising oil'],
      },
      {
        name: 'Full leg',
        description: 'Complete leg wax from thigh to ankle. Popular before events and holidays.',
        duration: '45 min',
        price: 'From KES 2,500',
        highlights: ['Thorough coverage', 'Neat hairline', 'After-care sheet'],
      },
      {
        name: 'Bikini & Brazilian',
        description:
          'Discrete, professional body waxing with your comfort in mind. Options from bikini line to full Brazilian.',
        duration: '30–45 min',
        price: 'From KES 2,000',
        highlights: ['Private room', 'Hot wax', 'Hygiene-first setup'],
      },
      {
        name: 'Full body wax',
        description:
          'Legs, underarms, brows and chosen body areas in one visit. Also included in full packages.',
        duration: '90 min',
        price: 'From KES 6,500',
        highlights: ['Package favourite', 'Head-to-toe smooth', 'Single appointment'],
      },
    ],
  },
  {
    id: 'makeup',
    name: 'Makeup',
    cardTitle: 'Makeup',
    intro:
      'Everyday polish through to full bridal and event glam. Skin prep first so your look lasts in photos and in person.',
    image: '/images/service-makeup.jpg',
    icon: '/images/icon-makeup.png',
    imageAlt: 'Makeup artist applying glam makeup',
    daysNote: SINGLE_DAYS_LABEL,
    treatments: [
      {
        name: 'Everyday makeup',
        description:
          'Fresh, natural finish for work, brunch or errands. Enhances your features without looking overdone.',
        duration: '45 min',
        price: 'From KES 4,000',
        highlights: ['Skin prep', 'Lash-friendly products', 'Wear tips'],
      },
      {
        name: 'Soft glam',
        description:
          'Defined eyes, flawless base and a polished lip — perfect for dinners, graduations and photos.',
        duration: '60 min',
        price: 'From KES 5,500',
        highlights: ['Photo-ready base', 'Brow sculpt', 'Long-wear setting'],
      },
      {
        name: 'Bridal & event glam',
        description:
          'Full glam built to last through tears, dancing and flash photography. Trial sessions available on request.',
        duration: '90 min',
        price: 'From KES 8,000',
        highlights: ['Trial option', 'Water-resistant base', 'Touch-up kit advice'],
      },
      {
        name: 'Evening & photography makeup',
        description:
          'Bold, camera-friendly looks for shoots, parties and red-carpet moments. Contour and highlight balanced for lights.',
        duration: '75 min',
        price: 'From KES 6,500',
        highlights: ['HD-friendly finish', 'Custom lip & eye', 'Setting spray'],
      },
    ],
  },
]

export interface SingleTreatmentHighlight {
  category: ServiceCategoryId
  categoryName: string
  name: string
  description: string
  duration: string
  price: string
  highlights: string[]
}

/** One marquee, directly-bookable treatment per category for the homepage singles rail. */
const SINGLE_HIGHLIGHT_PICKS: Record<string, string> = {
  facials: 'Deep cleansing facial',
  massage: 'Back, neck & shoulders',
  waxing: 'Full leg',
  makeup: 'Soft glam',
}

export function getSingleTreatmentHighlights(): SingleTreatmentHighlight[] {
  return serviceCategories.map((category) => {
    const pick = SINGLE_HIGHLIGHT_PICKS[category.id]
    const treatment =
      category.treatments.find((t) => t.name === pick) ?? category.treatments[0]!
    return {
      category: category.id as ServiceCategoryId,
      categoryName: category.cardTitle,
      name: treatment.name,
      description: treatment.description,
      duration: treatment.duration,
      price: treatment.price,
      highlights: treatment.highlights,
    }
  })
}

export function getServiceSummaries() {
  return serviceCategories.map((category) => ({
    id: category.id,
    name: category.cardTitle,
    text: category.intro.split('.')[0] + '.',
    image: category.image,
    icon: category.icon,
    ctaTo: `${SERVICES_ROUTES.page}#${category.id}`,
    ctaLabel: `View ${category.cardTitle.toLowerCase()}`,
  }))
}

export function validateServiceCategories(list: ServiceCategory[]): boolean {
  return (
    list.length >= 4 &&
    list.every(
      (category) =>
        category.treatments.length >= 3 &&
        assertSafeDisplayText(category.name) &&
        assertSafeDisplayText(category.intro) &&
        category.treatments.every(
          (treatment) =>
            assertSafeDisplayText(treatment.name) &&
            assertSafeDisplayText(treatment.description) &&
            treatment.highlights.every(assertSafeDisplayText),
        ),
    )
  )
}

export { LANDING_PRIMARY_CTA }
