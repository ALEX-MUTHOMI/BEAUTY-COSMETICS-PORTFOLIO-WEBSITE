/** Non-secret desk greeting helpers — never store passwords/tokens. */

const GREET_STORAGE_KEY = 'shee.desk.greet'

export function firstNameFromDisplay(value: string): string {
  const cleaned = String(value || '')
    .replace(/[^a-zA-Z0-9 ._-]+/g, ' ')
    .trim()
  if (!cleaned) return ''
  const first = cleaned.split(/[\s._-]+/).find(Boolean) || ''
  if (!first) return ''
  return first.charAt(0).toUpperCase() + first.slice(1).toLowerCase()
}

export function firstNameFromEmail(email: string): string {
  const local = String(email || '').split('@', 1)[0] || ''
  return firstNameFromDisplay(local)
}

export function readStoredGreetName(storage: Storage = localStorage): string {
  try {
    return firstNameFromDisplay(storage.getItem(GREET_STORAGE_KEY) || '')
  } catch {
    return ''
  }
}

export function writeStoredGreetName(name: string, storage: Storage = localStorage): void {
  const safe = firstNameFromDisplay(name)
  if (!safe) return
  try {
    storage.setItem(GREET_STORAGE_KEY, safe.slice(0, 32))
  } catch {
    // Ignore quota / private-mode failures.
  }
}

/** Login no longer shows a time-of-day lede; kept for call-site compat. */
export function timeOfDayLede(_now = new Date()): string {
  return ''
}

export function welcomeHeadline(storedName: string, typedEmail: string): string {
  // Typed email wins so the headline updates live as staff enter their address.
  const live = firstNameFromEmail(typedEmail)
  if (live) return `Welcome back, ${live}`
  const remembered = firstNameFromDisplay(storedName)
  if (remembered) return `Welcome back, ${remembered}`
  return 'Welcome back'
}

export { GREET_STORAGE_KEY }
