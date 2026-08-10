import { describe, expect, it } from 'vitest'
import {
  BLACK_FLOWER_PATTERN_URL,
  BW_MAKEUP_FILTER_STAGE,
  BW_MAKEUP_FILTER_VISIT,
  FEATURED_CARD_DARK_CANVAS,
  MOBILE_CARD_PADDING_CLAMP,
  validateBwMakeupFilter,
  validateFeaturedDarkCardCanvas,
} from './packagesBwAesthetic'

describe('packagesBwAesthetic design contract', () => {
  it('enforces a 100% black and white grayscale filter for stage makeup background', () => {
    expect(BW_MAKEUP_FILTER_STAGE).toContain('grayscale(1)')
    expect(validateBwMakeupFilter(BW_MAKEUP_FILTER_STAGE)).toBe(true)
  })

  it('enforces a matching black and white mono filter for visit door & carousel makeup image', () => {
    expect(BW_MAKEUP_FILTER_VISIT).toContain('grayscale(1)')
    expect(validateBwMakeupFilter(BW_MAKEUP_FILTER_VISIT)).toBe(true)
  })

  it('defines dark obsidian black paper canvas and black flower pattern for featured card', () => {
    expect(FEATURED_CARD_DARK_CANVAS.background).toContain('#120e0f')
    expect(FEATURED_CARD_DARK_CANVAS.patternUrl).toBe(BLACK_FLOWER_PATTERN_URL)
    expect(validateFeaturedDarkCardCanvas(FEATURED_CARD_DARK_CANVAS)).toBe(true)
  })

  it('provides fluid mobile card padding rules to prevent choking small screens', () => {
    expect(MOBILE_CARD_PADDING_CLAMP).toContain('clamp')
    expect(MOBILE_CARD_PADDING_CLAMP).toContain('rem')
  })
})
