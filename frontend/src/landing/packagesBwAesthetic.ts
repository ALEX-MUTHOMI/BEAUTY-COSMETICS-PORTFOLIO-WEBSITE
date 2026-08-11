/**
 * B&W Makeup background & Black Flower card design tokens and validation utilities.
 * Enforces editorial high-contrast B&W makeup photography atmosphere and
 * luxury black flower paper card aesthetic across device viewports.
 */

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

export const MOBILE_CARD_PADDING_CLAMP = 'clamp(1.15rem, 4vw, 1.45rem)'
export const MOBILE_CARD_TITLE_CLAMP = 'clamp(1.25rem, 5.2vw, 1.55rem)'

export function validateBwMakeupFilter(filter: string): boolean {
  return typeof filter === 'string' && filter.includes('grayscale(1)')
}

export function validateFeaturedDarkCardCanvas(canvas: FeaturedDarkCardCanvas): boolean {
  return (
    typeof canvas === 'object' &&
    canvas.background.includes('#120e0f') &&
    canvas.patternUrl === BLACK_FLOWER_PATTERN_URL &&
    canvas.titleColor === '#fcf8f5'
  )
}
