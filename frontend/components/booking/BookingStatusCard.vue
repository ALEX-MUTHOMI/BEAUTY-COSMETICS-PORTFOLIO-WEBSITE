<template>
  <main class="book-status">
    <img
      :src="flowerSrc"
      alt=""
      class="book-status__bloom book-status__bloom--tl"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="120"
      height="120"
      decoding="async"
    />
    <img
      :src="flowerSrc"
      alt=""
      class="book-status__bloom book-status__bloom--br"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="140"
      height="140"
      decoding="async"
    />
    <section class="book-status__card" aria-live="polite">
      <p class="book-status__eyebrow">{{ modeLabel }}</p>
      <h1>{{ headline }}</h1>
      <p class="book-status__lead">{{ lead }}</p>

      <dl v-if="snapshot" class="book-status__meta">
        <div>
          <dt>Reference</dt>
          <dd>{{ shortReference }}</dd>
        </div>
        <div v-if="snapshot.serviceName">
          <dt>Service</dt>
          <dd>{{ snapshot.serviceName }}</dd>
        </div>
        <div v-if="snapshot.scheduleDate">
          <dt>When</dt>
          <dd>{{ snapshot.scheduleDate }} · {{ snapshot.scheduleTime }}</dd>
        </div>
      </dl>

      <p v-if="polling" class="book-status__polling">{{ BOOKING_STATUS_COPY.polling }}</p>
      <p v-if="error" class="book-status__error" role="alert">{{ error }}</p>
      <p v-if="stkMessage" class="book-status__polling" role="status">{{ stkMessage }}</p>

      <form v-if="canRetryStk" class="book-status__retry" @submit.prevent="retryStk">
        <label>
          {{ BOOKING_STATUS_COPY.retryLabel }}
          <input
            v-model="retryPhone"
            autocomplete="tel"
            inputmode="tel"
            name="phone"
            type="tel"
            required
          />
        </label>
        <button type="submit" class="book-status__retry-btn" :disabled="retrying">
          {{ retrying ? BOOKING_STATUS_COPY.retryingButton : BOOKING_STATUS_COPY.retryButton }}
        </button>
      </form>

      <div v-if="showRememberOptIn" class="book-status__remember">
        <label class="book-status__remember-label">
          <input v-model="rememberOptIn" type="checkbox" :disabled="rememberBusy || rememberDone" />
          <span>{{ rememberCopy }}</span>
        </label>
        <button
          type="button"
          class="book-status__remember-btn"
          :disabled="!rememberOptIn || rememberBusy || rememberDone"
          @click="saveRememberDevice"
        >
          {{ rememberDone ? 'Saved on this device' : rememberBusy ? 'Saving' : 'Save for next visit' }}
        </button>
        <p v-if="rememberMessage" class="book-status__polling" role="status">{{ rememberMessage }}</p>
      </div>

      <div class="book-status__actions">
        <SiteButton to="/" variant="outline">Home</SiteButton>
        <SiteButton
          :to="bookAgainHref"
          variant="primary"
          @click="trackFunnelEvent('book_again_click', { href: bookAgainHref })"
        >
          Book again
        </SiteButton>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { ensureBookingCsrfToken } from '@/booking/bookingCsrf'
import { buildStkIdempotencyKey, createBookingAttemptNonce } from '@/booking/bookingIdempotency'
import { isTerminalBookingStatus, pollBookingStatusUntilSettled } from '@/booking/bookingStatusPoll'
import {
  fetchBookingStatus,
  initiateBookingGuestStk,
  type BookingStatusSnapshot,
} from '@/booking/bookingWriteApi'
import { optInRememberDevice, REMEMBER_DEVICE_CUSTOMER_COPY } from '@/booking/rememberDevice'
import { lastBookHref, SERVICES_BOOK_ENTRY } from '@/landing/bookingHandoff'
import { BOOKING_STATUS_COPY, MELLIS_FLOWER_SRC } from '@/landing/clientPagesContent'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const flowerSrc = MELLIS_FLOWER_SRC

type BookingStatusMode = 'status' | 'confirmation'

const props = withDefaults(
  defineProps<{
    bookingPublicId: string
    mode?: BookingStatusMode
  }>(),
  { mode: 'status' },
)

const modeLabel = computed(() =>
  props.mode === 'confirmation'
    ? BOOKING_STATUS_COPY.confirmationEyebrow
    : BOOKING_STATUS_COPY.statusEyebrow,
)

const config = useRuntimeConfig()
const apiBaseUrl = (config.public.apiBaseUrl as string) || 'http://localhost:8000'

const publicId = computed(() => String(props.bookingPublicId ?? ''))
const bookAgainHref = computed(() => {
  if (!import.meta.client) return SERVICES_BOOK_ENTRY
  const last = lastBookHref()
  return last && last !== SERVICES_BOOK_ENTRY ? last : SERVICES_BOOK_ENTRY
})

