<template>
  <section v-if="isoDate" class="flo-slots" aria-live="polite">
    <header class="flo-slots__head">
      <p class="flo-slots__eyebrow">Your hour</p>
      <h3>Choose a start time</h3>
      <p class="flo-slots__date">{{ dateLabel }}</p>
      <p v-if="durationHint" class="flo-slots__hint">{{ durationHint }}</p>
    </header>

    <div
      v-if="loading"
      class="flo-slots__pending"
      role="status"
      aria-live="polite"
      aria-label="Checking open hours"
    >
      <p class="flo-slots__loading">Checking open hours…</p>
      <div class="flo-slots__skeleton" aria-hidden="true">
        <div
          v-for="n in 3"
          :key="n"
          class="flo-slots__skel-btn flo-slots__skel-shimmer"
        />
      </div>
    </div>

    <div v-else-if="slots.length === 0" class="flo-slots__empty">
      No open times for this day. Try another date.
    </div>

    <template v-else>
      <div class="flo-slots__timeline" role="list">
        <article
          v-for="group in visibleGroups"
          :key="group.hourLabel"
          class="flo-slots__band"
          role="listitem"
        >
          <header class="flo-slots__band-head">
            <h4 class="flo-slots__hour">{{ group.hourLabel }}</h4>
            <span class="flo-slots__count">
              {{ group.slots.length }}
              {{ group.slots.length === 1 ? 'opening' : 'openings' }}
            </span>
          </header>
          <div
            class="flo-slots__grid"
            role="group"
            :aria-label="`${group.hourLabel} openings`"
          >
            <button
              v-for="slot in group.slots"
              :key="`${slot.startsAt}:${slot.resourcePublicId}`"
              type="button"
              class="flo-slots__btn"
              :class="{
                'flo-slots__btn--active': isSameBookingSlot(selectedSlot, slot),
              }"
              :aria-pressed="isSameBookingSlot(selectedSlot, slot)"
              :disabled="loading"
              @click="emit('select', slot)"
            >
              <span class="flo-slots__btn-start">
                {{
                  slot.endsAt
                    ? formatSlotRange(slot.startsAt, slot.endsAt)
                    : formatSlotLabel(slot.startsAt)
                }}
              </span>
            </button>
          </div>
        </article>
      </div>

      <button
        v-if="hasMoreHours"
        type="button"
        class="flo-slots__more"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        {{ expanded ? 'Show fewer hours' : `Show later hours (+${hiddenHourCount})` }}
      </button>
    </template>

    <p v-if="selectionSummary" class="flo-slots__confirm">
      <span class="flo-slots__confirm-label">Held for checkout</span>
      <span class="flo-slots__confirm-value">{{ selectionSummary }}</span>
    </p>
  </section>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  formatSlotHourBand,
  formatSlotLabel,
  formatSlotRange,
  isSameBookingSlot,
  type BookingSlot,
} from '@/booking/bookingPublicApi'

/** Collapse by whole hour bands so we never split an hour mid-grid. */
const HOUR_BANDS_COLLAPSED = 3

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

/** Group backend-offered slots by Nairobi hour — never invent start times. */
function groupSlotsByHour(slots: BookingSlot[]): { hourLabel: string; slots: BookingSlot[] }[] {
  const buckets = new Map<string, BookingSlot[]>()
  for (const slot of slots) {
    const hourKey = formatSlotHourBand(slot.startsAt) || formatSlotLabel(slot.startsAt)
    if (!hourKey) continue
    const list = buckets.get(hourKey) ?? []
    list.push(slot)
    buckets.set(hourKey, list)
  }
  return Array.from(buckets.entries()).map(([hourLabel, groupSlots]) => ({
    hourLabel,
    slots: groupSlots,
  }))
}

const allGroups = computed(() => groupSlotsByHour(props.slots))

const hasMoreHours = computed(() => allGroups.value.length > HOUR_BANDS_COLLAPSED)

const hiddenHourCount = computed(() =>
  Math.max(0, allGroups.value.length - HOUR_BANDS_COLLAPSED),
)

const visibleGroups = computed(() => {
  if (expanded.value || allGroups.value.length <= HOUR_BANDS_COLLAPSED) {
    return allGroups.value
  }
  return allGroups.value.slice(0, HOUR_BANDS_COLLAPSED)
})

