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

    <template v-else>
      <div class="flo-slots__grid" role="group" aria-label="Available times">
        <button
          v-for="slot in visibleSlots"
          :key="`${slot.startsAt}:${slot.resourcePublicId}`"
          type="button"
          class="flo-slots__btn"
          :class="{ 'flo-slots__btn--active': selectedSlot?.startsAt === slot.startsAt }"
          :aria-pressed="selectedSlot?.startsAt === slot.startsAt"
          :disabled="loading"
          @click="emit('select', slot)"
        >
          {{ formatSlotLabel(slot.startsAt) }}
        </button>
      </div>

      <button
        v-if="hasMoreSlots"
        type="button"
        class="flo-slots__more"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        {{ expanded ? 'Show fewer times' : 'Show more times' }}
      </button>
    </template>

    <p v-if="selectionSummary" class="flo-slots__confirm">
      {{ selectionSummary }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { formatSlotLabel, type BookingSlot } from '@/booking/bookingPublicApi'

const SLOT_COLLAPSED_COUNT = 8

const props = defineProps<{
  isoDate: string | null
  slots: BookingSlot[]
  selectedSlot: BookingSlot | null
  loading?: boolean
}>()

const emit = defineEmits<{ select: [slot: BookingSlot] }>()

const expanded = ref(false)

watch(
  () => props.isoDate,
  () => {
    expanded.value = false
  },
)

const hasMoreSlots = computed(() => props.slots.length > SLOT_COLLAPSED_COUNT)

const visibleSlots = computed(() => {
  if (expanded.value || props.slots.length <= SLOT_COLLAPSED_COUNT) return props.slots
  return props.slots.slice(0, SLOT_COLLAPSED_COUNT)
})

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

const selectionSummary = computed(() => {
  if (!props.isoDate || !props.selectedSlot) return ''
  const parts = props.isoDate.split('-').map(Number)
  const year = parts[0]
  const month = parts[1]
  const day = parts[2]
  if (!year || !month || !day) return ''
  const utc = new Date(Date.UTC(year, month - 1, day, 12, 0, 0))
  const dayPart = new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Africa/Nairobi',
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  }).format(utc)
  const timePart = formatSlotLabel(props.selectedSlot.startsAt)
  if (!timePart) return ''
  return `${dayPart} · ${timePart}`
})
</script>

<style scoped>
.flo-slots {
  margin-top: 0.9rem;
  padding: 0.95rem 1rem 1rem;
  border-radius: 12px;
  background: #fff;
  border: 1px solid var(--color-line);
  box-shadow: 0 8px 24px rgba(39, 37, 42, 0.05);
}

.flo-slots__head h3 {
  margin: 0 0 0.15rem;
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 400;
}

.flo-slots__head p {
  margin: 0 0 0.7rem;
  font: 500 0.8rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__loading,
.flo-slots__empty {
  margin: 0;
  font: 500 0.88rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
}

.flo-slots__btn {
  min-height: 2.65rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: #fff;
  font: 600 0.82rem var(--font-body);
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

.flo-slots__more {
  margin-top: 0.55rem;
  padding: 0.35rem 0.15rem;
  border: 0;
  background: transparent;
  color: var(--color-rose-dark);
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 0.15em;
}

.flo-slots__more:hover {
  color: var(--color-rose);
}

.flo-slots__confirm {
  margin: 0.75rem 0 0;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  background: var(--color-rose-soft, #f8ebe8);
  font: 600 0.84rem var(--font-body);
  color: var(--color-ink);
  text-align: center;
}

@media (min-width: 520px) {
  .flo-slots__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
