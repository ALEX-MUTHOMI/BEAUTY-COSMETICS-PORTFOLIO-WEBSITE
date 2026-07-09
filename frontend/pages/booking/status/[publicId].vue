<template>
  <main class="book-status">
    <section class="book-status__card" aria-live="polite">
      <p class="book-status__eyebrow">Booking status</p>
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

      <p v-if="polling" class="book-status__polling">Checking for payment updates…</p>
      <p v-if="error" class="book-status__error" role="alert">{{ error }}</p>
      <p v-if="stkMessage" class="book-status__polling" role="status">{{ stkMessage }}</p>

      <form
        v-if="canRetryStk"
        class="book-status__retry"
        @submit.prevent="retryStk"
      >
        <label>
          M-Pesa phone (must match the number used at booking)
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
          {{ retrying ? 'Sending…' : 'Resend M-Pesa prompt' }}
        </button>
      </form>

      <div class="book-status__actions">
        <SiteButton to="/" variant="outline">Home</SiteButton>
        <SiteButton to="/book" variant="primary">Book again</SiteButton>
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

const route = useRoute()
const config = useRuntimeConfig()
const apiBaseUrl = (config.public.apiBaseUrl as string) || 'http://localhost:8000'

const publicId = computed(() => String(route.params.publicId ?? ''))
const snapshot = ref<BookingStatusSnapshot | null>(null)
const checkoutPublicId = ref('')
const polling = ref(false)
const error = ref<string | null>(null)
const stkMessage = ref<string | null>(null)
const retryPhone = ref('')
const retrying = ref(false)
const abort = new AbortController()

const shortReference = computed(() => {
  const id = snapshot.value?.bookingReference ?? publicId.value
  return id ? id.slice(0, 8).toUpperCase() : '—'
})

const canRetryStk = computed(() => {
  if (!snapshot.value) return false
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return false
  }
  return (
    snapshot.value.paymentStatus === 'payment_pending' ||
    snapshot.value.nextAction === 'complete_mpesa_stk' ||
    snapshot.value.nextAction === 'initiate_payment'
  )
})

const headline = computed(() => {
  if (!snapshot.value) return 'Loading your booking'
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return 'Booking confirmed'
  }
  if (snapshot.value.paymentStatus === 'payment_failed') return 'Payment not completed'
  if (snapshot.value.paymentStatus === 'payment_pending') return 'Complete M-Pesa payment'
  if (snapshot.value.bookingStatus === 'held') return 'Hold active'
  return 'Booking update'
})

const lead = computed(() => {
  if (!snapshot.value) return 'Please wait while we load your booking.'
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return 'Thank you — we have received your booking. A receipt email will follow shortly.'
  }
  if (snapshot.value.paymentStatus === 'payment_failed') {
    return 'No charge was completed. You can resend the M-Pesa prompt with the same phone used at booking.'
  }
  if (snapshot.value.paymentStatus === 'payment_pending') {
    return 'Approve the M-Pesa prompt on your phone. This page updates automatically. If nothing arrives, resend below.'
  }
  return 'We are tracking your booking. You can safely close this page and return later.'
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
    stkMessage.value = 'Open this page from the booking flow to retry payment, or book again.'
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
    await loadStatus()
  } finally {
    retrying.value = false
  }
}

onMounted(() => {
  checkoutPublicId.value = readCheckoutIdFromSession()
  void loadStatus()
})

onBeforeUnmount(() => {
  abort.abort()
})

definePageMeta({ layout: 'landing' })

useSeoMeta({
  title: 'Booking Status | Shee Aesthetics Meru',
  robots: 'noindex,nofollow',
})
</script>

<style scoped>
.book-status {
  min-height: 70vh;
  padding: 2rem 1rem;
  background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
}

.book-status__card {
  width: var(--container);
  max-width: 36rem;
  margin: 0 auto;
  display: grid;
  gap: 1.25rem;
  padding: 1.75rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 1.25rem;
  background: #fff;
}

.book-status__eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b4a3a;
}

.book-status__card h1 {
  margin: 0;
  font-size: 1.75rem;
}

.book-status__lead,
.book-status__polling,
.book-status__error {
  margin: 0;
}

.book-status__error {
  color: #8b1e1e;
}

.book-status__meta {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.book-status__meta div {
  display: grid;
  gap: 0.2rem;
}

.book-status__meta dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b6b6b;
}

.book-status__meta dd {
  margin: 0;
  font-weight: 600;
}

.book-status__retry {
  display: grid;
  gap: 0.75rem;
}

.book-status__retry label {
  display: grid;
  gap: 0.4rem;
  font-weight: 600;
}

.book-status__retry input {
  min-height: 2.75rem;
  padding: 0 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.14);
  border-radius: 0.75rem;
}

.book-status__retry-btn {
  min-height: 2.75rem;
  padding: 0 1.25rem;
  border: 0;
  border-radius: 0.75rem;
  font-weight: 700;
  color: #fff;
  background: #241611;
  cursor: pointer;
}

.book-status__retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.book-status__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
