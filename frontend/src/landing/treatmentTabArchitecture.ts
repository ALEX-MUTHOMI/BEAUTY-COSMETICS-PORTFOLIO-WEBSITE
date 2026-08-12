/**
 * Treatment Tab & High-Density Architecture Contracts
 * Defines token contracts for ultra-slim category tabs (<= 3.5rem height) and compact treatment row density.
 */

export interface TreatmentTabArchitectureContract {
  maxTabHeight: string
  maxRowPaddingY: string
  tabActiveBorderColor: string
}

export const TREATMENT_TAB_CONTRACT: TreatmentTabArchitectureContract = {
  maxTabHeight: '3.25rem',
  maxRowPaddingY: '0.65rem',
  tabActiveBorderColor: 'var(--color-rose, #b07a71)',
}

export function validateTreatmentTabArchitecture(
  contract: TreatmentTabArchitectureContract,
): boolean {
  return (
    parseFloat(contract.maxTabHeight) <= 3.5 &&
    parseFloat(contract.maxRowPaddingY) <= 0.75 &&
    contract.tabActiveBorderColor.includes('rose')
  )
}
