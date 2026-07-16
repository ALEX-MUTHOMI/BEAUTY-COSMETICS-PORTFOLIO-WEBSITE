<template>
  <main class="book-page">
    <header class="book-hero" :class="{ 'book-hero--compact': checkoutStep === 'pick' }">
      <div class="book-hero__inner">
        <p class="label">Book online</p>
        <h1>{{ pageTitle }}</h1>
        <p class="book-hero__lead">{{ pageLead }}</p>
      </div>
    </header>

    <section class="book-body" aria-label="Booking availability">
      <div class="book-shell book-shell--active">
        <nav class="book-steps" aria-label="Booking progress">
          <span
            class="book-steps__item"
            :class="{ 'book-steps__item--active': checkoutStep === 'pick' }"
            :aria-current="checkoutStep === 'pick' ? 'step' : undefined"
          >
            1 Date &amp; time
          </span>
          <span class="book-steps__divider" aria-hidden="true" />
          <span
            class="book-steps__item"
            :class="{ 'book-steps__item--active': checkoutStep === 'details' || checkoutStep === 'submitting' }"
            :aria-current="checkoutStep !== 'pick' ? 'step' : undefined"
          >
            2 Your details
          </span>
        </nav>

        <div class="book-summary">
          <p class="book-summary__eyebrow">
            {{ handoff.type === 'package' ? 'Full package' : 'Single treatment' }}
          </p>
          <h2>{{ selectionName }}</h2>
          <p v-if="flow.selection.value" class="book-summary__meta">
            {{ flow.selection.value.durationMinutes }} min · {{ flow.selection.value.name }}
          </p>
        </div>

        <div v-if="displayError" class="book-error" role="alert">
          <p class="book-error__text">{{ displayError }}</p>
          <button
            v-if="checkoutStep === 'pick' && canRetryAvailability"
            type="button"
            class="book-error__retry"
            :disabled="flow.loading.value || flow.slotsLoading.value"
            @click="flow.retryLoad()"
          >
            Retry availability
          </button>
        </div>

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
            @select="onSelectDate"
          />

          <div ref="slotsAnchor" class="book-slots-anchor">
            <BookingFloSlots
              :iso-date="flow.selectedDate.value"
              :slots="flow.daySlots.value"
              :selected-slot="flow.selectedSlot.value"
              :loading="flow.slotsLoading.value"
              @select="flow.selectSlot"
            />
          </div>

          <div
            class="book-actions"
            :class="{ 'book-actions--ready': flow.canContinue.value }"
          >
            <SiteButton :to="changeServiceHref" variant="outline">Change service</SiteButton>
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
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, toRef, watch, type Ref } from 'vue'
import BookingCustomerPanel from '~/components/booking/BookingCustomerPanel.vue'
import BookingFloCalendar from '~/components/booking/BookingFloCalendar.vue'
import BookingFloSlots from '~/components/booking/BookingFloSlots.vue'
import { useBookCheckout } from '@/booking/useBookCheckout'
import { useBookFlow } from '@/booking/useBookFlow'
import { GENERIC_BOOKING_THROTTLE_ERROR } from '@/booking/bookingRequestGovernor'
import { SINGLE_DAYS_LABEL } from '@/landing/landingContent'
import {
  persistBookHandoff,
  SERVICES_BOOK_ENTRY,
  type ResolvedBookHandoff,
} from '@/landing/bookingHandoff'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const props = defineProps<{
  handoff: ResolvedBookHandoff
}>()

const router = useRouter()
const config = useRuntimeConfig()
const apiBaseUrl = (config.public.apiBaseUrl as string) || 'http://localhost:8000'

const handoffRef = toRef(props, 'handoff') as Ref<ResolvedBookHandoff | null>
const flow = useBookFlow(handoffRef, apiBaseUrl)
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

const slotsAnchor = ref<HTMLElement | null>(null)

watch(
  handoffRef,
  (value) => {
    if (value) persistBookHandoff(value)
  },
  { immediate: true },
)

const calendarLocked = computed(
  () =>
    flow.calendarInteractionLocked.value ||
    flow.slotsLoading.value ||
    isSubmitting.value ||
    checkoutStep.value !== 'pick',
)

const displayError = computed(() => flow.error.value || submitError.value)

const canRetryAvailability = computed(
  () =>
    Boolean(flow.error.value) &&
    (flow.error.value === GENERIC_BOOKING_THROTTLE_ERROR ||
      /try again|unavailable|too many/i.test(flow.error.value || '')),
)

