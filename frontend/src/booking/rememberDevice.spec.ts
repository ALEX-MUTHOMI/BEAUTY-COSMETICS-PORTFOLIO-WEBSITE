import { describe, expect, it } from 'vitest'
import {
  REMEMBER_DEVICE_CUSTOMER_COPY,
} from './rememberDevice'

describe('rememberDevice contract', () => {
  it('keeps customer-facing copy without calling the profile an account', () => {
    expect(REMEMBER_DEVICE_CUSTOMER_COPY.toLowerCase()).not.toContain('account')
    expect(REMEMBER_DEVICE_CUSTOMER_COPY.toLowerCase()).toContain('device')
    expect(REMEMBER_DEVICE_CUSTOMER_COPY.length).toBeGreaterThan(40)
  })
})
