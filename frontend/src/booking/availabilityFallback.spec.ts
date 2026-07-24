import { describe, expect, it } from 'vitest'

/**
 * Mirrors BookCheckoutPage showAvailabilityFallback — empty or errored calendar on pick step.
 */
function showAvailabilityFallback(input: {
  checkoutStep: string
  loading: boolean
  error: string | null
  dayCount: number
}): boolean {
  return (
    input.checkoutStep === 'pick' &&
    !input.loading &&
    (Boolean(input.error) || input.dayCount === 0)
  )
}

describe('book availability fail-open', () => {
  it('shows fallback when calendar is empty and not loading', () => {
    expect(
      showAvailabilityFallback({
        checkoutStep: 'pick',
        loading: false,
        error: null,
        dayCount: 0,
      }),
    ).toBe(true)
  })

  it('shows fallback when API error is set', () => {
    expect(
      showAvailabilityFallback({
        checkoutStep: 'pick',
        loading: false,
        error: 'Booking information is temporarily unavailable. Please try again.',
        dayCount: 3,
      }),
    ).toBe(true)
  })

  it('hides fallback while loading or on details step', () => {
    expect(
      showAvailabilityFallback({
        checkoutStep: 'pick',
        loading: true,
        error: null,
        dayCount: 0,
      }),
    ).toBe(false)
    expect(
      showAvailabilityFallback({
        checkoutStep: 'details',
        loading: false,
        error: null,
        dayCount: 0,
      }),
    ).toBe(false)
  })
})
