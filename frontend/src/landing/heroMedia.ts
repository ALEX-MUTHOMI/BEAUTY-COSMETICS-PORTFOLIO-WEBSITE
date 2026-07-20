/**
 * Homepage hero — Mellis-style ambient fade gallery.
 *
 * Inspected from https://mellis.ovathemewp.com/ (Revolution Slider):
 * - Stack: white mark → uppercase Manrope eyebrow → Parisienne script title → rose CTA
 * - Slide change: opacity fade (~1500ms); data-out o:0 / data-in o:0
 * - Title font: Parisienne; body/UI: Manrope
 * - CTA: #DE968D, 0 radius, uppercase Manrope
 *
 * Shee titles: "Shee Facials" | "Shee Massage" | "Shee Waxing" | "Shee Makeup"
 */

export type HeroService = 'facial' | 'massage' | 'waxing' | 'makeup'

/** Layout + motion contract aligned to Mellis RS hero. */
export const HERO_LAYOUT = {
  mobileHeightCss: 'min(78dvh, 40rem)',
  minHeightRem: 28,
  tabletHeightCss: 'min(72vh, 42rem)',
  desktopHeightCss: 'min(78vh, 46rem)',
  /** Soft full-frame dim like Mellis slide overlay (~25–35%). */
  overlayMidMax: 0.28,
  overlayBottomMax: 0.42,
  /** Photo + copy crossfade — slower than RS default so it feels calm. */
  fadeMs: 1800,
  /**
   * Seam into the page — wave clip (not ash/smoke gradient).
   * Kept for contract checks; CSS uses an SVG wave, not a fog %.
   */
  blendFadePercent: 0,
  seam: 'wave' as const,
} as const

export interface HeroSlide {
  service: HeroService
  serviceTitle: string
  /** Full script headline — "Shee Massage". */
  headline: string
  /** Uppercase Manrope eyebrow above the script title. */
  eyebrow: string
  image: string
  width: number
  height: number
  srcset: string
  sizes: string
  objectPosition: string
  alt: string
  photoBrief: string
}

const HERO_SIZES = '100vw'
const SHARED_EYEBROW = 'Ideal place to unwind'

function heroSrcset(basePath: string): string {
  return `${basePath} 1600w`
}

function slide(
  service: HeroService,
  serviceTitle: string,
  image: string,
  width: number,
  height: number,
  objectPosition: string,
  alt: string,
  photoBrief: string,
): HeroSlide {
  return {
    service,
    serviceTitle,
    headline: `Shee ${serviceTitle}`,
    eyebrow: SHARED_EYEBROW,
    image,
    width,
    height,
    srcset: heroSrcset(image),
    sizes: HERO_SIZES,
    objectPosition,
    alt,
    photoBrief,
  }
}

/** Mellis-style CTA under the script title. */
export const HERO_CTA = {
  label: 'Discover more',
  to: '/services',
} as const

export function formatHeroHeadline(slide: Pick<HeroSlide, 'serviceTitle' | 'headline'>): string {
  return slide.headline || `Shee ${slide.serviceTitle}`
}

export const heroSlides: HeroSlide[] = [
  slide(
    'facial',
    'Facials',
    '/images/hero-facial.jpg',
    1600,
    1067,
    'center 28%',
    'Facial treatment at Shee Aesthetics',
    'Facial in progress. Warm light.',
  ),
  slide(
    'massage',
    'Massage',
    '/images/hero-massage.jpg',
    1200,
    1800,
    'center 30%',
    'Therapist applying warm oil during a back massage',
    'Hands-on back/shoulder massage.',
  ),
  slide(
    'waxing',
    'Waxing',
    '/images/service-waxing.jpg',
    1200,
    1200,
    'center 40%',
    'Waxing treatment at Shee Aesthetics',
    'Clearly waxing.',
  ),
  slide(
    'makeup',
    'Makeup',
    '/images/hero-makeup.jpg',
    1600,
    1067,
    'center 32%',
    'Makeup artist finishing a soft glam look',
    'Makeup brush or lipstick — unmistakably glam.',
  ),
]

/**
 * Time between slide advances (includes crossfade).
 * Slow enough to read the title; not a screensaver.
 */
export const HERO_FADE_MS = 5600

/** Crossfade duration — calm Mellis-style opacity fade. */
export const HERO_CROSSFADE_MS = HERO_LAYOUT.fadeMs

/** Content layer fade (mark / eyebrow / title / CTA). */
export const HERO_COPY_FADE_MS = 1100

export function getHeroLcpHref(): string {
  return heroSlides[0]?.image ?? '/images/hero-facial.jpg'
}

export function shouldMountHeroImage(_activeIndex: number, _index: number, total: number): boolean {
  return total > 0
}

export function assertHeroServiceMatch(slides: HeroSlide[] = heroSlides): boolean {
  const required: HeroService[] = ['facial', 'massage', 'waxing', 'makeup']
  if (slides.length !== required.length) return false
  return slides.every((entry, i) => {
    const expected = required[i]
    if (!expected || entry.service !== expected) return false
    if (!entry.image.toLowerCase().includes(expected === 'waxing' ? 'wax' : expected)) return false
    if (formatHeroHeadline(entry) !== `Shee ${entry.serviceTitle}`) return false
    if (!entry.headline.startsWith('Shee ')) return false
    if (!entry.eyebrow || entry.eyebrow.length < 8) return false
    return entry.alt.length > 10
  })
}

export function assertHeroImagesAreLocal(slides: HeroSlide[] = heroSlides): boolean {
  return slides.every((entry) => {
    const path = entry.image
    if (!path.startsWith('/images/')) return false
    if (path.includes('..') || path.includes('\\') || path.includes('//')) return false
    if (/[\s<>"'`]/.test(path)) return false
    return true
  })
}

export function assertHeroLayoutPhotoForward(
  layout: typeof HERO_LAYOUT = HERO_LAYOUT,
): boolean {
  return (
    layout.overlayBottomMax <= 0.5 &&
    layout.overlayMidMax <= 0.35 &&
    layout.minHeightRem >= 28 &&
    layout.fadeMs >= 1600 &&
    layout.fadeMs <= 2200 &&
    layout.blendFadePercent === 0 &&
    layout.seam === 'wave' &&
    layout.mobileHeightCss.includes('78dvh')
  )
}

/** Dwell must feel unhurried once crossfade is subtracted. */
export function assertHeroTiming(
  fadeMs: number = HERO_FADE_MS,
  crossfadeMs: number = HERO_CROSSFADE_MS,
): boolean {
  if (fadeMs < 5000 || fadeMs > 7000) return false
  if (crossfadeMs < 1600 || crossfadeMs > 2200) return false
  const settled = fadeMs - crossfadeMs
  return settled >= 2800 && settled <= 5200
}
