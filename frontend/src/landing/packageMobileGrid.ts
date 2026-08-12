/**
 * Package Mobile Grid Contracts
 * Defines token contracts for 100% full-width vertical mobile package stacking and 3-column desktop layout.
 */

export interface PackageGridContract {
  mobileLayout: string
  desktopLayout: string
  mobileWidth: string
}

export const PACKAGE_GRID_CONTRACT: PackageGridContract = {
  mobileLayout: 'grid-template-columns: 1fr',
  desktopLayout: 'grid-template-columns: repeat(3, 1fr)',
  mobileWidth: '100%',
}

export function validatePackageGridContract(contract: PackageGridContract): boolean {
  return (
    contract.mobileLayout.includes('1fr') &&
    contract.desktopLayout.includes('repeat(3, 1fr)') &&
    contract.mobileWidth === '100%'
  )
}
