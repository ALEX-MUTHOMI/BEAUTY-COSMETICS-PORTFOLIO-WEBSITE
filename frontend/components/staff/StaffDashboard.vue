<template>
  <StaffPortalShell title="Today" :api-base-url="apiBaseUrl">
    <template #actions>
      <NuxtLink class="action-link" to="/staff/bookings">Schedule</NuxtLink>
    </template>

    <section v-if="showLoading" class="desk-state" aria-label="Loading dashboard">
      <div v-for="index in 2" :key="index" class="skeleton-row" />
    </section>
    <section v-else-if="showError" class="desk-state" role="alert">
      <h2>Couldn’t load today.</h2>
      <p>{{ displayError }}</p>
      <button type="button" @click="loadSchedule">Try again</button>
    </section>
    <template v-else>
      <section v-if="isClosed" class="capacity capacity--closed" role="status">
        <p class="capacity__label">Studio</p>
        <p class="capacity__value">Closed</p>
        <p class="capacity__meta">No client bookings today</p>
      </section>
      <section v-else class="capacity" aria-label="Today’s capacity">
        <p class="capacity__label">Spots left</p>
        <p class="capacity__value">{{ capacity.remainingClients }}</p>
        <p class="capacity__meta">
          {{ capacity.bookedClients }} booked · {{ capacity.maxClients }} today
        </p>
      </section>

      <section class="appointments" aria-label="Next appointments">
        <header class="appointments__head">
          <h2>Next</h2>
          <NuxtLink class="appointments__link" to="/staff/bookings">All bookings</NuxtLink>
        </header>
        <p v-if="appointments.length === 0" class="empty-copy">{{ emptyCopy }}</p>
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

import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { staffLocalDateIso } from '~/src/staff/staffUxHelpers'
import { getDailySchedule, type StaffAppointment } from '~/src/staff/staffPortalApi'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
    loading?: boolean
    errorMessage?: string
    appointments?: StaffAppointment[]
    capacity?: { bookedClients: number; maxClients: number; remainingClients: number }
  }>(),
  {
    apiBaseUrl: '',
    loading: false,
    errorMessage: '',
    appointments: undefined,
    capacity: undefined,
  },
)

const internalLoading = ref(false)
const internalError = ref('')
const scheduleAppointments = ref<StaffAppointment[]>([])
const scheduleCapacity = ref({ bookedClients: 0, maxClients: 0, remainingClients: 0 })

const showLoading = computed(() => props.loading || internalLoading.value)
const displayError = computed(() => props.errorMessage || internalError.value)
const showError = computed(() => Boolean(displayError.value) && !showLoading.value)

const appointments = computed(() => {
  if (props.appointments) return props.appointments
  return scheduleAppointments.value
})

const capacity = computed(() => props.capacity ?? scheduleCapacity.value)

const isClosed = computed(() => capacity.value.maxClients <= 0)

const emptyCopy = computed(() => {
  if (isClosed.value) return 'Studio is closed today.'
  return 'No appointments yet.'
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
    const today = staffLocalDateIso()
    const result = await getDailySchedule(props.apiBaseUrl, today)
    if (!result.ok || !result.data) {
      internalError.value = result.message || 'Please check your connection and try again.'
      scheduleAppointments.value = []
      return
    }
    scheduleCapacity.value = result.data.capacity
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
  padding: 0 1rem;
  border: 0;
  border-radius: 0.85rem;
  color: #fff;
  background: #965f57;
  text-decoration: none;
  font: 600 0.72rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.action-link:hover {
  background: var(--color-rose-dark, #b5746c);
}

.desk-state {
  display: grid;
  gap: 0.75rem;
  margin-top: 0.35rem;
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  background: var(--color-paper, #fffcf8);
}

.desk-state h2 {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 1.25rem;
  font-weight: 400;
}

.desk-state p {
  margin: 0;
  color: var(--color-muted, #89858d);
}

.desk-state button {
  width: fit-content;
  min-height: 2.5rem;
  border: 0;
  padding: 0 0.9rem;
  color: #fff;
  background: var(--color-ink, #27272a);
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.capacity {
  margin-top: 0.25rem;
  padding: 1.15rem 1rem 1.25rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0.85rem;
  background: var(--color-paper, #fffcf8);
}

.capacity--closed {
  border-left: 3px solid var(--color-rose, #c98980);
}

.capacity__label {
  margin: 0 0 0.35rem;
  color: var(--color-muted, #89858d);
  font: 600 0.72rem/1.2 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.capacity__value {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(2.75rem, 14vw, 3.75rem);
  font-weight: 400;
  line-height: 0.95;
  letter-spacing: -0.03em;
  color: var(--color-ink, #27272a);
}

.capacity__meta {
  margin: 0.65rem 0 0;
  color: var(--color-muted, #89858d);
  font: 500 0.9rem/1.35 var(--font-body, 'Manrope', sans-serif);
}

.appointments {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0.85rem;
  background: var(--color-paper, #fffcf8);
}

.appointments__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.appointments__head h2 {
  margin: 0;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 1.35rem;
  font-weight: 400;
}

.appointments__link {
  color: var(--color-rose-dark, #b5746c);
  text-decoration: none;
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.empty-copy {
  margin: 0;
  color: var(--color-muted, #89858d);
  font-size: 0.95rem;
}

.timeline {
  display: grid;
  gap: 0.65rem;
}

.timeline article {
  display: grid;
  grid-template-columns: 4.25rem minmax(0, 1fr);
  gap: 0.35rem 0.85rem;
  align-items: start;
  padding: 0.85rem 0;
  border-top: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
}

.timeline article:first-child {
  border-top: 0;
  padding-top: 0;
}

.timeline strong {
  font: 600 0.95rem/1.3 var(--font-body, 'Manrope', sans-serif);
}

.timeline p,
.timeline span {
  margin: 0;
}

.timeline span {
  display: block;
  margin-top: 0.15rem;
  color: var(--color-muted, #89858d);
  font-size: 0.85rem;
}

.timeline :deep(.status-chip),
.timeline a {
  grid-column: 2;
  justify-self: start;
}

.timeline a {
  min-height: 2.25rem;
  display: inline-flex;
  align-items: center;
  margin-top: 0.15rem;
  padding: 0 0.75rem;
  border: 0;
  color: #fff;
  background: var(--color-ink, #27272a);
  text-decoration: none;
  font: 600 0.72rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.skeleton-row {
  min-height: 3.5rem;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), var(--color-stone, #efeae3), var(--color-rose-soft, #f5e8e6));
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (min-width: 720px) {
  .capacity {
    padding: 1.35rem 1.35rem 1.5rem;
  }

  .appointments {
    padding: 1.25rem 1.35rem;
  }

  .timeline article {
    grid-template-columns: 5rem minmax(0, 1fr) auto auto;
    align-items: center;
    gap: 1rem;
    padding: 1rem 0;
  }

  .timeline :deep(.status-chip),
  .timeline a {
    grid-column: auto;
    justify-self: auto;
    margin-top: 0;
  }
}
</style>
