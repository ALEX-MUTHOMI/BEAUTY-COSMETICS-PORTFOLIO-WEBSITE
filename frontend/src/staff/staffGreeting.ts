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

export function timeOfDayLede(now = new Date()): string {
  const hour = now.getHours()
  if (hour < 12) return 'Good morning — sign in to your desk.'
  if (hour < 17) return 'Good afternoon — sign in to your desk.'
  return 'Good evening — sign in to your desk.'
}

export function welcomeHeadline(storedName: string, typedEmail: string): string {
  const live = firstNameFromEmail(typedEmail)
  const name = storedName || live
  if (name) return `Welcome back, ${name}`
  return 'Welcome back'
}

export { GREET_STORAGE_KEY }
