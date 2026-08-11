/**
 * Services Responsiveness & Color Uniformity Contracts
 * Defines token contracts for unified page background and compact door card density.
 */

export const UNIFIED_SERVICES_BG = 'var(--color-paper, #e5e1dc)'

export const COMPACT_DOOR_HEIGHT_MOBILE = '6.5rem'
export const COMPACT_DOOR_HEIGHT_DESKTOP = '7.5rem'

export interface ServicesPageThemeContract {
  unifiedBackground: string
  compactDoorHeightMobile: string
  compactDoorHeightDesktop: string
}

export const SERVICES_THEME_CONTRACT: ServicesPageThemeContract = {
  unifiedBackground: UNIFIED_SERVICES_BG,
  compactDoorHeightMobile: COMPACT_DOOR_HEIGHT_MOBILE,
  compactDoorHeightDesktop: COMPACT_DOOR_HEIGHT_DESKTOP,
}

export function validateServicesTheme(contract: ServicesPageThemeContract): boolean {
  return (
    contract.unifiedBackground.includes('color-paper') &&
    parseFloat(contract.compactDoorHeightMobile) <= 7.0 &&
    parseFloat(contract.compactDoorHeightDesktop) <= 8.0
  )
}
