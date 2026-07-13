<template>
  <StaffPortalShell title="Today at a glance" :api-base-url="apiBaseUrl">
    <template #actions>
      <NuxtLink class="action-link" to="/staff/bookings">View today&apos;s schedule</NuxtLink>
    </template>

    <section v-if="showLoading" class="panel panel--state" aria-label="Loading dashboard">
      <div v-for="index in 3" :key="index" class="skeleton-row" />
    </section>
    <section v-else-if="showError" class="panel panel--state" role="alert">
      <h2>Today&apos;s desk could not load.</h2>
      <p>{{ displayError }}</p>
      <button type="button" @click="loadSchedule">Try again</button>
    </section>
    <template v-else>
      <StaffPortalCards label="Dashboard summary" :cards="cards" />

      <section class="panel">
        <div>
          <p class="eyebrow">Next appointments</p>
          <h2>Keep the day moving smoothly.</h2>
        </div>
        <p v-if="appointments.length === 0" class="empty-copy">No appointments on today&apos;s schedule yet.</p>
        <div v-else class="timeline">
          <article v-for="booking in appointments" :key="booking.publicBookingId">
            <strong>{{ booking.time }}</strong>
            <div>
              <p>{{ booking.client }}</p>
              <span>{{ booking.service }}</span>
            </div>
            <StaffStatusChip :status="booking.paymentStatus" />
            <NuxtLink :to="`/staff/bookings/${booking.publicBookingId}`">Open</NuxtLink>
          </article>
        </div>
      </section>
    </template>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import StaffPortalCards from './StaffPortalCards.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { getDailySchedule, type StaffAppointment } from './staffPortalApi'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
    loading?: boolean
    errorMessage?: string
    appointments?: StaffAppointment[]
  }>(),
  {
    apiBaseUrl: '',
    loading: false,
    errorMessage: '',
    appointments: undefined,
  },
)

const internalLoading = ref(false)
const internalError = ref('')
const scheduleAppointments = ref<StaffAppointment[]>([])
const capacity = ref({ bookedClients: 0, maxClients: 0, remainingClients: 0 })

const showLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.errorMessage || internalError.value)
const showError = computed(() => Boolean(displayError.value) && !showLoading.value)

const appointments = computed(() => {
  if (props.appointments) return props.appointments
  return scheduleAppointments.value
})

const cards = computed(() => {
  const rows = appointments.value
  const awaiting = rows.filter((row) => {
    const status = row.paymentStatus.toLowerCase()
    return status.includes('pending') || status === 'not_paid' || status === 'held'
  }).length
  const paid = rows.filter((row) => {
    const status = row.paymentStatus.toLowerCase()
    return status === 'paid' || status === 'success'
  }).length
  return [
    {
      label: 'Today',
      value: capacity.value.bookedClients || rows.length,
      hint: 'Appointments on your schedule',
    },
    {
      label: 'Capacity left',
      value: capacity.value.remainingClients,
      hint: capacity.value.maxClients ? `Of ${capacity.value.maxClients} client slots` : 'Open slots today',
    },
    {
      label: 'Paid',
      value: paid,
      hint: 'Payment confirmed',
    },
    {
      label: 'Awaiting',
      value: awaiting,
      hint: 'Need a quick look',
    },
  ]
})

async function loadSchedule() {
  if (props.appointments || props.loading || props.errorMessage) return
  if (!props.apiBaseUrl) {
    scheduleAppointments.value = []
    return
  }
  internalLoading.value = true
  internalError.value = ''
  try {
    const today = new Date().toISOString().slice(0, 10)
    const result = await getDailySchedule(props.apiBaseUrl, today)
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Please check your connection and try again.'
      scheduleAppointments.value = []
      return
    }
    capacity.value = result.data.capacity
    scheduleAppointments.value = result.data.appointments
  } catch {
    internalError.value = 'Please check your connection and try again.'
    scheduleAppointments.value = []
  } finally {
    internalLoading.value = false
  }
}

onMounted(() => {
  void loadSchedule()
})
</script>

<style scoped>
.action-link {
  min-height: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 1.1rem;
  border: 0;
  border-radius: 0;
  color: #fff;
  background: var(--color-rose, #c98980);
  text-decoration: none;
  font: 600 0.74rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition:
    background 0.2s var(--ease-story, ease),
    transform 0.2s var(--ease-story, ease);
}

.action-link:hover {
  background: var(--color-rose-dark, #b5746c);
}

.action-link:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 3px rgba(201, 137, 128, 0.28);
}

.panel {
  margin-top: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
}

.panel--state {
  display: grid;
  gap: 0.75rem;
}

.eyebrow {
  margin: 0 0 0.4rem;
  color: var(--color-rose-dark, #c97f76);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font: 600 0.72rem/1.2 var(--font-body, 'Manrope', sans-serif);
}

.panel h2 {
  margin: 0 0 1rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
}

.empty-copy {
  margin: 0;
  color: var(--color-muted, #89858d);
}

.timeline {
  display: grid;
  gap: 0.8rem;
}

.timeline article {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr) auto auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: var(--color-cream, #fcf5f5);
}

.timeline p,
.timeline span {
  margin: 0;
}

.timeline a,
.panel--state button {
  min-height: 2.4rem;
  display: inline-flex;
  align-items: center;
  padding: 0 0.9rem;
  border: 0;
  color: #fff;
  background: var(--color-ink, #27272a);
  text-decoration: none;
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.skeleton-row {
  min-height: 3.5rem;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), #fff, var(--color-rose-soft, #f5e8e6));
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 640px) {
  .timeline article {
    grid-template-columns: 1fr;
  }
}
</style>
