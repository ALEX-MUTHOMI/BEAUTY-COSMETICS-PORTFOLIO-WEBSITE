import { describe, expect, it } from 'vitest'
import {
  MELLIS_PALETTE,
  MELLIS_TYPOGRAPHY,
  validateMellisDesignSystem,
} from './mellisDesignSystem'

describe('mellisDesignSystem', () => {
  it('enforces non-negotiable typography tokens for display, script, and body', () => {
    expect(MELLIS_TYPOGRAPHY.display).toContain('font-display')
    expect(MELLIS_TYPOGRAPHY.script).toContain('font-script')
    expect(MELLIS_TYPOGRAPHY.body).toContain('font-body')
  })

  it('enforces systemic color palette harmony between Obsidian and Porcelain cards', () => {
    expect(validateMellisDesignSystem(MELLIS_TYPOGRAPHY, MELLIS_PALETTE)).toBe(true)
    expect(MELLIS_PALETTE.cardLightPorcelain).toBe('#fcf8f5')
    expect(MELLIS_PALETTE.roseGold).toBe('#b07a71')
  })
})
