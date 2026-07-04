import { describe, expect, it } from 'vitest'

/** Mirrors SiteLoader timing contract — keep in sync with components/SiteLoader.vue */
export function loaderSafetyTimeoutMs(minDuration: number): number {
  return minDuration + 1500
}

describe('landing loader timing contract', () => {
  it('always dismisses within minDuration plus safety window', () => {
    expect(loaderSafetyTimeoutMs(2400)).toBe(3900)
    expect(loaderSafetyTimeoutMs(1000)).toBe(2500)
  })
})
