/**
 * Module: bookingIdempotency
 * Ensures booking idempotency.
 */
/**
 * @module bookingIdempotency
 * Helpers for enforcing idempotency during booking submissions.
 */
import { stableActionKey } from '../staff/botGuard'

const IDEMPOTENCY_MAX_LENGTH = 128

/** Stable per slot attempt — survives double-clicks without creating duplicate holds. */
export function buildHoldIdempotencyKey(input: {
  selectionPublicId: string
  startsAt: string
  resourcePublicId: string
  attemptNonce: string
}): string {
  return stableActionKey([
    'hold',
    input.selectionPublicId,
    input.startsAt,
    input.resourcePublicId,
    input.attemptNonce,
  ]).slice(0, IDEMPOTENCY_MAX_LENGTH)
}

/** Stable per held booking — safe checkout retries after network blips. */
export function buildCheckoutIdempotencyKey(bookingPublicId: string): string {
  return stableActionKey(['checkout', bookingPublicId]).slice(0, IDEMPOTENCY_MAX_LENGTH)
}

/** Stable per checkout STK attempt — safe retries without duplicate provider spam. */
export function buildStkIdempotencyKey(checkoutPublicId: string, attemptNonce: string): string {
  return stableActionKey(['stk', checkoutPublicId, attemptNonce]).slice(0, IDEMPOTENCY_MAX_LENGTH)
}

export function createBookingAttemptNonce(): string {
  return crypto.randomUUID()
}

