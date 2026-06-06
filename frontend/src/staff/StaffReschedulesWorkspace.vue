<template>
  <StaffPortalShell title="Reschedules">
    <section class="workflow">
      <article v-for="item in requests" :key="item.reference">
        <p class="eyebrow">{{ item.status }}</p>
        <h2>{{ item.client }}</h2>
        <p>{{ item.copy }}</p>
        <button type="button" :disabled="item.disabled">Open reschedule flow</button>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import StaffPortalShell from './StaffPortalShell.vue'

const requests = [
  {
    reference: 'BK-1003',
    client: 'Wanjiku N.',
    status: 'Reschedule requested',
    copy: 'This booking can be rescheduled according to the booking policy.',
    disabled: false,
  },
  {
    reference: 'BK-1004',
    client: 'Muthoni R.',
    status: 'Recently completed',
    copy: 'No action needed right now.',
    disabled: true,
  },
]
</script>

<style scoped>
.workflow {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.workflow article {
  padding: 1.2rem;
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 28px;
  background: rgba(255, 253, 248, 0.84);
}

.eyebrow {
  margin: 0 0 0.4rem;
  color: #8a4f34;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.workflow button {
  min-height: 2.7rem;
  border: 0;
  border-radius: 999px;
  padding: 0 1rem;
  color: #fffaf3;
  background: #241611;
  font-weight: 900;
}

.workflow button:disabled {
  opacity: 0.52;
}

@media (max-width: 720px) {
  .workflow {
    grid-template-columns: 1fr;
  }
}
</style>
