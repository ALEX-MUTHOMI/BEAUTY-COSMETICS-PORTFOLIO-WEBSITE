import { describe, expect, it } from 'vitest'

import { loaderSafetyTimeoutMs } from './loaderTiming'

describe('landing loader timing contract', () => {
  it('always dismisses within minDuration plus safety window', () => {
    expect(loaderSafetyTimeoutMs(420)).toBe(1620)
    expect(loaderSafetyTimeoutMs(1000)).toBe(2200)
  })
})
