<template>
  <main class="book-page">
    <header class="book-hero">
      <div class="book-hero__inner">
        <p class="label">Book online</p>
        <h1>{{ pageTitle }}</h1>
        <p class="book-hero__lead">{{ pageLead }}</p>
      </div>
    </header>

    <section class="book-body" aria-label="Booking availability">
      <div class="book-shell" :class="{ 'book-shell--active': Boolean(handoff) }">
        <template v-if="handoff">
          <div class="book-summary">
            <p class="book-summary__eyebrow">{{ handoff.type === 'package' ? 'Full package' : 'Single treatment' }}</p>
            <h2>{{ selectionName }}</h2>
            <p v-if="flow.selection.value" class="book-summary__meta">
              {{ flow.selection.value.durationMinutes }} min · {{ flow.selection.value.name }}
            </p>
          </div>

          <p v-if="displayError" class="book-error" role="alert">{{ displayError }}</p>

          <template v-if="checkoutStep === 'pick'">
            <BookingFloCalendar
              :days="flow.calendarDays.value"
              :weeks="flow.calendar.value?.weeks ?? []"
              :layout="flow.calendar.value?.layout ?? 'singles'"
              :selected-date="flow.selectedDate.value"
              :range="flow.calendar.value?.range ?? null"
              :loading="flow.loading.value"
              :interaction-locked="calendarLocked"
              :capacity-hint="capacityHint"
              aria-label="Pick your visit date"
              @select="flow.selectDate"
            />

            <BookingFloSlots
              :iso-date="flow.selectedDate.value"
              :slots="flow.daySlots.value"
              :selected-slot="flow.selectedSlot.value"
              :loading="flow.slotsLoading.value"
              @select="flow.selectSlot"
            />

            <div class="book-actions">
              <SiteButton to="/services" variant="outline">Change service</SiteButton>
              <button
                type="button"
                class="book-continue"
                :disabled="!flow.canContinue.value || isSubmitting"
                @click="openDetails"
              >
                Continue to checkout
              </button>
            </div>
          </template>

          <BookingCustomerPanel
            v-else
            v-model:customer-form="customerForm"
            v-model:policy-accepted="policyAccepted"
            v-model:turnstile-token="turnstileToken"
            :policy-text="policyText"
            :turnstile-required="turnstileRequired"
            :can-submit="canSubmit"
            :disabled="isSubmitting"
            :submit-error="submitError"
            @back="backToPick"
            @submit="handleSubmit"
          />
        </template>

        <template v-else>
          <h2>What would you like to book?</h2>
          <p class="book-summary__meta">
            Choose a package or treatment on our services page, then return here to see live availability.
          </p>
          <div class="book-actions book-actions--stack">
            <SiteButton to="/services#full-packages" variant="primary">View packages</SiteButton>
            <SiteButton to="/services#single-sessions" variant="outline">View singles</SiteButton>
          </div>
        </template>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import BookingCustomerPanel from '~/components/booking/BookingCustomerPanel.vue'
import BookingFloCalendar from '~/components/booking/BookingFloCalendar.vue'
import BookingFloSlots from '~/components/booking/BookingFloSlots.vue'
import { useBookCheckout } from '@/booking/useBookCheckout'
import { useBookFlow } from '@/booking/useBookFlow'
import { PACKAGE_DAYS, SINGLE_DAYS_LABEL } from '@/landing/landingContent'
import {
  parseBookHandoffQuery,
  persistBookHandoff,
  readPersistedBookHandoff,
  type ResolvedBookHandoff,
} from '@/landing/bookingHandoff'

const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()
const apiBaseUrl = (config.public.apiBaseUrl as string) || 'http://localhost:8000'

const handoff = ref<ResolvedBookHandoff | null>(null)
const flow = useBookFlow(handoff, apiBaseUrl)
const checkout = useBookCheckout(apiBaseUrl, flow.selection, flow.selectedSlot)
const {
  customerForm,
  policyAccepted,
  turnstileToken,
  policyText,
  turnstileRequired,
  canSubmit,
  isSubmitting,
  submitError,
  step: checkoutStep,
  openDetails,
  backToPick,
  submitBooking,
} = checkout

