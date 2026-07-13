<template>
  <StaffPortalShell title="Bookings" :api-base-url="apiBaseUrl">
    <section class="toolbar" aria-label="Booking filters">
      <label>
        Date
        <input v-model="selectedDate" type="date" @change="onDateOrStatusChange" />
      </label>
      <label>
        Status
        <select v-model="statusFilter" @change="onDateOrStatusChange">
          <option value="">All bookings</option>
          <option value="confirmed">Booking confirmed</option>
          <option value="held">Awaiting payment</option>
          <option value="cancelled">Cancelled</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <label>
        Beautician
        <select v-model="assignedFilter" @change="onDateOrStatusChange">
          <option value="">All</option>
          <option value="unassigned">Unassigned</option>
          <option value="me">Mine</option>
        </select>
      </label>
      <label>
        Search
        <input
          v-model="searchQuery"
          placeholder="Name, code, or receipt (3+ chars)"
          @input="onSearchInput"
        />
      </label>
    </section>
    <p v-if="searchHint" class="search-hint" role="status">{{ searchHint }}</p>

    <section v-if="showLoading" class="table-card table-card--state" aria-label="Loading bookings">
      <div v-for="index in 4" :key="index" class="skeleton-row" />
    </section>
    <section v-else-if="showError" class="table-card table-card--state" role="alert">
      <h2>Bookings could not load.</h2>
      <p>{{ displayError }}</p>
      <button type="button" @click="reload">Try again</button>
    </section>
    <section v-else-if="showEmpty" class="table-card table-card--state">
      <h2>No bookings found.</h2>
      <p>Try a different date, search (3+ characters), or booking code.</p>
    </section>
    <section v-else class="table-card" aria-label="Staff bookings list">
      <div class="table-card__head">
        <span>Time</span>
        <span>Client</span>
        <span>Code</span>
        <span>Service</span>
        <span>Booking</span>
        <span>Fulfillment</span>
        <span>Payment</span>
        <span>Actions</span>
      </div>
      <article v-for="booking in visibleBookings" :key="booking.publicBookingId" class="booking-row">
        <strong>{{ booking.time }}</strong>
        <span>{{ booking.client }}</span>
        <span class="code">{{ shortCode(booking.bookingReference || booking.publicBookingId) }}</span>
        <span>{{ booking.service }}</span>
        <StaffStatusChip :status="booking.bookingStatus" />
        <StaffStatusChip :status="booking.fulfillmentStatus || 'not_started'" />
        <StaffStatusChip :status="booking.paymentStatus" />
        <NuxtLink :to="`/staff/bookings/${booking.publicBookingId}`">Open</NuxtLink>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { getDailySchedule, searchStaffBookings, type StaffAppointment } from './staffPortalApi'

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
const statusFilter = ref('')
const assignedFilter = ref('')
const searchQuery = ref('')
const searchHint = ref('')
const internalLoading = ref(false)
const internalError = ref('')
const bookings = ref<StaffAppointment[]>([])
const searchMode = ref(false)
let searchTimer: ReturnType<typeof setTimeout> | null = null

const showLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.errorMessage || internalError.value)
const showError = computed(() => Boolean(displayError.value) && !showLoading.value)

const visibleBookings = computed(() => {
  if (props.appointments) return props.appointments
  return bookings.value
})

const showEmpty = computed(() => {
  if (showLoading.value || showError.value) return false
  if (props.empty) return true
  return visibleBookings.value.length === 0
})

function shortCode(value: string) {
  const text = String(value || '')
  return text.length > 8 ? `${text.slice(0, 8)}…` : text
}

async function loadSchedule() {
  if (props.appointments || props.loading || props.errorMessage || props.empty) return
  if (!props.apiBaseUrl) {
    bookings.value = []
    return
  }
  searchMode.value = false
  searchHint.value = ''
  internalLoading.value = true
  internalError.value = ''
  try {
    const result = await getDailySchedule(props.apiBaseUrl, selectedDate.value, {
      status: statusFilter.value || undefined,
      assignedTo: assignedFilter.value || undefined,
    })
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Bookings could not load.'
      bookings.value = []
      return
    }
    bookings.value = result.data.appointments
  } catch {
    internalError.value = 'Bookings could not load.'
    bookings.value = []
  } finally {
    internalLoading.value = false
  }
}

async function runServerSearch() {
  if (!props.apiBaseUrl) return
  const q = searchQuery.value.trim()
  if (q.length < 3) {
    searchHint.value = q ? 'Enter at least 3 characters to search.' : ''
    searchMode.value = false
    await loadSchedule()
    return
  }
  searchMode.value = true
  searchHint.value = ''
  internalLoading.value = true
  internalError.value = ''
  try {
    const result = await searchStaffBookings(props.apiBaseUrl, q)
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Search could not run.'
      bookings.value = []
      return
    }
    bookings.value = result.data.appointments
  } catch {
    internalError.value = 'Search could not run.'
    bookings.value = []
  } finally {
    internalLoading.value = false
  }
}

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    void runServerSearch()
  }, 300)
}

function onDateOrStatusChange() {
  if (searchQuery.value.trim().length >= 3) {
    void runServerSearch()
    return
  }
  void loadSchedule()
}

function reload() {
  if (searchQuery.value.trim().length >= 3) {
    void runServerSearch()
    return
  }
  void loadSchedule()
}

onMounted(() => {
  void loadSchedule()
})

onUnmounted(() => {
  if (searchTimer) clearTimeout(searchTimer)
})
</script>

<style scoped>
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem 1.1rem;
  margin-bottom: 1rem;
}

.toolbar label {
  display: grid;
  gap: 0.35rem;
  font-size: 0.85rem;
}

.toolbar input,
.toolbar select {
  font: inherit;
  min-width: 10rem;
  padding: 0.45rem 0.6rem;
  border-radius: 0.55rem;
  border: 1px solid color-mix(in srgb, var(--staff-ink, #2c2420) 14%, transparent);
  background: color-mix(in srgb, var(--staff-surface, #f7f3ee) 88%, white);
}

.search-hint {
  margin: 0 0 0.75rem;
  font-size: 0.85rem;
  color: color-mix(in srgb, var(--staff-ink, #2c2420) 62%, transparent);
}

.table-card {
  display: grid;
  gap: 0.55rem;
  padding: 1rem 1.1rem;
  border-radius: 1.1rem;
  background: color-mix(in srgb, var(--staff-surface, #f7f3ee) 92%, white);
  border: 1px solid color-mix(in srgb, var(--staff-ink, #2c2420) 8%, transparent);
}

.table-card__head,
.booking-row {
  display: grid;
  grid-template-columns: 4.5rem 1fr 6.5rem 1.2fr 0.9fr 0.9fr 0.9fr 4rem;
  gap: 0.55rem;
  align-items: center;
}

.table-card__head {
  font-size: 0.75rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--staff-ink, #2c2420) 55%, transparent);
}

.booking-row {
  padding: 0.55rem 0;
  border-top: 1px solid color-mix(in srgb, var(--staff-ink, #2c2420) 8%, transparent);
}

.code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.8rem;
}

.skeleton-row {
  height: 2.4rem;
  border-radius: 0.65rem;
  background: color-mix(in srgb, var(--staff-ink, #2c2420) 7%, transparent);
}

@media (max-width: 960px) {
  .table-card__head {
    display: none;
  }

  .booking-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
