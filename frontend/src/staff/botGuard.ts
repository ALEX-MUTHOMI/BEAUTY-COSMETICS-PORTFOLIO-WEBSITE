export interface ClickGate {
  canRun(key: string, now?: number): boolean
  finish(key: string): void
  isRunning(key: string): boolean
}

export function createClickGate(cooldownMs = 900): ClickGate {
  const running = new Set<string>()
  const lastRun = new Map<string, number>()

  return {
    canRun(key: string, now = Date.now()) {
      if (running.has(key)) {
        return false
      }
      const previous = lastRun.get(key) || 0
      if (now - previous < cooldownMs) {
        return false
      }
      running.add(key)
      lastRun.set(key, now)
      return true
    },
    finish(key: string) {
      running.delete(key)
    },
    isRunning(key: string) {
      return running.has(key)
    },
  }
}

export function stableActionKey(parts: Array<string | number | undefined>): string {
  return parts.map((part) => String(part || 'none').replace(/[^a-zA-Z0-9:_-]/g, '')).join(':')
}
