/**
 * Module: checkoutResilience
 * Checkout retry and resilience logic.
 */
export type CheckoutBackendStatus =
  | 'created'
  | 'payment_pending'
  | 'stk_sent'
  | 'paid'
  | 'failed'
  | 'expired'
  | 'cancelled'

export type CheckoutUiState =
  | 'INITIATING'
  | 'STK_SENT'
  | 'PAYMENT_PENDING'
  | 'PAID'
  | 'FAILED'
  | 'EXPIRED'
  | 'TRY_AGAIN'

export interface CheckoutResilienceConfig {
  maxWaitMs: number
  pollIntervalMs: number
}

export const DEFAULT_CHECKOUT_RESILIENCE: CheckoutResilienceConfig = {
  maxWaitMs: 45000,
  pollIntervalMs: 5000,
}

export function checkoutUiState(
  backendStatus: CheckoutBackendStatus,
  elapsedMs: number,
  config: CheckoutResilienceConfig = DEFAULT_CHECKOUT_RESILIENCE,
): CheckoutUiState {
  if (backendStatus === 'paid') return 'PAID'
  if (backendStatus === 'failed' || backendStatus === 'cancelled') return 'FAILED'
  if (backendStatus === 'expired') return 'EXPIRED'
  if (elapsedMs >= config.maxWaitMs) return 'TRY_AGAIN'
  if (backendStatus === 'stk_sent') return 'STK_SENT'
  if (backendStatus === 'payment_pending') return 'PAYMENT_PENDING'
  return 'INITIATING'
}

export function shouldPollCheckoutStatus(uiState: CheckoutUiState): boolean {
  return uiState === 'STK_SENT' || uiState === 'PAYMENT_PENDING' || uiState === 'TRY_AGAIN'
}

export function nextPollDelayMs(
  uiState: CheckoutUiState,
  config: CheckoutResilienceConfig = DEFAULT_CHECKOUT_RESILIENCE,
  retryAfterHeader: string | null = null,
): number | null {
  return shouldPollCheckoutStatus(uiState) ? retryAfterDelayMs(retryAfterHeader, config) : null
}

/**
 * Honors the API's numeric Retry-After value without allowing malformed
 * headers to turn a transient rejection into a zero-delay retry loop.
 */
export function retryAfterDelayMs(
  retryAfterHeader: string | null,
  config: CheckoutResilienceConfig = DEFAULT_CHECKOUT_RESILIENCE,
): number {
  const retryAfterSeconds = Number(retryAfterHeader)
  if (!Number.isFinite(retryAfterSeconds) || retryAfterSeconds <= 0) {
    return config.pollIntervalMs
  }
  return Math.max(config.pollIntervalMs, Math.ceil(retryAfterSeconds * 1000))
}

export function buildStablePaymentRetryKey(checkoutId: string, existingKey?: string): string {
  return existingKey || `stk:${checkoutId}`
}

