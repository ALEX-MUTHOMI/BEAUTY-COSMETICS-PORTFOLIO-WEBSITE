<template>
  <StaffPortalShell title="Booking detail">
    <section v-if="loading" class="detail-card detail-card--state" aria-label="Loading booking">
      <div class="skeleton-block" />
      <div class="skeleton-block skeleton-block--short" />
    </section>
    <section v-else-if="errorMessage" class="detail-card detail-card--state" role="alert">
      <h2>Booking could not load.</h2>
      <p>{{ errorMessage }}</p>
      <button type="button" @click="loadDetail">Try again</button>
    </section>
    <section v-else-if="detail" class="detail-card">
      <p class="eyebrow">Appointment</p>
      <h2>{{ detail.client }} · {{ detail.service }}</h2>
      <div class="detail-grid">
        <span>{{ detail.localDate }} · {{ detail.time }}{{ detail.endTime ? `–${detail.endTime}` : '' }}</span>
        <StaffStatusChip :status="detail.bookingStatus" />
        <StaffStatusChip :status="detail.paymentStatus" />
        <span v-if="detail.amount">{{ detail.currency }} {{ detail.amount }}</span>
      </div>

      <section class="payment-panel" aria-label="Payment summary">
        <p class="eyebrow">Payment</p>
        <p v-if="paymentLoading" class="payment-panel__copy">Loading payment summary…</p>
        <p v-else-if="paymentError" class="payment-panel__copy" role="alert">{{ paymentError }}</p>
        <template v-else-if="payment">
          <div class="detail-grid">
            <StaffStatusChip :status="payment.paymentStatus" />
            <span>{{ payment.currency }} {{ payment.amount }}</span>
            <StaffStatusChip :status="receiptChipStatus(payment.receiptStatus)" />
            <span v-if="payment.paidAtEat">Paid {{ payment.paidAtEat }}</span>
          </div>
          <p v-if="!receiptReady" class="payment-panel__copy">Receipt not issued yet.</p>
          <button
            type="button"
            class="receipt-button"
            :disabled="!receiptReady || receiptDownloading"
            @click="openReceiptPdf"
          >
            {{ receiptDownloading ? 'Opening receipt…' : 'View receipt PDF' }}
          </button>
          <p v-if="receiptMessage" class="payment-panel__copy" role="status">{{ receiptMessage }}</p>
        </template>
      </section>

      <div v-if="revealedContact" class="contact-reveal" role="status">
        <p><strong>Email</strong> {{ revealedContact.email }}</p>
        <p><strong>Phone</strong> {{ revealedContact.phone }}</p>
      </div>

      <div class="actions">
        <button type="button" @click="showReauth = true">Reveal customer contact</button>
        <button type="button" :disabled="completed" @click="completed = true">
          {{ completed ? 'Service completed' : 'Mark service completed' }}
        </button>
        <NuxtLink to="/staff/bookings">Back to bookings</NuxtLink>
      </div>
    </section>

    <StaffContactRevealModal
      v-if="showReauth"
      :api-base-url="props.apiBaseUrl"
      @close="showReauth = false"
      @confirmed="onReauthConfirmed"
    />
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { ensureBookingCsrfToken } from '../booking/bookingCsrf'
import StaffContactRevealModal from './StaffContactRevealModal.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import {
  downloadStaffReceiptPdf,
  getStaffBookingDetail,
  getStaffBookingPayment,
  postStaffContactAccess,
  type StaffBookingDetailData,
  type StaffPaymentSummary,
} from './staffPortalApi'
import { isReceiptIssued, receiptChipStatus } from './statusCopy'

const props = withDefaults(
  defineProps<{
    /** Injected by Nuxt pages — never call useRuntimeConfig inside src/ components. */
    apiBaseUrl?: string
    publicBookingId?: string
  }>(),
  { apiBaseUrl: '', publicBookingId: '' },
)

const showReauth = ref(false)
const completed = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const detail = ref<StaffBookingDetailData | null>(null)
const payment = ref<StaffPaymentSummary | null>(null)
const paymentLoading = ref(false)
const paymentError = ref('')
const receiptDownloading = ref(false)
const receiptMessage = ref('')
const revealedContact = ref<{ email: string; phone: string } | null>(null)

const demoDetail: StaffBookingDetailData = {
  publicBookingId: 'demo',
  localDate: 'Today',
  time: '09:00',
  endTime: '',
  client: 'Grace M.',
  service: 'Soft glam makeup',
  bookingStatus: 'confirmed',
  paymentStatus: 'paid',
  receiptStatus: 'issued',
  amount: '4,500',
  currency: 'KES',
  resource: '',
}

