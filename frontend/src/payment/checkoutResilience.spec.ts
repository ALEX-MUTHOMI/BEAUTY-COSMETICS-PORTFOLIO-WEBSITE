import { describe, expect, it } from 'vitest'

import {
  buildStablePaymentRetryKey,
  checkoutUiState,
  DEFAULT_CHECKOUT_RESILIENCE,
  nextPollDelayMs,
  retryAfterDelayMs,
  shouldPollCheckoutStatus,
} from './checkoutResilience'

describe('checkout resilience', () => {
  it('does not spin forever when the provider or customer network is slow', () => {
    const state = checkoutUiState('stk_sent', 46000, {
      maxWaitMs: 45000,
      pollIntervalMs: 5000,
    })

    expect(state).toBe('TRY_AGAIN')
    expect(shouldPollCheckoutStatus(state)).toBe(true)
    expect(nextPollDelayMs(state)).toBe(5000)
  })

  it('maps terminal payment states without exposing provider identifiers', () => {
    expect(checkoutUiState('paid', 100000)).toBe('PAID')
    expect(checkoutUiState('failed', 100)).toBe('FAILED')
    expect(checkoutUiState('expired', 100)).toBe('EXPIRED')
  })

  it('uses a stable idempotency key for retries after reload', () => {
    expect(buildStablePaymentRetryKey('checkout-123')).toBe('stk:checkout-123')
    expect(buildStablePaymentRetryKey('checkout-123', 'existing-key')).toBe('existing-key')
  })

  it('honors a valid API retry hint and falls back safely for malformed hints', () => {
    expect(nextPollDelayMs('PAYMENT_PENDING', DEFAULT_CHECKOUT_RESILIENCE, '12')).toBe(12000)
    expect(retryAfterDelayMs('1')).toBe(5000)
    expect(retryAfterDelayMs('not-a-number')).toBe(5000)
    expect(nextPollDelayMs('PAID', DEFAULT_CHECKOUT_RESILIENCE, '12')).toBeNull()
  })
})
