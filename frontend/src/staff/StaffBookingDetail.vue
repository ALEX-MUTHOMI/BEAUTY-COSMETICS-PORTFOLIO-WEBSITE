<template>
  <StaffPortalShell title="Booking detail">
    <section class="detail-card">
      <p class="eyebrow">Appointment</p>
      <h2>Grace M. · Soft glam makeup</h2>
      <div class="detail-grid">
        <span>Today, 09:00</span>
        <StaffStatusChip status="confirmed" />
        <StaffStatusChip status="paid" />
        <span>KES 4,500</span>
      </div>
      <div class="actions">
        <button type="button" @click="showReauth = true">Reveal customer contact</button>
        <button type="button" :disabled="completed" @click="completed = true">
          {{ completed ? 'Service completed' : 'Mark service completed' }}
        </button>
        <NuxtLink to="/staff/reschedules">Reschedule booking</NuxtLink>
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
import { ref } from 'vue'

import StaffContactRevealModal from './StaffContactRevealModal.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'

const props = withDefaults(
  defineProps<{
    /** Injected by Nuxt pages — never call useRuntimeConfig inside src/ components. */
    apiBaseUrl?: string
  }>(),
  { apiBaseUrl: '' },
)

const showReauth = ref(false)
const completed = ref(false)

function onReauthConfirmed() {
  showReauth.value = false
}
</script>

<style scoped>
.detail-card {
  display: grid;
  gap: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 32px;
  background: rgba(255, 253, 248, 0.86);
}

.eyebrow {
  margin: 0;
  color: #8a4f34;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 900;
}

.detail-card h2 {
  margin: 0;
}

.detail-grid,
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.actions button,
.actions a {
  min-height: 2.8rem;
  display: inline-flex;
  align-items: center;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  color: #fffaf3;
  background: #241611;
  text-decoration: none;
  font-weight: 900;
}

.actions button:disabled {
  opacity: 0.6;
}
</style>
