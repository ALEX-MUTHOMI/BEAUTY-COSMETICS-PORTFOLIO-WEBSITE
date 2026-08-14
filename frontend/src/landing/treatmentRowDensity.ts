/**
 * Treatment Row Density & Theme Unification System
 * Eliminates alternating white blocks and enforces unified dark obsidian rows with thin density.
 */

export interface TreatmentRowDensityContract {
  unifiedTheme: 'dark'
  maxRowPaddingY: string
  maxContainerWidth: string
  hasZebraStriping: boolean
}

export const TREATMENT_ROW_CONTRACT: TreatmentRowDensityContract = {
  unifiedTheme: 'dark',
  maxRowPaddingY: '0.65rem',
  maxContainerWidth: '54rem',
  hasZebraStriping: false,
}

export function validateTreatmentRowDensity(contract: TreatmentRowDensityContract): boolean {
  return (
    contract.unifiedTheme === 'dark' &&
    !contract.hasZebraStriping &&
    parseFloat(contract.maxRowPaddingY) <= 0.75 &&
    parseFloat(contract.maxContainerWidth) <= 56
  )
}
