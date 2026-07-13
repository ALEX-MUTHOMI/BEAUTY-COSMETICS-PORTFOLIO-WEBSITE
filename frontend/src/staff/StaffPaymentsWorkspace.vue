<template>
  <StaffPortalShell :title="shellTitle" :api-base-url="apiBaseUrl">
    <section class="toolbar" aria-label="Payment day filters">
      <label>
        Date
        <input v-model="selectedDate" type="date" @change="loadSchedule" />
      </label>
      <p class="toolbar__hint">Day-scoped payment view for the selected date — change the date to review past days.</p>
    </section>

    <StaffPortalCards label="Payment overview" :cards="cards" :loading="showLoading" />

    <section v-if="showLoading" class="list-panel" aria-label="Loading payment records">
      <div v-for="index in 4" :key="index" class="payment-skeleton" />
    </section>
    <section v-else-if="showError" class="list-panel list-panel--state" role="alert">
      <h2>Payments could not load.</h2>
      <p>{{ displayError }}</p>
      <button type="button" @click="loadSchedule">Try again</button>
    </section>
    <section v-else-if="showEmpty" class="list-panel list-panel--state">
      <h2>No payment records for this day.</h2>
      <p>Try a different date, or open bookings for the full schedule.</p>
    </section>
    <section v-else class="list-panel" aria-label="Payment records">
      <div class="list-panel__head">
        <span>Time</span>
        <span>Service</span>
        <span>Payment</span>
        <span>Receipt</span>
        <span>Actions</span>
      </div>
      <article v-for="payment in sortedPayments" :key="payment.publicBookingId">
        <strong>{{ payment.time }}</strong>
        <div>
          <strong>{{ payment.client }}</strong>
          <span>{{ payment.service }}</span>
          <span v-if="payment.amount">{{ payment.currency || 'KES' }} {{ payment.amount }}</span>
        </div>
        <StaffStatusChip :status="payment.paymentStatus" />
        <StaffStatusChip :status="receiptChipStatus(payment.receiptStatus)" />
        <NuxtLink :to="`/staff/bookings/${payment.publicBookingId}`">Open</NuxtLink>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import StaffPortalCards from './StaffPortalCards.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { getDailySchedule, type StaffAppointment } from './staffPortalApi'
import { receiptChipStatus } from './statusCopy'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
    loading?: boolean
    empty?: boolean
    errorMessage?: string
    appointments?: StaffAppointment[]
  }>(),
  {
    apiBaseUrl: '',
    loading: false,
    empty: false,
    errorMessage: '',
    appointments: undefined,
  },
)

const selectedDate = ref(new Date().toISOString().slice(0, 10))
const internalLoading = ref(false)
const internalError = ref('')
const payments = ref<StaffAppointment[]>([])

const shellTitle = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return selectedDate.value === today ? "Today's payments" : `Payments for ${selectedDate.value}`
})

const showLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.errorMessage || internalError.value)
const showError = computed(() => Boolean(displayError.value) && !showLoading.value)

const sourcePayments = computed(() => {
  if (props.appointments) return props.appointments
  return payments.value
})

const sortedPayments = computed(() => {
  return [...sourcePayments.value].sort((left, right) => {
    const leftPending = isAwaiting(left.paymentStatus) ? 0 : 1
    const rightPending = isAwaiting(right.paymentStatus) ? 0 : 1
    if (leftPending !== rightPending) return leftPending - rightPending
    return left.time.localeCompare(right.time)
  })
})

const showEmpty = computed(() => {
  if (showLoading.value || showError.value) return false
  if (props.empty) return true
  return sortedPayments.value.length === 0
})

const cards = computed(() => {
  const rows = sourcePayments.value
  const paid = rows.filter((row) => isPaid(row.paymentStatus)).length
  const awaiting = rows.filter((row) => isAwaiting(row.paymentStatus)).length
  const receiptsReady = rows.filter((row) => {
    const status = String(row.receiptStatus || '').toLowerCase()
    return status && status !== 'not_issued'
  }).length
  return [
    { label: 'Confirmed', value: paid, hint: 'Paid bookings this day' },
    { label: 'Awaiting', value: awaiting, hint: 'Customer action needed' },
    { label: 'On schedule', value: rows.length, hint: `For ${selectedDate.value}` },
    { label: 'Receipts', value: receiptsReady, hint: 'Ready to view' },
  ]
})

function isPaid(status: string) {
  const normalized = status.toLowerCase()
  return normalized === 'paid' || normalized === 'success'
}

function isAwaiting(status: string) {
  const normalized = status.toLowerCase()
  return normalized.includes('pending') || normalized === 'not_paid' || normalized === 'held'
}

async function loadSchedule() {
  if (props.appointments || props.loading || props.errorMessage || props.empty) return
  if (!props.apiBaseUrl) {
    payments.value = []
    return
  }
  internalLoading.value = true
  internalError.value = ''
  try {
    const result = await getDailySchedule(props.apiBaseUrl, selectedDate.value)
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Please check your connection and try again.'
      payments.value = []
      return
    }
    payments.value = result.data.appointments
  } catch {
    internalError.value = 'Please check your connection and try again.'
    payments.value = []
  } finally {
    internalLoading.value = false
  }
}

onMounted(() => {
  void loadSchedule()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1rem;
}

.toolbar label {
  display: grid;
  gap: 0.35rem;
  font: 600 0.82rem/1.2 var(--font-body, 'Manrope', sans-serif);
}

.toolbar input {
  min-height: 2.8rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0;
  padding: 0 0.85rem;
  background: var(--color-paper, #fff);
  color: var(--color-ink, #27272a);
  font: 1rem var(--font-body, 'Manrope', sans-serif);
}

.toolbar__hint {
  margin: 0;
  max-width: 36ch;
  color: var(--color-muted, #89858d);
  font: 0.9rem/1.45 var(--font-body, 'Manrope', sans-serif);
}

.list-panel {
  display: grid;
  gap: 0.8rem;
  margin-top: 1rem;
}

.list-panel__head,
.list-panel article {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1.4fr) auto auto auto;
  gap: 1rem;
  align-items: center;
}

.list-panel__head {
  padding: 0 1rem;
  color: var(--color-muted, #89858d);
  font: 600 0.72rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.list-panel article {
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
}

.list-panel div {
  display: grid;
  gap: 0.2rem;
}

.list-panel span {
  color: var(--color-muted, #89858d);
}

.list-panel a,
.list-panel--state button {
  width: max-content;
  min-height: 2.7rem;
  display: inline-flex;
  align-items: center;
  border: 0;
  padding: 0 1rem;
  color: #fff;
  background: var(--color-ink, #27272a);
  text-decoration: none;
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.list-panel--state {
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
}

.list-panel--state h2,
.list-panel--state p {
  margin: 0;
}

.payment-skeleton {
  min-height: 4rem;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), #fff, var(--color-rose-soft, #f5e8e6));
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 860px) {
  .list-panel__head {
    display: none;
  }

  .list-panel article {
    grid-template-columns: 1fr;
  }
}
</style>
