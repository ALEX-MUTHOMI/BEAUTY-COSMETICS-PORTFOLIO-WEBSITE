<template>
  <StaffPortalShell title="Bookings">
    <section class="toolbar" aria-label="Booking filters">
      <label>Date <input v-model="selectedDate" type="date" /></label>
      <label>Status <select><option>All bookings</option><option>Booking confirmed</option></select></label>
      <label>Search <input placeholder="Client or booking reference" /></label>
    </section>

    <section v-if="props.loading" class="table-card table-card--state" aria-label="Loading bookings">
      <div v-for="index in 4" :key="index" class="skeleton-row" />
    </section>
    <section v-else-if="props.errorMessage" class="table-card table-card--state" role="alert">
      <h2>Bookings could not load.</h2>
      <p>{{ props.errorMessage }}</p>
      <button type="button">Try again</button>
    </section>
    <section v-else-if="props.empty" class="table-card table-card--state">
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
      <article v-for="booking in bookings" :key="booking.publicBookingId" class="booking-row">
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
import { ref } from 'vue'

import StaffPortalShell from './StaffPortalShell.vue'
import StaffStatusChip from './StaffStatusChip.vue'

const props = withDefaults(
  defineProps<{
    loading?: boolean
    empty?: boolean
    errorMessage?: string
  }>(),
  {
    loading: false,
    empty: false,
    errorMessage: '',
  },
)

const selectedDate = ref(new Date().toISOString().slice(0, 10))
const bookings = [
  {
    publicBookingId: 'BK-1001',
    time: '09:00',
    client: 'Grace M.',
    service: 'Soft glam makeup',
    bookingStatus: 'confirmed',
    paymentStatus: 'paid',
  },
  {
    publicBookingId: 'BK-1002',
    time: '11:30',
    client: 'Amina K.',
    service: 'Full package',
    bookingStatus: 'held',
    paymentStatus: 'payment_pending',
  },
]
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
  font-weight: 850;
}

.toolbar input,
.toolbar select {
  min-height: 2.8rem;
  border: 1px solid rgba(55, 32, 22, 0.16);
  border-radius: 16px;
  padding: 0 0.8rem;
  background: #fffaf3;
}

.table-card {
  overflow: hidden;
}

.table-card--state {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
}

.table-card--state h2,
.table-card--state p {
  margin: 0;
}

.table-card--state button {
  width: max-content;
  min-height: 2.7rem;
  border: 0;
  border-radius: 999px;
  padding: 0 1rem;
  color: #fffaf3;
  background: #241611;
  font-weight: 900;
}

.skeleton-row {
  min-height: 3.4rem;
  border-radius: 18px;
  background: linear-gradient(90deg, #ead7c3, #fff8ef, #ead7c3);
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

.table-card__head,
.booking-row {
  display: grid;
  grid-template-columns: 5rem 1fr 1.5fr 1fr 1fr 5rem;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
}

.table-card__head {
  color: #76513d;
  background: #f3e2d0;
  font-weight: 900;
}

.booking-row:not(:last-child) {
  border-bottom: 1px solid rgba(55, 32, 22, 0.1);
}

@media (max-width: 820px) {
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
