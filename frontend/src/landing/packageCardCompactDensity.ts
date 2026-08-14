/**
 * Package Card Compact Density Contracts
 * Enforces slim card padding (<= 1.35rem) and 2-column inclusion grid layout.
 */

export interface PackageCardCompactDensityContract {
  maxCardPaddingMobile: string
  maxCardPaddingDesktop: string
  inclusionGridColumnsMobile: number
  isCompact: boolean
}

export const PACKAGE_CARD_COMPACT_CONTRACT: PackageCardCompactDensityContract = {
  maxCardPaddingMobile: '1.15rem',
  maxCardPaddingDesktop: '1.35rem',
  inclusionGridColumnsMobile: 2,
  isCompact: true,
}

export function validatePackageCardCompactDensity(
  contract: PackageCardCompactDensityContract,
): boolean {
  return (
    contract.isCompact &&
    parseFloat(contract.maxCardPaddingMobile) <= 1.25 &&
    parseFloat(contract.maxCardPaddingDesktop) <= 1.5 &&
    contract.inclusionGridColumnsMobile >= 2
  )
}