const calendarLocked = computed(
  () =>
    flow.calendarInteractionLocked.value ||
    flow.slotsLoading.value ||
    isSubmitting.value ||
    checkoutStep.value !== 'pick',
)

const displayError = computed(() => flow.error.value || submitError.value)

function syncHandoff() {
  handoff.value =
    parseBookHandoffQuery(route.query as Record<string, unknown>) ?? readPersistedBookHandoff()
  if (handoff.value) persistBookHandoff(handoff.value)
}

async function handleSubmit() {
  const result = await submitBooking()
  if (!result) return
  // statusUrl is already allowlisted in parseCheckout; never navigate API absolute URLs.
  await router.push(result.statusUrl || `/booking/status/${result.bookingPublicId}/`)
}

onMounted(syncHandoff)
watch(() => route.query, syncHandoff)

const selectionName = computed(
  () =>
    flow.selection.value?.name ??
    handoff.value?.planName ??
    handoff.value?.treatmentName ??
    'Your selection',
)

const capacityHint = computed(() =>
  handoff.value?.type === 'package'
    ? `Tue & Wed · up to 3 clients per day`
    : `${SINGLE_DAYS_LABEL} · up to 5 clients per day`,
)

const pageTitle = computed(() => {
  if (!handoff.value) return 'Book your visit'
  if (checkoutStep.value === 'details') return 'Confirm your details'
  return 'Pick your day & time'
})

const pageLead = computed(() => {
  if (!handoff.value) return 'Start on services, then book here with live availability.'
  if (checkoutStep.value === 'details') {
    return 'One booking per click. Your slot is held only after you confirm.'
  }
  if (handoff.value.type === 'package') {
    return `Package days: ${PACKAGE_DAYS.join(' and ')}. Tap a day to load open times.`
  }
  return `Single days: ${SINGLE_DAYS_LABEL}. Tap a day to load open times.`
})

definePageMeta({ layout: 'landing' })

const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'
useSeoMeta({
  title: 'Book Online | Shee Aesthetics Meru',
  description: 'See live availability and book your visit at Shee Aesthetics Meru.',
  robots: 'noindex,follow',
})
useHead({ link: [{ rel: 'canonical', href: `${siteUrl}/book` }] })
</script>

<style scoped>
.book-page {
  background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
  min-height: 70vh;
  padding-bottom: calc(var(--mobile-book-bar-height) + env(safe-area-inset-bottom, 0px));
}

.label {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.book-hero {
  padding: clamp(1.75rem, 5vh, 3rem) 1rem 1rem;
  border-bottom: 1px solid var(--color-line);
}

.book-hero__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
  text-align: center;
}

.book-hero h1 {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 4.5vw, 2.45rem);
}

.book-hero__lead {
  margin: 0;
  color: var(--color-muted);
}

.book-body {
  padding: 1.5rem 1rem 2rem;
}

.book-shell {
  width: var(--container);
  max-width: 32rem;
  margin: 0 auto;
  padding: 1.25rem;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: #fafafa;
}

.book-shell--active {
  max-width: 42rem;
}

.book-summary h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.45rem;
  font-weight: 400;
}

.book-summary__eyebrow {
  margin: 0 0 0.25rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.book-summary__meta {
  margin: 0 0 1rem;
  color: var(--color-muted);
  font-size: 0.92rem;
}

.book-error {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #fff5f5;
  color: #9b2c2c;
  font-size: 0.9rem;
}

.book-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 1.25rem;
}

.book-actions--stack {
  flex-direction: column;
}

.book-actions :deep(.site-btn) {
  flex: 1;
}

.book-continue {
  flex: 1;
  min-height: 2.75rem;
  border: 0;
  border-radius: 999px;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
}

.book-continue:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