const receiptReady = computed(() => isReceiptIssued(payment.value?.receiptStatus || detail.value?.receiptStatus))

if (!props.publicBookingId) {
  detail.value = demoDetail
  payment.value = {
    paymentStatus: 'paid',
    amount: '4,500',
    currency: 'KES',
    receiptStatus: 'issued',
    paidAtEat: '',
    providerReference: 'redacted',
  }
}

async function loadPayment() {
  if (!props.apiBaseUrl || !props.publicBookingId) return
  paymentLoading.value = true
  paymentError.value = ''
  try {
    const result = await getStaffBookingPayment(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok || !result.data) {
      paymentError.value = result.message || 'Payment summary could not load.'
      payment.value = null
      return
    }
    payment.value = result.data
  } catch {
    paymentError.value = 'Payment summary could not load.'
    payment.value = null
  } finally {
    paymentLoading.value = false
  }
}

async function loadDetail() {
  if (!props.apiBaseUrl || !props.publicBookingId) {
    detail.value = demoDetail
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await getStaffBookingDetail(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Please check your connection and try again.'
      detail.value = null
      return
    }
    detail.value = result.data
    await loadPayment()
  } catch {
    errorMessage.value = 'Please check your connection and try again.'
    detail.value = null
  } finally {
    loading.value = false
  }
}

async function openReceiptPdf() {
  if (!props.apiBaseUrl || !props.publicBookingId || !receiptReady.value) return
  receiptDownloading.value = true
  receiptMessage.value = ''
  try {
    const result = await downloadStaffReceiptPdf(props.apiBaseUrl, props.publicBookingId)
    if (!result.ok) {
      receiptMessage.value = result.message || 'Receipt could not be opened.'
    }
  } catch {
    receiptMessage.value = 'Receipt could not be opened.'
  } finally {
    receiptDownloading.value = false
  }
}

async function onReauthConfirmed() {
  showReauth.value = false
  if (!props.apiBaseUrl || !props.publicBookingId) return
  try {
    const csrfToken = await ensureBookingCsrfToken(props.apiBaseUrl)
    if (!csrfToken) {
      errorMessage.value = 'Contact details could not be revealed. Confirm your password and try again.'
      return
    }
    const result = await postStaffContactAccess(
      props.apiBaseUrl,
      props.publicBookingId,
      'Staff needs customer contact for appointment coordination',
      csrfToken,
    )
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Contact details could not be revealed.'
      return
    }
    revealedContact.value = { email: result.data.email, phone: result.data.phone }
  } catch {
    errorMessage.value = 'Contact details could not be revealed. Confirm your password and try again.'
  }
}

onMounted(() => {
  void loadDetail()
})

watch(
  () => [props.apiBaseUrl, props.publicBookingId],
  () => {
    void loadDetail()
  },
)
</script>

<style scoped>
.detail-card {
  display: grid;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0;
  background: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
  font-family: var(--font-body, 'Manrope', sans-serif);
}

.detail-card--state {
  gap: 0.75rem;
}

.eyebrow {
  margin: 0;
  color: var(--color-rose-dark, #c97f76);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font: 600 0.72rem/1.2 var(--font-body, 'Manrope', sans-serif);
}

.detail-card h2 {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
}

.detail-grid,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.payment-panel {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: var(--color-cream, #fcf5f5);
}

.payment-panel__copy {
  margin: 0;
  color: var(--color-muted, #89858d);
}

.receipt-button {
  width: max-content;
  min-height: 2.8rem;
  border: 0;
  padding: 0 1rem;
  color: #fff;
  background: var(--color-rose, #de968d);
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
}

.receipt-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.contact-reveal {
  display: grid;
  gap: 0.35rem;
  padding: 0.9rem 1rem;
  background: var(--color-rose-soft, #f5e8e6);
}

.contact-reveal p {
  margin: 0;
}

.actions button,
.actions a,
.detail-card--state button {
  min-height: 2.8rem;
  display: inline-flex;
  align-items: center;
  padding: 0 1rem;
  border: 0;
  border-radius: 0;
  color: #fff;
  background: var(--color-ink, #27272a);
  text-decoration: none;
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.actions button:disabled {
  opacity: 0.6;
}

.skeleton-block {
  height: 2.8rem;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), #fff, var(--color-rose-soft, #f5e8e6));
  background-size: 200% 100%;
  animation: shimmer 1.2s linear infinite;
}

.skeleton-block--short {
  width: 60%;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}
</style>
