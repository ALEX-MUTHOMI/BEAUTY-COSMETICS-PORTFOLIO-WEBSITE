import { computed, onBeforeUnmount, ref, watch, type Ref } from 'vue'
import { createClickGate } from '@/staff/botGuard'
import { ensureBookingCsrfToken } from './bookingCsrf'
import type { BookingCustomerValidation } from './bookingCustomer'
import { validateBookingCustomer } from './bookingCustomer'
import {
  buildCheckoutIdempotencyKey,
  buildHoldIdempotencyKey,
  buildStkIdempotencyKey,
  createBookingAttemptNonce,
} from './bookingIdempotency'
import { GENERIC_BOOKING_THROTTLE_ERROR } from './bookingRequestGovernor'
import {
  createBookingCheckout,
  createBookingHold,
  fetchPolicyAcceptanceText,
  initiateBookingGuestStk,
  type BookingCheckoutResult,
} from './bookingWriteApi'
import type { BookingSlot, ResolvedSelection } from './bookingPublicApi'
import {
  BookingSubmitGovernor,
  GENERIC_BOOKING_SUBMIT_ERROR,
} from './bookingSubmitGovernor'

export type BookCheckoutStep = 'pick' | 'details' | 'submitting'

export function useBookCheckout(
  apiBaseUrl: string,
  selection: Ref<ResolvedSelection | null>,
  selectedSlot: Ref<BookingSlot | null>,
) {
  const submitGovernor = new BookingSubmitGovernor()
  const clickGate = createClickGate(1_200)
  let submitAbort: AbortController | null = null

  const step = ref<BookCheckoutStep>('pick')
  const attemptNonce = ref('')
  const policyText = ref('')
  const policyAccepted = ref(false)
  const turnstileToken = ref('')
  const turnstileRequired = ref(true)
  const submitError = ref<string | null>(null)
  const checkoutResult = ref<BookingCheckoutResult | null>(null)

  const customerForm = ref<BookingCustomerValidation>({
    fullName: '',
    email: '',
    emailConfirm: '',
    phone: '',
    honeypot: '',
  })

  const holdIdempotencyKey = computed(() => {
    if (!selection.value || !selectedSlot.value || !attemptNonce.value) return ''
    return buildHoldIdempotencyKey({
      selectionPublicId: selection.value.publicId,
      startsAt: selectedSlot.value.startsAt,
      resourcePublicId: selectedSlot.value.resourcePublicId,
      attemptNonce: attemptNonce.value,
    })
  })

  const canOpenDetails = computed(
    () => Boolean(selection.value && selectedSlot.value) && step.value === 'pick' && !submitGovernor.isInFlight,
  )

  const canSubmit = computed(() => {
    if (step.value !== 'details' || submitGovernor.isInFlight) return false
    if (!policyAccepted.value || !policyText.value) return false
    if (turnstileRequired.value && !turnstileToken.value) return false
    return Boolean(validateBookingCustomer(customerForm.value))
  })

  function abortInFlightSubmit() {
    submitAbort?.abort()
    submitAbort = null
  }

  async function loadPolicyText() {
    const result = await fetchPolicyAcceptanceText(apiBaseUrl)
    if ('data' in result) {
      policyText.value = result.data
    }
  }

  function openDetails() {
    if (!canOpenDetails.value) return
    if (!clickGate.canRun('open-details')) return
    attemptNonce.value = createBookingAttemptNonce()
    step.value = 'details'
    submitError.value = null
    void loadPolicyText()
    clickGate.finish('open-details')
  }

  function backToPick() {
    if (submitGovernor.isInFlight) {
      abortInFlightSubmit()
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
    }
    step.value = 'pick'
    submitError.value = null
    turnstileToken.value = ''
  }

  async function submitBooking(): Promise<BookingCheckoutResult | null> {
    if (!canSubmit.value || !selection.value || !selectedSlot.value || !holdIdempotencyKey.value) {
      return null
    }
    if (!clickGate.canRun('hold-checkout')) return null
    if (!submitGovernor.beginSubmit()) return null
    if (!submitGovernor.canAttemptHold()) {
      submitError.value = GENERIC_BOOKING_THROTTLE_ERROR
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    const customer = validateBookingCustomer(customerForm.value)
    if (!customer) {
      submitError.value = GENERIC_BOOKING_SUBMIT_ERROR
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    const csrfToken = await ensureBookingCsrfToken(apiBaseUrl)
    if (!csrfToken) {
      submitError.value = GENERIC_BOOKING_SUBMIT_ERROR
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    abortInFlightSubmit()
    submitAbort = new AbortController()
    const signal = submitAbort.signal

    step.value = 'submitting'
    submitError.value = null
    submitGovernor.recordHoldAttempt()

    const holdResult = await createBookingHold(
      apiBaseUrl,
      selection.value,
      selectedSlot.value,
      customer,
      holdIdempotencyKey.value,
      csrfToken,
      { turnstileToken: turnstileToken.value, signal },
    )

    if (signal.aborted) {
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    if ('error' in holdResult) {
      if (holdResult.throttled) {
        submitGovernor.markAbuseSuspected()
        turnstileRequired.value = true
        submitError.value = GENERIC_BOOKING_THROTTLE_ERROR
      } else {
        submitError.value = GENERIC_BOOKING_SUBMIT_ERROR
      }
      step.value = 'details'
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    submitGovernor.noteHoldTtlMinutes(holdResult.data.holdTtlMinutes)
    if (submitGovernor.abuseMode) {
      turnstileRequired.value = true
    }

    if (!submitGovernor.canAttemptCheckout()) {
      submitError.value = GENERIC_BOOKING_THROTTLE_ERROR
      step.value = 'details'
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    submitGovernor.recordCheckoutAttempt()

    const checkout = await createBookingCheckout(
      apiBaseUrl,
      holdResult.data.bookingPublicId,
      buildCheckoutIdempotencyKey(holdResult.data.bookingPublicId),
      policyText.value,
      csrfToken,
      { signal },
    )

    if (signal.aborted) {
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    if ('error' in checkout) {
      if (checkout.throttled) {
        submitGovernor.markAbuseSuspected()
        submitError.value = GENERIC_BOOKING_THROTTLE_ERROR
      } else {
        submitError.value = GENERIC_BOOKING_SUBMIT_ERROR
      }
      step.value = 'details'
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }

    // Guest-safe STK: phone must match booking customer (server HMAC). Fail closed on error
    // but still return checkout so status page can offer retry without orphaning the hold.
    if (checkout.data.nextAction === 'initiate_payment' || checkout.data.checkoutPublicId) {
      const stk = await initiateBookingGuestStk(
        apiBaseUrl,
        {
          bookingPublicId: checkout.data.bookingPublicId,
          checkoutPublicId: checkout.data.checkoutPublicId,
          phoneNumber: customer.phone,
          idempotencyKey: buildStkIdempotencyKey(
            checkout.data.checkoutPublicId,
            attemptNonce.value || createBookingAttemptNonce(),
          ),
        },
        csrfToken,
        { signal },
      )
      if (signal.aborted) {
        submitGovernor.finishSubmit()
        clickGate.finish('hold-checkout')
        return null
      }
      if ('error' in stk) {
        if (stk.throttled) {
          submitGovernor.markAbuseSuspected()
          submitError.value = GENERIC_BOOKING_THROTTLE_ERROR
        }
        // Still navigate to status — payment can be retried there.
      }
    }

    checkoutResult.value = checkout.data
    submitAbort = null
    submitGovernor.finishSubmit()
    clickGate.finish('hold-checkout')
    return checkout.data
  }

  watch(selectedSlot, () => {
    if (step.value === 'details' || step.value === 'submitting') {
      abortInFlightSubmit()
      submitGovernor.finishSubmit()
      step.value = 'pick'
      attemptNonce.value = ''
      turnstileToken.value = ''
      submitError.value = null
    }
  })

  watch(selection, () => {
    abortInFlightSubmit()
    submitGovernor.reset()
    step.value = 'pick'
    attemptNonce.value = ''
    checkoutResult.value = null
    turnstileToken.value = ''
    submitError.value = null
  })

  onBeforeUnmount(() => {
    abortInFlightSubmit()
  })

  return {
    step,
    policyText,
    policyAccepted,
    turnstileToken,
    turnstileRequired,
    submitError,
    checkoutResult,
    customerForm,
    canOpenDetails,
    canSubmit,
    isSubmitting: computed(() => submitGovernor.isInFlight || step.value === 'submitting'),
    abuseMode: computed(() => submitGovernor.abuseMode),
    openDetails,
    backToPick,
    submitBooking,
  }
}
