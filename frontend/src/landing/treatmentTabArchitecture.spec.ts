import { describe, expect, it } from 'vitest'
import {
  TREATMENT_TAB_CONTRACT,
  validateTreatmentTabArchitecture,
} from './treatmentTabArchitecture'

describe('treatmentTabArchitecture', () => {
  it('enforces ultra-slim category tab height bounds (<= 3.5rem)', () => {
    expect(validateTreatmentTabArchitecture(TREATMENT_TAB_CONTRACT)).toBe(true)
    expect(parseFloat(TREATMENT_TAB_CONTRACT.maxTabHeight)).toBeLessThanOrEqual(3.5)
  })

  it('restricts treatment row vertical padding to compact density', () => {
    expect(parseFloat(TREATMENT_TAB_CONTRACT.maxRowPaddingY)).toBeLessThanOrEqual(0.75)
  })
})
