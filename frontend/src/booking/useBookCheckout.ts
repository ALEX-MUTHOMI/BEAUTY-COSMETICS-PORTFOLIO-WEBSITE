import { computed, onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'
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
import { trackFunnelEvent } from '@/landing/funnelEvents'
import {
  createHoldFromRememberedDevice,
  fetchRememberedDevice,
  forgetRememberedDevice,
  type RememberedDeviceState,
} from './rememberDevice'

export type BookCheckoutStep = 'pick' | 'details' | 'submitting'

function phoneLooksValid(phone: string): boolean {
  const digits = phone.replace(/\D/g, '')
  return digits.length >= 9 && digits.length <= 15
}

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
  const remembered = ref<RememberedDeviceState>({
    remembered: false,
    canUseSavedDetails: false,
    profileSummary: null,
  })
  const useSavedDetails = ref(false)

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
    if (customerForm.value.honeypot) return false
    if (useSavedDetails.value && remembered.value.canUseSavedDetails) {
      return phoneLooksValid(customerForm.value.phone)
    }
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

  async function loadRememberedDevice() {
    const result = await fetchRememberedDevice(apiBaseUrl)
    if ('error' in result) return
    remembered.value = result.data
    if (!result.data.remembered) {
      useSavedDetails.value = false
    }
  }

  function openDetails() {
    if (!canOpenDetails.value) return
    if (!clickGate.canRun('open-details')) return
    attemptNonce.value = createBookingAttemptNonce()
    step.value = 'details'
    submitError.value = null
    if (!policyText.value) void loadPolicyText()
    void loadRememberedDevice()
    clickGate.finish('open-details')
  }

  onMounted(() => {
    // Prefetch while client picks date/time so details opens without policy flash.
    void loadPolicyText()
    void ensureBookingCsrfToken(apiBaseUrl)
    void loadRememberedDevice()
  })

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

  async function chooseSavedDetails() {
    if (!remembered.value.canUseSavedDetails) return
    useSavedDetails.value = true
    submitError.value = null
  }

  async function chooseFreshDetails() {
    useSavedDetails.value = false
    const csrf = await ensureBookingCsrfToken(apiBaseUrl)
    if (csrf && remembered.value.remembered) {
      await forgetRememberedDevice(apiBaseUrl, csrf)
      remembered.value = { remembered: false, canUseSavedDetails: false, profileSummary: null }
    }
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

    const usingSaved = useSavedDetails.value && remembered.value.canUseSavedDetails
    const customer = usingSaved ? null : validateBookingCustomer(customerForm.value)
    if (!usingSaved && !customer) {
      submitError.value = GENERIC_BOOKING_SUBMIT_ERROR
      submitGovernor.finishSubmit()
      clickGate.finish('hold-checkout')
      return null
    }
    if (usingSaved && !phoneLooksValid(customerForm.value.phone)) {
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

    const holdResult = usingSaved
      ? await createHoldFromRememberedDevice(
          apiBaseUrl,
          selection.value,
          selectedSlot.value,
          holdIdempotencyKey.value,
          csrfToken,
          { signal },
        )
      : await createBookingHold(
          apiBaseUrl,
          selection.value,
          selectedSlot.value,
          customer!,
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
        if (usingSaved) {
          useSavedDetails.value = false
        }
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

    const stkPhone = usingSaved ? customerForm.value.phone.trim() : customer!.phone

    if (checkout.data.nextAction === 'initiate_payment' || checkout.data.checkoutPublicId) {
      const stk = await initiateBookingGuestStk(
        apiBaseUrl,
        {
          bookingPublicId: checkout.data.bookingPublicId,
          checkoutPublicId: checkout.data.checkoutPublicId,
          phoneNumber: stkPhone,
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
      } else {
        trackFunnelEvent('stk_sent', {
          booking: checkout.data.bookingPublicId,
          surface: 'checkout_initial',
        })
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
    remembered,
    useSavedDetails,
    canOpenDetails,
    canSubmit,
    isSubmitting: computed(() => submitGovernor.isInFlight || step.value === 'submitting'),
    abuseMode: computed(() => submitGovernor.abuseMode),
    openDetails,
    backToPick,
    chooseSavedDetails,
    chooseFreshDetails,
    submitBooking,
  }
}