const snapshot = ref<BookingStatusSnapshot | null>(null)
const checkoutPublicId = ref('')
const polling = ref(false)
const error = ref<string | null>(null)
const stkMessage = ref<string | null>(null)
const retryPhone = ref('')
const retrying = ref(false)
const abort = new AbortController()

const rememberOptIn = ref(false)
const rememberBusy = ref(false)
const rememberDone = ref(false)
const rememberMessage = ref<string | null>(null)
const rememberCopy = REMEMBER_DEVICE_CUSTOMER_COPY

const shortReference = computed(() => {
  const id = snapshot.value?.bookingReference ?? publicId.value
  return id ? id.slice(0, 8).toUpperCase() : BOOKING_STATUS_COPY.emptyReference
})

const isConfirmed = computed(
  () => snapshot.value?.bookingStatus === 'confirmed' || snapshot.value?.paymentStatus === 'paid',
)

const showRememberOptIn = computed(() => isConfirmed.value && !rememberDone.value)

const canRetryStk = computed(() => {
  if (!snapshot.value) return false
  if (isConfirmed.value) return false
  return (
    snapshot.value.paymentStatus === 'payment_pending' ||
    snapshot.value.nextAction === 'complete_mpesa_stk' ||
    snapshot.value.nextAction === 'initiate_payment'
  )
})

const headline = computed(() => {
  if (!snapshot.value) {
    return props.mode === 'confirmation'
      ? BOOKING_STATUS_COPY.confirmingHeadline
      : BOOKING_STATUS_COPY.loadingHeadline
  }
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return props.mode === 'confirmation'
      ? BOOKING_STATUS_COPY.confirmedConfirmationHeadline
      : BOOKING_STATUS_COPY.confirmedStatusHeadline
  }
  if (snapshot.value.paymentStatus === 'payment_failed') return BOOKING_STATUS_COPY.paymentFailedHeadline
  if (snapshot.value.paymentStatus === 'payment_pending') return BOOKING_STATUS_COPY.paymentPendingHeadline
  if (snapshot.value.bookingStatus === 'held') return BOOKING_STATUS_COPY.heldHeadline
  return BOOKING_STATUS_COPY.updateHeadline
})

const lead = computed(() => {
  if (!snapshot.value) {
    return props.mode === 'confirmation'
      ? BOOKING_STATUS_COPY.confirmingLead
      : BOOKING_STATUS_COPY.loadingLead
  }
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return BOOKING_STATUS_COPY.confirmedLead
  }
  if (snapshot.value.paymentStatus === 'payment_failed') return BOOKING_STATUS_COPY.paymentFailedLead
  if (snapshot.value.paymentStatus === 'payment_pending') return BOOKING_STATUS_COPY.paymentPendingLead
  return BOOKING_STATUS_COPY.updateLead
})

function readCheckoutIdFromSession(): string {
  if (typeof sessionStorage === 'undefined') return ''
  try {
    return sessionStorage.getItem(`aesthetic_os:checkout:${publicId.value}`) || ''
  } catch {
    return ''
  }
}

async function loadStatus() {
  const result = await fetchBookingStatus(apiBaseUrl, publicId.value, { signal: abort.signal })
  if ('error' in result) {
    error.value = result.error
    return
  }

  snapshot.value = result.data
  checkoutPublicId.value = readCheckoutIdFromSession()

  if (!isTerminalBookingStatus(result.data)) {
    polling.value = true
    await pollBookingStatusUntilSettled(apiBaseUrl, publicId.value, {
      onUpdate: (next) => {
        snapshot.value = next
      },
      signal: abort.signal,
    })
    polling.value = false
  }
}

async function retryStk() {
  if (!canRetryStk.value || retrying.value) return

  const checkoutId = checkoutPublicId.value || readCheckoutIdFromSession()
  if (!checkoutId) {
    stkMessage.value = 'Payment retry is not available here. Book again or contact the studio.'
    return
  }

  retrying.value = true
  stkMessage.value = null
  error.value = null

  try {
    const csrf = await ensureBookingCsrfToken(apiBaseUrl)
    if (!csrf) {
      error.value = 'Payment could not be started. Please try again.'
      return
    }

    const stk = await initiateBookingGuestStk(
      apiBaseUrl,
      {
        bookingPublicId: publicId.value,
        checkoutPublicId: checkoutId,
        phoneNumber: retryPhone.value,
        idempotencyKey: buildStkIdempotencyKey(checkoutId, createBookingAttemptNonce()),
      },
      csrf,
      { signal: abort.signal },
    )

    if ('error' in stk) {
      error.value = stk.error
      return
    }

    stkMessage.value = 'M-Pesa prompt sent. Approve it on your phone.'
    trackFunnelEvent('stk_sent', { booking: publicId.value })
    await loadStatus()
  } finally {
    retrying.value = false
  }
}

