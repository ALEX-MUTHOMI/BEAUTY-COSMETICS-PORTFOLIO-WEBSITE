import { describe, expect, it, vi } from 'vitest'

import {
  applyStaffTheme,
  nextStaffTheme,
  persistStaffTheme,
  readStoredStaffTheme,
  resolveStaffTheme,
  STAFF_THEME_STORAGE_KEY,
} from './theme'
import { storageContainsStaffSecrets } from './staffAuth'

describe('staff theme preference security contract', () => {
  it('persists only a non-sensitive theme preference', () => {
    localStorage.clear()

    persistStaffTheme('dark')

    expect(localStorage.getItem(STAFF_THEME_STORAGE_KEY)).toBe('dark')
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
  })

  it('falls back to system preference when no safe stored preference exists', () => {
    const storage = { getItem: vi.fn<Storage['getItem']>().mockReturnValue('token=secret') }
    const win = {
      matchMedia: vi.fn<Window['matchMedia']>().mockReturnValue({ matches: true } as MediaQueryList),
    }

    expect(readStoredStaffTheme(storage)).toBeNull()
    expect(resolveStaffTheme(storage, win)).toBe('dark')
  })

  it('applies and toggles light and dark themes', () => {
    const root = document.createElement('html')

    applyStaffTheme('dark', root)
    expect(root.getAttribute('data-staff-theme')).toBe('dark')
    expect(root.style.colorScheme).toBe('dark')
    expect(nextStaffTheme('dark')).toBe('light')
    expect(nextStaffTheme('light')).toBe('dark')

    applyStaffTheme('light', root)
    expect(root.getAttribute('data-staff-theme')).toBe('light')
    expect(root.style.colorScheme).toBe('light')
  })
})
