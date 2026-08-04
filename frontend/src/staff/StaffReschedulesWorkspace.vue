<template>
  <StaffPortalShell title="Reschedules" :api-base-url="apiBaseUrl">
    <section v-if="loading" class="workflow workflow--state" aria-label="Loading reschedules">
      <div v-for="index in 2" :key="index" class="skeleton" />
    </section>
    <section v-else-if="errorMessage" class="workflow workflow--state" role="alert">
      <h2>Reschedules could not load.</h2>
      <p>{{ errorMessage }}</p>
      <button type="button" @click="loadQueue">Try again</button>
    </section>
    <section v-else-if="items.length === 0" class="workflow workflow--state">
      <h2>No open moves right now.</h2>
      <p>Open a booking to choose a new time, or wait for a customer reschedule request.</p>
      <NuxtLink class="workflow__link" to="/staff/bookings">Go to bookings</NuxtLink>
    </section>
    <section v-else class="workflow">
      <article v-for="item in items" :key="item.publicBookingId">
        <p class="eyebrow">{{ queueLabel(item) }}</p>
        <h2>{{ item.client }}</h2>
        <p>
          {{ item.time }} · {{ item.service }}
          <span v-if="item.bookingReference" class="code"> · {{ shortCode(item.bookingReference) }}</span>
        </p>
        <StaffStatusChip :status="item.rescheduleStatus === 'none' ? item.bookingStatus : item.rescheduleStatus" />
        <NuxtLink :to="`/staff/bookings/${item.publicBookingId}`">Open reschedule</NuxtLink>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'
import { getStaffRescheduleQueue, type StaffAppointment } from './staffPortalApi'
import { friendlyStatus } from './statusCopy'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
  }>(),
  { apiBaseUrl: '' },
)

const loading = ref(false)
const errorMessage = ref('')
const items = ref<StaffAppointment[]>([])

function shortCode(value: string) {
  const text = String(value || '')
  return text.length > 8 ? `${text.slice(0, 8)}…` : text
}

function queueLabel(item: StaffAppointment) {
  if (String(item.rescheduleStatus).toLowerCase() === 'requested') {
    return friendlyStatus('reschedule_requested')
  }
  return 'Confirmed — ready to move'
}

async function loadQueue() {
  if (!props.apiBaseUrl) {
    items.value = []
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await getStaffRescheduleQueue(props.apiBaseUrl)
    if (!result.ok || !result.data) {
      errorMessage.value = result.message || 'Reschedule queue could not load.'
      items.value = []
      return
    }
    items.value = result.data.appointments
  } catch {
    errorMessage.value = 'Reschedule queue could not load.'
    items.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadQueue()
})
</script>

<style scoped>
.workflow {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.workflow--state {
  grid-template-columns: 1fr;
  padding: 1.25rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  background: var(--color-paper, #fffcf8);
}

.workflow article {
  display: grid;
  gap: 0.65rem;
  padding: 1.2rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  background: var(--color-paper, #fffcf8);
}

.eyebrow {
  margin: 0;
  color: var(--color-rose-dark, #b5746c);
  font: 600 0.72rem/1.2 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.workflow h2,
.workflow p {
  margin: 0;
  font-family: var(--font-body, 'Manrope', sans-serif);
}

.workflow h2 {
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-weight: 400;
}

.code {
  color: var(--color-muted, #8a8580);
  font-size: 0.85rem;
}

.workflow a,
.workflow button,
.workflow__link {
  min-height: 2.7rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  padding: 0 1rem;
  color: #fff;
  background: var(--color-ink, #27272a);
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
}

.skeleton {
  min-height: 8rem;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), var(--color-stone, #efeae3), var(--color-rose-soft, #f5e8e6));
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 720px) {
  .workflow {
    grid-template-columns: 1fr;
  }
}
</style>