async function saveRememberDevice() {
  if (!rememberOptIn.value || rememberBusy.value || rememberDone.value || !isConfirmed.value) return

  rememberBusy.value = true
  rememberMessage.value = null
  try {
    const csrf = await ensureBookingCsrfToken(apiBaseUrl)
    if (!csrf) {
      rememberMessage.value = 'Could not save on this device. Please try again.'
      return
    }

    const result = await optInRememberDevice(apiBaseUrl, publicId.value, csrf, {
      signal: abort.signal,
    })

    if ('error' in result) {
      rememberMessage.value = 'Could not save on this device. Please try again.'
      return
    }

    rememberDone.value = true
    rememberMessage.value = 'Saved. Next visit you can book faster on this phone.'
  } finally {
    rememberBusy.value = false
  }
}

onMounted(() => {
  checkoutPublicId.value = readCheckoutIdFromSession()
  void loadStatus()
})

onBeforeUnmount(() => {
  abort.abort()
})
</script>

<style scoped>
.book-status {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: 70vh;
  padding: clamp(2.5rem, 7vh, 4rem) 1rem 3.5rem;
  background:
    radial-gradient(ellipse 80% 45% at 50% -8%, rgba(176, 122, 113, 0.09), transparent 55%),
    linear-gradient(180deg, var(--color-paper) 0%, var(--color-parchment) 100%);
}

.book-status__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.2;
  filter: saturate(1.3) brightness(1.02);
}

.book-status__bloom--tl {
  top: 0.75rem;
  left: max(0.35rem, env(safe-area-inset-left));
  width: min(110px, 22vw);
  transform: rotate(-18deg);
}

.book-status__bloom--br {
  right: max(0.35rem, env(safe-area-inset-right));
  bottom: 1.5rem;
  width: min(130px, 26vw);
  transform: rotate(145deg);
}

.book-status__card {
  position: relative;
  z-index: 1;
  width: var(--container);
  max-width: 36rem;
  margin: 0 auto;
  display: grid;
  gap: 1.15rem;
  padding: 2rem 1.5rem 1.75rem;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-surface-raised);
  box-shadow: var(--shadow-card);
}

.book-status__eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-rose);
}

.book-status__card h1 {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.65rem, 4vw, 2.15rem);
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.book-status__lead,
.book-status__polling,
.book-status__error {
  margin: 0;
  font: 400 0.98rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.book-status__error {
  color: #8b3a3a;
}

.book-status__meta {
  display: grid;
  gap: 0.85rem;
  margin: 0.35rem 0 0;
  padding: 1.1rem 0 0;
  border-top: 1px solid var(--color-line);
}

.book-status__meta div {
  display: grid;
  gap: 0.25rem;
}

.book-status__meta dt {
  font: 600 0.68rem/1 var(--font-body);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--color-muted);
}

.book-status__meta dd {
  margin: 0;
  font: 600 0.98rem/1.35 var(--font-body);
  color: var(--color-ink);
}

.book-status__retry {
  display: grid;
  gap: 0.75rem;
  padding-top: 0.35rem;
}

.book-status__retry label {
  display: grid;
  gap: 0.45rem;
  font: 600 0.82rem/1.3 var(--font-body);
  color: var(--color-ink);
}

.book-status__retry input {
  min-height: 2.75rem;
  padding: 0 0.85rem;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: var(--color-paper);
  font: 400 1rem/1 var(--font-body);
  color: var(--color-ink);
}

.book-status__retry input:focus {
  outline: 2px solid rgba(176, 122, 113, 0.35);
  outline-offset: 1px;
}

.book-status__retry-btn {
  min-height: 2.75rem;
  padding: 0 1.5rem;
  border: 0;
  border-radius: var(--radius-sm);
  font: 600 0.78rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #fff;
  background: var(--color-rose);
  cursor: pointer;
  transition: background-color 0.3s var(--ease-story);
}

.book-status__retry-btn:hover:not(:disabled) {
  background: var(--color-rose-dark);
}

.book-status__retry-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.book-status__remember {
  display: grid;
  gap: 0.85rem;
  padding: 1rem 0 0;
  border-top: 1px solid var(--color-line);
  background: transparent;
}

.book-status__remember-label {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  font: 400 0.9rem/1.5 var(--font-body);
  color: var(--color-ink);
}

.book-status__remember-btn {
  min-height: 2.5rem;
  padding: 0 1.25rem;
  border: 0;
  border-radius: var(--radius-sm);
  font: 600 0.72rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #fff;
  background: var(--color-rose);
  cursor: pointer;
  justify-self: start;
  transition: background-color 0.3s var(--ease-story);
}

.book-status__remember-btn:hover:not(:disabled) {
  background: var(--color-rose-dark);
}

.book-status__remember-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.book-status__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  padding-top: 0.35rem;
}
</style>
