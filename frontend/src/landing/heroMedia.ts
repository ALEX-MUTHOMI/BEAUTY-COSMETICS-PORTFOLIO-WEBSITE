/**
 * Homepage hero media contract.
 *
 * Rules:
 * - One slide = one service. Title copy and image subject must match.
 * - Landscape-first assets; per-slide object-position keeps the treatment action in frame.
 * - No Ken Burns / scale motion on the image plane — stillness = trust for beauty brands.
 * - Stable filenames so a Meru photographer can drop replacements later.
 * - Only the active (+ neighbour) slides mount images to keep concurrent visits light.
 */

export type HeroService = 'facial' | 'massage' | 'makeup'

export interface HeroSlide {
  service: HeroService
  /** Desktop / default asset (LCP for slide 0). */
  image: string
  /** Optional tighter crop for narrow viewports. Falls back to `image`. */
  imageMobile?: string
  width: number
  height: number
  srcset: string
  sizes: string
  /** CSS object-position — keep faces / treatment action in frame. */
  objectPosition: string
  alt: string
  eyebrow: string
  title: string
  subtitle: string
  cta: string
  ctaTo: string
  /** Shot list for the future Meru photographer. */
  photoBrief: string
}

const LOCATION = 'Meru Town, Meru County'
const CTA = 'Book your visit'
const HERO_SIZES = '100vw'

function heroSrcset(basePath: string): string {
  return `${basePath} 1600w`
}

export const heroSlides: HeroSlide[] = [
  {
    service: 'facial',
    image: '/images/hero-facial.jpg',
    imageMobile: '/images/hero-facial.jpg',
    width: 1600,
    height: 1067,
    srcset: heroSrcset('/images/hero-facial.jpg'),
    sizes: HERO_SIZES,
    objectPosition: 'center center',
    alt: 'Aesthetician applying a facial treatment in a warm private room',
    eyebrow: LOCATION,
    title: 'Facials',
    subtitle: 'Deep cleanse, brightening and hydration in a private room',
    cta: CTA,
    ctaTo: '/services',
    photoBrief:
      'Landscape. Facial in progress. Warm private-room light. East African client. Face readable for centered title.',
  },
  {
    service: 'massage',
    image: '/images/hero-massage.jpg',
    imageMobile: '/images/hero-massage.jpg',
    width: 1200,
    height: 1800,
    srcset: heroSrcset('/images/hero-massage.jpg'),
    sizes: HERO_SIZES,
    objectPosition: 'center 30%',
    alt: 'Therapist applying warm oil during a back massage',
    eyebrow: LOCATION,
    title: 'Massage',
    subtitle: 'Swedish and deep tissue for back, neck and shoulders',
    cta: CTA,
    ctaTo: '/services',
    photoBrief:
      'Prefer landscape next shoot. Hands-on back/shoulder massage. Warm light. East African skin tones. Action mid-frame.',
  },
  {
    service: 'makeup',
    image: '/images/hero-makeup.jpg',
    imageMobile: '/images/hero-makeup.jpg',
    width: 1600,
    height: 1067,
    srcset: heroSrcset('/images/hero-makeup.jpg'),
    sizes: HERO_SIZES,
    objectPosition: 'center 32%',
    alt: 'Makeup artist applying lipstick during a private glam session',
    eyebrow: LOCATION,
    title: 'Makeup',
    subtitle: 'Everyday polish and full glam for events',
    cta: CTA,
    ctaTo: '/services',
    photoBrief:
      'Landscape. Makeup brush or lipstick on face — unmistakably glam, not massage. Warm studio light.',
  },
]

/** Future Meru shoot: add a 4th slide only when a true waxing frame exists. */
export const HERO_WAXING_BRIEF =
  'Landscape. Clearly waxing (wax pot, strip, or treated area) — never massage. Warm private room.'

export function getHeroLcpHref(): string {
  return heroSlides[0]?.image ?? '/images/hero-facial.jpg'
}

/** Active slide + neighbours mount so crossfade never flashes an empty ink plane. */
export function shouldMountHeroImage(activeIndex: number, index: number, total: number): boolean {
  if (total <= 0) return false
  if (index === activeIndex) return true
  if (index === (activeIndex + 1) % total) return true
  if (index === (activeIndex - 1 + total) % total) return true
  return false
}

export function assertHeroServiceMatch(slides: HeroSlide[] = heroSlides): boolean {
  const required: HeroService[] = ['facial', 'massage', 'makeup']
  if (slides.length !== required.length) return false
  return slides.every((slide, i) => {
    const expected = required[i]
    if (!expected || slide.service !== expected) return false
    if (!slide.image.includes(`hero-${expected}`)) return false
    const title = slide.title.toLowerCase()
    if (expected === 'facial' && !title.includes('facial')) return false
    if (expected === 'massage' && !title.includes('massage')) return false
    if (expected === 'makeup' && !title.includes('makeup')) return false
    return slide.alt.length > 10
  })
}
