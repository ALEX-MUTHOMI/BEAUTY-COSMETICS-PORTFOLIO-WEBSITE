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
  /**
   * Locked hero heights — do not ramble.
   * Mobile: 92dvh with a soft floor (short phones must not exceed viewport badly)
   * Tablet/iPad: 92vh
   * Desktop: 100vh
   * Floors only — never max-rem caps (those cut the photo on large screens).
   */
  mobileHeightCss: '92dvh',
  minHeightRem: 28,
  tabletHeightCss: '92vh',
  tabletMinHeightRem: 38,
  desktopHeightCss: '100vh',
  desktopMinHeightRem: 44,
  /** Soft full-frame dim — keep photos bright; copy still readable. */
  overlayMidMax: 0.22,
  overlayBottomMax: 0.34,
  /** Photo + copy crossfade — unhurried, luxurious. */
  fadeMs: 2800,
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
/** Pre-generated static widths — phones pick ≤960w without runtime IPX. */
export const HERO_SRCSET_WIDTHS = [640, 960, 1280] as const

export function heroVariantPath(basePath: string, width: number): string {
  return basePath.replace(/\.jpg$/i, `-${width}.jpg`)
}

function heroSrcset(basePath: string): string {
  const variants = HERO_SRCSET_WIDTHS.map((w) => `${heroVariantPath(basePath, w)} ${w}w`)
  return [...variants, `${basePath} 1600w`].join(', ')
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

/**
 * Hero photos — Kenyan beauty studio: Black / lightskin models, sharp aesthetic frames.
 * Order: Makeup first (hero arrival), then Facials, Massage, Waxing.
 */
export const heroSlides: HeroSlide[] = [
  slide(
    'makeup',
    'Makeup',
    '/images/hero-makeup.jpg',
    1440,
    1800,
    'center 28%',
    'Soft glam makeup look with dewy skin and glossy lips',
    'Sharp aesthetic glam portrait — unmistakably makeup.',
  ),
  slide(
    'facial',
    'Facials',
    '/images/hero-facial.jpg',
    1440,
    1920,
    'center 28%',
    'Black woman receiving a cream facial mask treatment in black and white',
    'Moody B&W spa facial — cream mask, gloved hands, towel wrap.',
  ),
  slide(
    'massage',
    'Massage',
    '/images/hero-massage.jpg',
    1600,
    1067,
    'center 32%',
    'Black woman relaxing during an oil back massage in black and white',
    'Moody B&W spa massage — oil sheen, serene close-up.',
  ),
  slide(
    'waxing',
    'Waxing',
    '/images/hero-waxing.jpg',
    1500,
    1700,
    'center 38%',
    'Therapist applying warm golden wax during a leg waxing treatment',
    'Warm spa waxing on deep skin — candlelight aesthetic.',
  ),
]

/**
 * Time between slide advances (includes crossfade).
 * Slow enough to watch the handwriting finish.
 */
export const HERO_FADE_MS = 9000

/** Crossfade duration — calm Mellis-style opacity fade. */
export const HERO_CROSSFADE_MS = HERO_LAYOUT.fadeMs

/** Content layer fade (eyebrow / title / CTA). */
export const HERO_COPY_FADE_MS = 1400

export function getHeroLcpHref(): string {
  const base = heroSlides[0]?.image ?? '/images/hero-makeup.jpg'
  return heroVariantPath(base, 960)
}

/** Full srcset for LCP preload imagesrcset. */
export function getHeroLcpSrcset(): string {
  return heroSlides[0]?.srcset ?? heroSrcset('/images/hero-makeup.jpg')
}

/**
 * Mount active + next only on first paint; callers may retain prior mounts for fade.
 */
export function shouldMountHeroImage(activeIndex: number, index: number, total: number): boolean {
  if (total <= 0) return false
  if (index === activeIndex) return true
  return index === (activeIndex + 1) % total
}

export function assertHeroServiceMatch(slides: HeroSlide[] = heroSlides): boolean {
  const required: HeroService[] = ['makeup', 'facial', 'massage', 'waxing']
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
    layout.minHeightRem >= 26 &&
    layout.minHeightRem <= 32 &&
    layout.tabletMinHeightRem >= 36 &&
    layout.desktopMinHeightRem >= 42 &&
    layout.fadeMs >= 2400 &&
    layout.fadeMs <= 3200 &&
    layout.blendFadePercent === 0 &&
    layout.seam === 'wave' &&
    layout.mobileHeightCss === '92dvh' &&
    layout.tabletHeightCss === '92vh' &&
    layout.desktopHeightCss === '100vh'
  )
}

/** Dwell must feel unhurried once crossfade is subtracted. */
export function assertHeroTiming(
  fadeMs: number = HERO_FADE_MS,
  crossfadeMs: number = HERO_CROSSFADE_MS,
): boolean {
  if (fadeMs < 7500 || fadeMs > 11000) return false
  if (crossfadeMs < 2400 || crossfadeMs > 3200) return false
  const settled = fadeMs - crossfadeMs
  return settled >= 4200 && settled <= 8000
}