const changeServiceHref = computed(() => {
  if (props.handoff.type === 'package') return SERVICES_ROUTES.fullPackages
  if (props.handoff.category) return `${SERVICES_ROUTES.page}#${props.handoff.category}`
  return SERVICES_BOOK_ENTRY
})

async function onSelectDate(isoDate: string) {
  flow.selectDate(isoDate)
  await nextTick()
  slotsAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

async function handleSubmit() {
  const result = await submitBooking()
  if (!result) return
  try {
    sessionStorage.setItem(`aesthetic_os:checkout:${result.bookingPublicId}`, result.checkoutPublicId)
  } catch {
    /* ignore quota / private mode */
  }
  await router.push(result.statusUrl || `/booking/status/${result.bookingPublicId}/`)
}

const selectionName = computed(
  () =>
    flow.selection.value?.name ??
    props.handoff.planName ??
    props.handoff.treatmentName ??
    'Your selection',
)

const capacityHint = computed(() =>
  props.handoff.type === 'package'
    ? 'Tue & Wed · limited spots'
    : `${SINGLE_DAYS_LABEL} · limited spots`,
)

const pageTitle = computed(() => {
  if (checkoutStep.value === 'details') return 'Confirm your details'
  return 'Pick your day & time'
})

const pageLead = computed(() => {
  if (checkoutStep.value === 'details') {
    return 'Confirm your details to reserve this time.'
  }
  return 'Choose a day, then a time.'
})
</script>

<style scoped>
.book-page {
  background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
  min-height: 70vh;
  /* Mobile book bar is hidden on /book/* — only need sticky-action + safe-area room. */
  padding-bottom: calc(env(safe-area-inset-bottom, 0px) + 5.5rem);
}

.label {
  margin: 0 0 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.book-hero {
  padding: clamp(1.75rem, 5vh, 3rem) 1rem 1rem;
  border-bottom: 1px solid var(--color-line);
}

.book-hero--compact {
  padding: 1.15rem 1rem 0.85rem;
}

.book-hero__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
  text-align: center;
}

.book-hero h1 {
  margin: 0 0 0.5rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 4.5vw, 2.45rem);
}

.book-hero--compact h1 {
  font-size: clamp(1.55rem, 4vw, 2rem);
  margin-bottom: 0.35rem;
}

.book-hero__lead {
  margin: 0;
  color: var(--color-muted);
}

.book-body {
  padding: 1.15rem 1rem 2rem;
}

.book-shell {
  width: var(--container);
  max-width: 42rem;
  margin: 0 auto;
  padding: 1.1rem 1.15rem 1.25rem;
  border: 1px solid var(--color-line);
  border-radius: 12px;
  background: #fafafa;
}

.book-steps {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-bottom: 0.85rem;
}

.book-steps__item {
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.book-steps__item--active {
  color: var(--color-rose-dark);
}

.book-steps__divider {
  flex: 0 0 1.25rem;
  height: 1px;
  background: var(--color-line);
}

.book-summary {
  position: sticky;
  top: 0;
  z-index: 2;
  margin: 0 -0.35rem 1rem;
  padding: 0.65rem 0.35rem 0.85rem;
  background: #fafafa;
  border-bottom: 1px solid var(--color-line);
}

.book-summary h2 {
  margin: 0 0 0.25rem;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 400;
}

.book-summary__eyebrow {
  margin: 0 0 0.2rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.book-summary__meta {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.88rem;
}

.book-error {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #fff5f5;
  color: #9b2c2c;
  font-size: 0.9rem;
}

.book-error__text {
  margin: 0;
}

.book-error__retry {
  margin-top: 0.65rem;
  min-height: 2.4rem;
  padding: 0.45rem 0.9rem;
  border: 1px solid #9b2c2c;
  border-radius: 999px;
  background: #fff;
  color: #9b2c2c;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.book-error__retry:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.book-slots-anchor {
  scroll-margin-top: 5.5rem;
}

.book-actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 1.15rem;
  padding-top: 0.25rem;
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

.book-actions--ready .book-continue {
  box-shadow: 0 8px 20px rgba(222, 150, 141, 0.35);
}

@media (max-width: 767px) {
  .book-actions {
    position: sticky;
    bottom: calc(env(safe-area-inset-bottom, 0px) + 0.5rem);
    z-index: 3;
    margin-top: 1rem;
    margin-left: -0.35rem;
    margin-right: -0.35rem;
    padding: 0.65rem 0.35rem;
    background: linear-gradient(180deg, rgba(250, 250, 250, 0.75) 0%, #fafafa 35%);
    border-top: 1px solid var(--color-line);
  }
}
</style>
