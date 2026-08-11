/**
 * Mobile Responsive Cards & Ivory/Obsidian Design System
 * Defines token contracts for flawless mobile card density and Ivory Porcelain / Black Obsidian card harmony.
 */

export interface CardThemeTokens {
  name: string
  background: string
  border: string
  textColor: string
  accentColor: string
  flowerOverlayOpacity: number
}

export const BLACK_OBSIDIAN_THEME: CardThemeTokens = {
  name: 'dark',
  background: 'linear-gradient(165deg, #241d1f 0%, #1a1516 50%, #120e0f 100%)',
  border: '1px solid rgba(222, 150, 141, 0.35)',
  textColor: '#fcf8f5',
  accentColor: '#f0b8ac',
  flowerOverlayOpacity: 0.18,
}

export const IVORY_PORCELAIN_THEME: CardThemeTokens = {
  name: 'light',
  background: 'linear-gradient(165deg, #f7f1eb 0%, #ebe3db 52%, #dfd6cd 100%)',
  border: '1px solid rgba(176, 122, 113, 0.35)',
  textColor: '#1f1a1b',
  accentColor: '#b56b62',
  flowerOverlayOpacity: 0.14,
}

export function validateCardHarmony(dark: CardThemeTokens, light: CardThemeTokens): boolean {
  return (
    dark.flowerOverlayOpacity > 0 &&
    light.flowerOverlayOpacity > 0 &&
    typeof dark.textColor === 'string' &&
    typeof light.textColor === 'string'
  )
}
