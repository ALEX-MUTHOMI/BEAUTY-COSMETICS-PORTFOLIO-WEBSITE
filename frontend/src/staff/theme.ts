export type StaffTheme = 'light' | 'dark'

export const STAFF_THEME_STORAGE_KEY = 'bc_theme_preference'

function isStaffTheme(value: unknown): value is StaffTheme {
  return value === 'light' || value === 'dark'
}

export function systemStaffTheme(win: Pick<Window, 'matchMedia'> | undefined = globalThis.window): StaffTheme {
  if (win?.matchMedia?.('(prefers-color-scheme: dark)').matches) {
    return 'dark'
  }
  return 'light'
}

export function readStoredStaffTheme(storage: Pick<Storage, 'getItem'> | undefined = globalThis.localStorage): StaffTheme | null {
  try {
    const value = storage?.getItem(STAFF_THEME_STORAGE_KEY)
    return isStaffTheme(value) ? value : null
  } catch {
    return null
  }
}

export function applyStaffTheme(theme: StaffTheme, root: HTMLElement | undefined = globalThis.document?.documentElement) {
  root?.setAttribute('data-staff-theme', theme)
}

export function resolveStaffTheme(
  storage: Pick<Storage, 'getItem'> | undefined = globalThis.localStorage,
  win: Pick<Window, 'matchMedia'> | undefined = globalThis.window,
): StaffTheme {
  return readStoredStaffTheme(storage) || systemStaffTheme(win)
}

export function persistStaffTheme(
  theme: StaffTheme,
  storage: Pick<Storage, 'setItem'> | undefined = globalThis.localStorage,
) {
  try {
    storage?.setItem(STAFF_THEME_STORAGE_KEY, theme)
  } catch {
    // Theme persistence is a convenience only. Never block portal access on it.
  }
}

export function nextStaffTheme(theme: StaffTheme): StaffTheme {
  return theme === 'dark' ? 'light' : 'dark'
}
