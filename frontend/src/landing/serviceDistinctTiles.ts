/**
 * Service Distinct Tiles & 2x2 Category Grid Contracts
 * Enforces 100% screen-fitted 2x2 mobile category grid and distinct individual service tile boundaries.
 */

export interface ServiceDistinctTilesContract {
  mobileCategoryGridColumns: number
  desktopCategoryGridColumns: number
  tileMarginBottom: string
  tileBorderRadius: string
  hasIndividualTileSeparation: boolean
}

export const SERVICE_DISTINCT_TILES_CONTRACT: ServiceDistinctTilesContract = {
  mobileCategoryGridColumns: 2,
  desktopCategoryGridColumns: 4,
  tileMarginBottom: '0.65rem',
  tileBorderRadius: '10px',
  hasIndividualTileSeparation: true,
}

export function validateServiceDistinctTiles(
  contract: ServiceDistinctTilesContract,
): boolean {
  return (
    contract.mobileCategoryGridColumns === 2 &&
    contract.desktopCategoryGridColumns === 4 &&
    contract.hasIndividualTileSeparation &&
    parseFloat(contract.tileMarginBottom) >= 0.5 &&
    parseFloat(contract.tileBorderRadius) >= 8
  )
}
