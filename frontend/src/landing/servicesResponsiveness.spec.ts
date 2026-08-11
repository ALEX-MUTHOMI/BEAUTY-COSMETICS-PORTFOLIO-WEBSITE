import { describe, expect, it } from 'vitest'
import {
  COMPACT_DOOR_HEIGHT_DESKTOP,
  COMPACT_DOOR_HEIGHT_MOBILE,
  SERVICES_THEME_CONTRACT,
  UNIFIED_SERVICES_BG,
  validateServicesTheme,
} from './servicesResponsiveness'

describe('servicesResponsiveness', () => {
  it('enforces unified --color-paper background across services page sections', () => {
    expect(UNIFIED_SERVICES_BG).toContain('color-paper')
    expect(validateServicesTheme(SERVICES_THEME_CONTRACT)).toBe(true)
  })

  it('restricts top chooser door card height to compact bounds', () => {
    expect(parseFloat(COMPACT_DOOR_HEIGHT_MOBILE)).toBeLessThanOrEqual(7.0)
    expect(parseFloat(COMPACT_DOOR_HEIGHT_DESKTOP)).toBeLessThanOrEqual(8.0)
  })
})
