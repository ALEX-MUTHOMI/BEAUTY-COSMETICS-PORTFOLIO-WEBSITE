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

      <div class="book-status__actions">
        <SiteButton to="/" variant="outline">Home</SiteButton>
        <SiteButton to="/book" variant="primary">Book again</SiteButton>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { fetchBookingStatus, type BookingStatusSnapshot } from '@/booking/bookingWriteApi'
import { isTerminalBookingStatus, pollBookingStatusUntilSettled } from '@/booking/bookingStatusPoll'

const route = useRoute()
const config = useRuntimeConfig()
const apiBaseUrl = (config.public.apiBaseUrl as string) || 'http://localhost:8000'

const publicId = computed(() => String(route.params.publicId ?? ''))
const snapshot = ref<BookingStatusSnapshot | null>(null)
const polling = ref(false)
const error = ref<string | null>(null)
const abort = new AbortController()

const shortReference = computed(() => {
  const id = snapshot.value?.bookingReference ?? publicId.value
  return id ? id.slice(0, 8).toUpperCase() : '—'
})

const headline = computed(() => {
  if (!snapshot.value) return 'Loading your booking'
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return 'Booking confirmed'
  }
  if (snapshot.value.paymentStatus === 'payment_pending') return 'Awaiting payment'
  if (snapshot.value.bookingStatus === 'held') return 'Hold active'
  return 'Booking update'
})

const lead = computed(() => {
  if (!snapshot.value) return 'Please wait while we load your booking.'
  if (snapshot.value.bookingStatus === 'confirmed' || snapshot.value.paymentStatus === 'paid') {
    return 'Thank you — we have received your booking. A receipt email will follow shortly.'
  }
  if (snapshot.value.paymentStatus === 'payment_pending') {
    return 'Complete payment on your phone if you have not already. This page will update automatically.'
  }
  return 'We are tracking your booking. You can safely close this page and return later.'
})

async function loadStatus() {
  const result = await fetchBookingStatus(apiBaseUrl, publicId.value, { signal: abort.signal })
  if ('error' in result) {
    error.value = result.error
    return
  }
  snapshot.value = result.data
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

onMounted(() => {
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
  padding: 1.5rem;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: #fff;
}

.book-status__eyebrow {
  margin: 0 0 0.5rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.book-status__card h1 {
  margin: 0 0 0.5rem;
  font-family: var(--font-display);
  font-size: 1.85rem;
  font-weight: 400;
}

.book-status__lead {
  margin: 0 0 1.25rem;
  color: var(--color-muted);
}

.book-status__meta {
  display: grid;
  gap: 0.75rem;
  margin: 0 0 1rem;
}

.book-status__meta dt {
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.book-status__meta dd {
  margin: 0.15rem 0 0;
}

.book-status__polling {
  margin: 0 0 1rem;
  color: var(--color-muted);
  font-size: 0.9rem;
}

.book-status__error {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #fff5f5;
  color: #9b2c2c;
}

.book-status__actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 1.25rem;
}

.book-status__actions :deep(.site-btn) {
  flex: 1;
}
</style>
