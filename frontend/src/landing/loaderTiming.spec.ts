import { describe, expect, it } from 'vitest'

import { loaderSafetyTimeoutMs } from './loaderTiming'

describe('landing loader timing contract', () => {
  it('always dismisses within minDuration plus safety window', () => {
    expect(loaderSafetyTimeoutMs(2400)).toBe(3900)
    expect(loaderSafetyTimeoutMs(1000)).toBe(2500)
  })
})
