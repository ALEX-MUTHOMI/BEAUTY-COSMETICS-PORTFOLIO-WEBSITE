/**
 * Non-Negotiable Mellis Theme Design System Tokens & Typography Architecture
 */

export interface MellisTypographyTokens {
  display: string
  script: string
  body: string
}

export interface MellisColorPalette {
  canvasPaper: string
  surfaceRaised: string
  cardDarkObsidian: string
  cardLightPorcelain: string
  ink: string
  muted: string
  roseGold: string
  roseGoldDark: string
}

export const MELLIS_TYPOGRAPHY: MellisTypographyTokens = {
  display: "var(--font-display, 'Fraunces', 'Libre Baskerville', serif)",
  script: "var(--font-script, 'Parisienne', cursive)",
  body: "var(--font-body, 'Manrope', sans-serif)",
}

export const MELLIS_PALETTE: MellisColorPalette = {
  canvasPaper: '#e5e1dc',
  surfaceRaised: '#ebe7e3',
  cardDarkObsidian: '#1e191b',
  cardLightPorcelain: '#fcf8f5',
  ink: '#2c2c30',
  muted: '#6e6764',
  roseGold: '#b07a71',
  roseGoldDark: '#965f57',
}

export function validateMellisDesignSystem(
  typography: MellisTypographyTokens,
  palette: MellisColorPalette,
): boolean {
  return (
    typography.display.includes('font-display') &&
    typography.body.includes('font-body') &&
    palette.canvasPaper === '#e5e1dc' &&
    palette.cardDarkObsidian === '#1e191b' &&
    palette.cardLightPorcelain === '#fcf8f5'
  )
}
