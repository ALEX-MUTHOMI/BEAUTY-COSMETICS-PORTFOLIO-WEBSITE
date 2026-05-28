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
): number | null {
  return shouldPollCheckoutStatus(uiState) ? config.pollIntervalMs : null
}

export function buildStablePaymentRetryKey(checkoutId: string, existingKey?: string): string {
  return existingKey || `stk:${checkoutId}`
}
