<template>
  <StaffPortalShell title="Today at a glance">
    <template #actions>
      <NuxtLink class="action-link" to="/staff/bookings">View today&apos;s schedule</NuxtLink>
    </template>

    <StaffPortalCards label="Dashboard summary" :cards="cards" />

    <section class="panel">
      <div>
        <p class="eyebrow">Next appointments</p>
        <h2>Keep the day moving smoothly.</h2>
      </div>
      <div class="timeline">
        <article v-for="booking in appointments" :key="booking.publicBookingId">
          <strong>{{ booking.time }}</strong>
          <div>
            <p>{{ booking.client }}</p>
            <span>{{ booking.service }}</span>
          </div>
          <StaffStatusChip :status="booking.paymentStatus" />
        </article>
      </div>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import StaffPortalCards from './StaffPortalCards.vue'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'

const cards = [
  { label: 'Today', value: 6, hint: 'Appointments on your schedule' },
  { label: 'Upcoming', value: 14, hint: 'Next seven days' },
  { label: 'Payments', value: 2, hint: 'Need a quick look' },
  { label: 'Full-package day', value: 'Tue/Wed', hint: 'Special capacity rules' },
]

const appointments = [
  {
    publicBookingId: 'BK-1001',
    time: '09:00',
    client: 'Grace M.',
    service: 'Soft glam makeup',
    paymentStatus: 'paid',
  },
  {
    publicBookingId: 'BK-1002',
    time: '11:30',
    client: 'Amina K.',
    service: 'Facial / skincare',
    paymentStatus: 'payment_pending',
  },
]
</script>

<style scoped>
.action-link {
  min-height: 2.8rem;
  display: inline-flex;
  align-items: center;
  padding: 0 1rem;
  border-radius: 999px;
  color: #fffaf3;
  background: #241611;
  text-decoration: none;
  font-weight: 900;
}

.panel {
  margin-top: 1rem;
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 32px;
  background: rgba(255, 253, 248, 0.78);
}

.eyebrow {
  margin: 0 0 0.4rem;
  color: #8a4f34;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-weight: 900;
}

.panel h2 {
  margin: 0 0 1rem;
}

.timeline {
  display: grid;
  gap: 0.8rem;
}

.timeline article {
  display: grid;
  grid-template-columns: 5rem minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border-radius: 22px;
  background: #fffaf3;
}

.timeline p,
.timeline span {
  margin: 0;
}

@media (max-width: 640px) {
  .timeline article {
    grid-template-columns: 1fr;
  }
}
</style>
