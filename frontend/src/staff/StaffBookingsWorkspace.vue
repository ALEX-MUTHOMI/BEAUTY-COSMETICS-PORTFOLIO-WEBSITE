<template>
  <StaffPortalShell title="Bookings">
    <section class="toolbar" aria-label="Booking filters">
      <label>
        Date
        <input v-model="selectedDate" type="date" @change="loadSchedule" />
      </label>
      <label>
        Status
        <select v-model="statusFilter" @change="loadSchedule">
          <option value="">All bookings</option>
          <option value="confirmed">Booking confirmed</option>
          <option value="held">Awaiting payment</option>
          <option value="cancelled">Cancelled</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <label>
        Search
        <input v-model="searchQuery" placeholder="Client or booking reference" />
      </label>
    </section>

    <section v-if="showLoading" class="table-card table-card--state" aria-label="Loading bookings">
      <div v-for="index in 4" :key="index" class="skeleton-row" />
    </section>
    <section v-else-if="showError" class="table-card table-card--state" role="alert">
      <h2>Bookings could not load.</h2>
      <p>{{ displayError }}</p>
      <button type="button" @click="loadSchedule">Try again</button>
    </section>
    <section v-else-if="showEmpty" class="table-card table-card--state">
      <h2>No bookings found.</h2>
      <p>Try a different date, payment status, or booking reference.</p>
    </section>
    <section v-else class="table-card" aria-label="Staff bookings list">
      <div class="table-card__head">
        <span>Time</span>
        <span>Client</span>
        <span>Service</span>
        <span>Booking</span>
        <span>Payment</span>
        <span>Actions</span>
      </div>
      <article v-for="booking in visibleBookings" :key="booking.publicBookingId" class="booking-row">
        <strong>{{ booking.time }}</strong>
        <span>{{ booking.client }}</span>
        <span>{{ booking.service }}</span>
        <StaffStatusChip :status="booking.bookingStatus" />
        <StaffStatusChip :status="booking.paymentStatus" />
        <NuxtLink :to="`/staff/bookings/${booking.publicBookingId}`">Open</NuxtLink>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { getDailySchedule, type StaffAppointment } from './staffPortalApi'

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
const searchQuery = ref('')
const internalLoading = ref(false)
const internalError = ref('')
const bookings = ref<StaffAppointment[]>([])

const showLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.errorMessage || internalError.value)
const showError = computed(() => Boolean(displayError.value) && !showLoading.value)

const sourceBookings = computed(() => {
  if (props.appointments) return props.appointments
  return bookings.value
})

const visibleBookings = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return sourceBookings.value
  return sourceBookings.value.filter((booking) => {
    const haystack = `${booking.client} ${booking.service} ${booking.publicBookingId} ${booking.bookingReference || ''}`.toLowerCase()
    return haystack.includes(query)
  })
})

const showEmpty = computed(() => {
  if (showLoading.value || showError.value) return false
  if (props.empty) return true
  return visibleBookings.value.length === 0
})

async function loadSchedule() {
  if (props.appointments || props.loading || props.errorMessage || props.empty) return
  if (!props.apiBaseUrl) {
    bookings.value = []
    return
  }
  internalLoading.value = true
  internalError.value = ''
  try {
    const result = await getDailySchedule(props.apiBaseUrl, selectedDate.value, {
      status: statusFilter.value || undefined,
    })
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Please check your connection and try again.'
      bookings.value = []
      return
    }
    bookings.value = result.data.appointments
  } catch {
    internalError.value = 'Please check your connection and try again.'
    bookings.value = []
  } finally {
    internalLoading.value = false
  }
}

onMounted(() => {
  void loadSchedule()
})

watch(
  () => props.apiBaseUrl,
  () => {
    void loadSchedule()
  },
)
</script>

<style scoped>
.toolbar,
.table-card {
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 28px;
  background: rgba(255, 253, 248, 0.82);
}

.toolbar {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.toolbar label {
  display: grid;
  gap: 0.4rem;
  font-weight: 800;
}

.toolbar input,
.toolbar select {
  min-height: 2.6rem;
  border: 1px solid rgba(55, 32, 22, 0.16);
  border-radius: 14px;
  padding: 0 0.75rem;
}

.table-card {
  overflow: hidden;
}

.table-card--state {
  display: grid;
  gap: 0.75rem;
  padding: 1.25rem;
}

.table-card__head,
.booking-row {
  display: grid;
  grid-template-columns: 0.8fr 1.1fr 1.4fr 1fr 1fr 0.7fr;
  gap: 0.75rem;
  align-items: center;
  padding: 0.85rem 1rem;
}

.table-card__head {
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 900;
  background: rgba(55, 32, 22, 0.06);
}

.booking-row + .booking-row {
  border-top: 1px solid rgba(55, 32, 22, 0.08);
}

.booking-row a,
.table-card--state button {
  min-height: 2.4rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.9rem;
  border: 0;
  border-radius: 999px;
  background: #241611;
  color: #fffaf3;
  text-decoration: none;
  font-weight: 800;
  cursor: pointer;
}

.skeleton-row {
  height: 3rem;
  margin: 0.75rem 1rem;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(55, 32, 22, 0.06), rgba(55, 32, 22, 0.12), rgba(55, 32, 22, 0.06));
  background-size: 200% 100%;
  animation: shimmer 1.2s linear infinite;
}

@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}

@media (max-width: 900px) {
  .toolbar,
  .table-card__head,
  .booking-row {
    grid-template-columns: 1fr;
  }

  .table-card__head {
    display: none;
  }
}
</style>