const durationHint = computed(() => {
  const first = props.slots[0]
  if (!first?.durationMinutes) return ''
  const buffer = first.bufferMinutes > 0 ? ` · ${first.bufferMinutes} min turnaround` : ''
  return `${first.durationMinutes} min visit${buffer}`
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
  const range = formatSlotRange(props.selectedSlot.startsAt, props.selectedSlot.endsAt)
  if (!range) return ''
  const mins = props.selectedSlot.durationMinutes
  return mins ? `${dayPart} · ${range} · ${mins} min` : `${dayPart} · ${range}`
})
</script>

<style scoped>
.flo-slots {
  margin-top: 0.9rem;
  padding: 1.05rem 1rem 1.1rem;
  border-radius: 14px;
  background:
    linear-gradient(165deg, rgba(255, 255, 255, 0.92) 0%, rgba(243, 242, 241, 0.96) 100%),
    var(--color-paper);
  border: 1px solid var(--color-line);
  box-shadow: 0 10px 28px rgba(39, 37, 42, 0.05);
}

.flo-slots__eyebrow {
  margin: 0 0 0.2rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.flo-slots__head h3 {
  margin: 0 0 0.2rem;
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 400;
  color: var(--color-ink);
}

.flo-slots__date {
  margin: 0;
  font: 500 0.82rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__hint {
  margin: 0.35rem 0 0;
  font: 500 0.75rem var(--font-body);
  color: var(--color-rose-dark, var(--color-rose));
}

.flo-slots__loading,
.flo-slots__empty {
  margin: 0.85rem 0 0;
  font: 500 0.88rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__pending {
  margin-top: 0.85rem;
}

.flo-slots__pending .flo-slots__loading {
  margin: 0 0 0.55rem;
}

.flo-slots__skeleton {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}

.flo-slots__skel-btn {
  min-height: 3.1rem;
  border-radius: 10px;
  border: 1px solid rgba(39, 37, 42, 0.06);
}

.flo-slots__skel-shimmer {
  background: linear-gradient(
    90deg,
    rgba(39, 37, 42, 0.05) 0%,
    rgba(39, 37, 42, 0.11) 45%,
    rgba(39, 37, 42, 0.05) 100%
  );
  background-size: 200% 100%;
  animation: flo-slots-shimmer 1.25s ease-in-out infinite;
}

@keyframes flo-slots-shimmer {
  0% {
    background-position: 100% 0;
  }
  100% {
    background-position: -100% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .flo-slots__skel-shimmer {
    animation: none;
    background: rgba(39, 37, 42, 0.07);
  }
}

.flo-slots__timeline {
  margin-top: 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.flo-slots__band {
  padding: 0.7rem 0.75rem 0.8rem;
  border-radius: 12px;
  background: var(--color-paper, #e5e1dc);
  border: 1px solid var(--color-line);
}

.flo-slots__band-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.flo-slots__hour {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 400;
  color: var(--color-ink);
  letter-spacing: 0.01em;
}

.flo-slots__count {
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.flo-slots__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}

.flo-slots__btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.12rem;
  min-height: 3.1rem;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--color-line);
  border-radius: 10px;
  background: var(--color-parchment, #ddd8d3);
  color: var(--color-ink);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.flo-slots__btn:hover {
  border-color: var(--color-rose);
}

.flo-slots__btn--active {
  border-color: var(--color-rose);
  background: var(--color-rose-soft);
}

.flo-slots__btn-start {
  font: 600 0.8rem/1.25 var(--font-body);
  letter-spacing: 0.01em;
}

.flo-slots__btn-end {
  font: 500 0.7rem var(--font-body);
  color: var(--color-muted);
}

.flo-slots__btn--active .flo-slots__btn-end {
  color: var(--color-rose-dark, var(--color-rose));
}

.flo-slots__more {
  margin-top: 0.7rem;
  padding: 0.4rem 0.15rem;
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
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  margin: 0.9rem 0 0;
  padding: 0.7rem 0.8rem;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-rose-soft, #f8ebe8), rgba(255, 255, 255, 0.7));
  border: 1px solid rgba(176, 122, 113, 0.22);
  text-align: left;
}

.flo-slots__confirm-label {
  font: 600 0.65rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.flo-slots__confirm-value {
  font: 600 0.92rem var(--font-body);
  color: var(--color-ink);
}

@media (min-width: 520px) {
  .flo-slots__grid,
  .flo-slots__skeleton {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
