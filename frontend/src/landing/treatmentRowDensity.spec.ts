import { describe, expect, it } from 'vitest'
import {
  TREATMENT_ROW_CONTRACT,
  validateTreatmentRowDensity,
} from './treatmentRowDensity'

describe('treatmentRowDensity', () => {
  it('enforces unified dark obsidian theme without white zebra striping', () => {
    expect(validateTreatmentRowDensity(TREATMENT_ROW_CONTRACT)).toBe(true)
    expect(TREATMENT_ROW_CONTRACT.unifiedTheme).toBe('dark')
    expect(TREATMENT_ROW_CONTRACT.hasZebraStriping).toBe(false)
  })

  it('enforces thin row padding bounds and container breathing room', () => {
    expect(parseFloat(TREATMENT_ROW_CONTRACT.maxRowPaddingY)).toBeLessThanOrEqual(0.75)
    expect(parseFloat(TREATMENT_ROW_CONTRACT.maxContainerWidth)).toBeLessThanOrEqual(56)
  })
})
