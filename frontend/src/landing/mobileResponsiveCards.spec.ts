import { describe, expect, it } from 'vitest'
import {
  BLACK_OBSIDIAN_THEME,
  IVORY_PORCELAIN_THEME,
  validateCardHarmony,
} from './mobileResponsiveCards'

describe('mobileResponsiveCards', () => {
  it('defines Black Obsidian and Ivory Porcelain card themes with shared flower overlays', () => {
    expect(validateCardHarmony(BLACK_OBSIDIAN_THEME, IVORY_PORCELAIN_THEME)).toBe(true)
    expect(BLACK_OBSIDIAN_THEME.textColor).toBe('#fcf8f5')
    expect(IVORY_PORCELAIN_THEME.textColor).toBe('#1f1a1b')
  })

  it('ensures Ivory Porcelain card has high contrast text and rose gold accents', () => {
    expect(IVORY_PORCELAIN_THEME.accentColor).toBe('#b56b62')
    expect(IVORY_PORCELAIN_THEME.background).toContain('#f7f1eb')
  })
})
