<template>
  <StaffPortalShell title="Payments">
    <StaffPortalCards label="Payment overview" :cards="cards" :loading="props.loading" />
    <section v-if="props.loading" class="list-panel" aria-label="Loading payment records">
      <div v-for="index in 4" :key="index" class="payment-skeleton" />
    </section>
    <section v-else-if="props.errorMessage" class="list-panel list-panel--state" role="alert">
      <h2>Payments could not load.</h2>
      <p>{{ props.errorMessage }}</p>
      <button type="button">Try again</button>
    </section>
    <section v-else-if="props.empty" class="list-panel list-panel--state">
      <h2>No payment records found.</h2>
      <p>Try a different date or payment status.</p>
    </section>
    <section v-else class="list-panel" aria-label="Payment records">
      <article v-for="payment in payments" :key="payment.reference">
        <div>
          <strong>{{ payment.client }}</strong>
          <span>{{ payment.service }}</span>
        </div>
        <span>{{ payment.amount }}</span>
        <StaffStatusChip :status="payment.status" />
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import StaffPortalCards from './StaffPortalCards.vue'
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

const cards = [
  { label: 'Confirmed', value: 'KES 18k', hint: 'Paid bookings' },
  { label: 'Awaiting', value: 2, hint: 'Customer action needed' },
  { label: 'Needs review', value: 0, hint: 'No open issues' },
  { label: 'Receipts', value: 'Ready', hint: 'Customer-safe copies' },
]

const payments = [
  { reference: 'BK-1001', client: 'Grace M.', service: 'Soft glam makeup', amount: 'KES 4,500', status: 'paid' },
  { reference: 'BK-1002', client: 'Amina K.', service: 'Full package', amount: 'KES 12,000', status: 'payment_pending' },
]
</script>

<style scoped>
.list-panel {
  display: grid;
  gap: 0.8rem;
  margin-top: 1rem;
}

.list-panel article {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 24px;
  background: rgba(255, 253, 248, 0.84);
}

.list-panel div {
  display: grid;
  gap: 0.2rem;
}

.list-panel span {
  color: #76513d;
}

.list-panel--state {
  padding: 1rem;
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 24px;
  background: rgba(255, 253, 248, 0.84);
}

.list-panel--state h2,
.list-panel--state p {
  margin: 0;
}

.list-panel--state button {
  width: max-content;
  min-height: 2.7rem;
  border: 0;
  border-radius: 999px;
  padding: 0 1rem;
  color: #fffaf3;
  background: #241611;
  font-weight: 900;
}

.payment-skeleton {
  min-height: 4rem;
  border-radius: 24px;
  background: linear-gradient(90deg, #ead7c3, #fff8ef, #ead7c3);
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 640px) {
  .list-panel article {
    grid-template-columns: 1fr;
  }
}
</style>
