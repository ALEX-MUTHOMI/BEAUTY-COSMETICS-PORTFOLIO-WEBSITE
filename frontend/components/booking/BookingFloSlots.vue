<template>
  <section v-if="isoDate" class="flo-slots" aria-live="polite">
    <header class="flo-slots__head">
      <h3>Choose a time</h3>
      <p>{{ dateLabel }}</p>
    </header>

    <p v-if="loading" class="flo-slots__loading">Loading times…</p>

    <div v-else-if="slots.length === 0" class="flo-slots__empty">
      No open times for this day. Try another date.
    </div>

    <div v-else class="flo-slots__grid" role="group" aria-label="Available times">
      <button
        v-for="slot in slots"
        :key="`${slot.startsAt}:${slot.resourcePublicId}`"
        type="button"
        class="flo-slots__btn"
        :class="{ 'flo-slots__btn--active': selectedSlot?.startsAt === slot.startsAt }"
        :aria-pressed="selectedSlot?.startsAt === slot.startsAt"
        @click="emit('select', slot)"
      >
        {{ formatSlotLabel(slot.startsAt) }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatSlotLabel, type BookingSlot } from '@/booking/bookingPublicApi'

const props = defineProps<{
  isoDate: string | null
  slots: BookingSlot[]
  selectedSlot: BookingSlot | null
  loading?: boolean
}>()

const emit = defineEmits<{ select: [slot: BookingSlot] }>()

const dateLabel = computed(() => {
  if (!props.isoDate) return ''
  const parts = props.isoDate.split('-').map(Number)
  const year = parts[0]
  const month = parts[1]
  const day = parts[2]
  if (!year || !month || !day) return props.isoDate
  const utc = new Date(Date.UTC(year, month - 1, day, 12, 0, 0))
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Africa/Nairobi',
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(utc)
})
</script>

<style scoped>
.flo-slots {
  margin-top: 1.25rem;
  padding: 1.15rem;
  border-radius: 12px;
  background: #fff;
  border: 1px solid var(--color-line);
  box-shadow: 0 8px 24px rgba(39, 37, 42, 0.05);
}

.flo-slots__head h3 {
  margin: 0 0 0.2rem;
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 400;
}

.flo-slots__head p {
  margin: 0 0 0.85rem;
  font: 500 0.82rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__loading,
.flo-slots__empty {
  margin: 0;
  font: 500 0.9rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.flo-slots__btn {
  min-height: 2.85rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: #fff;
  font: 600 0.84rem var(--font-body);
  color: var(--color-ink);
  cursor: pointer;
}

.flo-slots__btn:hover {
  border-color: var(--color-rose);
}

.flo-slots__btn--active {
  border-color: var(--color-rose);
  background: var(--color-rose-soft);
}

@media (min-width: 520px) {
  .flo-slots__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
