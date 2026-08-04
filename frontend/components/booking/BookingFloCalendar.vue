<template>
  <div
    class="flo-calendar"
    :class="{ 'flo-calendar--pairs': layout === 'package_pairs' }"
    role="group"
    :aria-label="ariaLabel"
  >
    <header v-if="loading || orderedDays.length > 0" class="flo-calendar__head">
      <p class="flo-calendar__range">Next open dates</p>
      <p v-if="capacityHint" class="flo-calendar__capacity">{{ capacityHint }}</p>
    </header>

    <div v-if="loading" class="flo-calendar__loading" aria-live="polite">
      <span class="flo-calendar__spinner" aria-hidden="true" />
      Loading open dates…
    </div>

    <template v-else-if="orderedDays.length > 0">
      <div class="flo-strip">
        <button
          v-for="day in visibleDays"
          :key="day.date"
          type="button"
          class="flo-chip"
          :class="dayClasses(day)"
          :disabled="!isDaySelectable(day) || isDayInteractionBlocked(day)"
          :aria-pressed="selectedDate === day.date"
          :aria-label="ariaForDay(day)"
          @click="emit('select', day.date)"
        >
          <span class="flo-chip__weekday">{{ weekdayShort(day.weekday) }}</span>
          <span class="flo-chip__num">{{ dayNumber(day.date) }}</span>
          <span class="flo-chip__meta">{{ chipStatusLabel(day) }}</span>
        </button>
      </div>

      <button
        v-if="hasMore"
        type="button"
        class="flo-calendar__more"
        :aria-expanded="expanded"
        @click="expanded = !expanded"
      >
        {{ expanded ? 'Show fewer dates' : 'Show more dates' }}
      </button>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  isDaySelectable,
  type CalendarDay,
  type CalendarWeek,
} from '@/booking/bookingPublicApi'
import {
  flattenCalendarDays,
  stripHasMore,
  visibleStripDays,
} from '@/booking/calendarStrip'

const props = defineProps<{
  days: CalendarDay[]
  weeks?: CalendarWeek[]
  layout?: 'singles' | 'package_pairs'
  selectedDate: string | null
  range?: { start: string; end: string } | null
  loading?: boolean
  interactionLocked?: boolean
  capacityHint: string
  ariaLabel?: string
}>()

const emit = defineEmits<{ select: [isoDate: string] }>()

const expanded = ref(false)

const orderedDays = computed(() => flattenCalendarDays(props.days, props.weeks))

const hasMore = computed(() => stripHasMore(orderedDays.value))

const visibleDays = computed(() => visibleStripDays(orderedDays.value, expanded.value))

watch(orderedDays, () => {
  expanded.value = false
})

function weekdayShort(weekday: number): string {
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][weekday] ?? ''
}

function dayNumber(isoDate: string): number {
  return Number(isoDate.split('-')[2]) || 0
}

function formatShort(isoDate: string): string {
  const parts = isoDate.split('-').map(Number)
  const year = parts[0]
  const month = parts[1]
  const day = parts[2]
  if (!year || !month || !day) return isoDate
  const utc = new Date(Date.UTC(year, month - 1, day, 12, 0, 0))
  return new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Africa/Nairobi',
    day: 'numeric',
    month: 'short',
  }).format(utc)
}

function chipStatusLabel(day: CalendarDay): string {
  if (day.status === 'available') return 'Open'
  if (day.status === 'capacity_full' || day.status === 'no_slots') return 'Full'
  if (day.status === 'closed') return 'Closed'
  return '—'
}

function dayClasses(day: CalendarDay): Record<string, boolean> {
  return {
    'flo-chip--selected': props.selectedDate === day.date,
    'flo-chip--available': day.status === 'available',
    'flo-chip--full': day.status === 'capacity_full' || day.status === 'no_slots',
    'flo-chip--locked': isDayInteractionBlocked(day),
  }
}

function isDayInteractionBlocked(day: CalendarDay): boolean {
  if (!props.interactionLocked) return false
  return props.selectedDate !== day.date
}

function ariaForDay(day: CalendarDay): string {
  const label = `${weekdayShort(day.weekday)} ${formatShort(day.date)}`
  return `${label}, ${chipStatusLabel(day)}`
}
</script>

<style scoped>
.flo-calendar__head {
  margin-bottom: 0.75rem;
}

.flo-calendar__range {
  margin: 0 0 0.2rem;
  font: 600 0.95rem var(--font-body);
  color: var(--color-ink);
}

.flo-calendar__capacity {
  margin: 0;
  font: 500 0.8rem/1.45 var(--font-body);
  color: var(--color-muted);
}

.flo-calendar__loading {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.85rem 0;
  color: var(--color-muted);
}

.flo-calendar__spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-line);
  border-top-color: var(--color-rose);
  border-radius: 50%;
  animation: flo-spin 0.7s linear infinite;
}

@keyframes flo-spin {
  to {
    transform: rotate(360deg);
  }
}

.flo-strip {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 0.15rem 0.1rem 0.45rem;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.flo-calendar--pairs .flo-chip {
  min-width: 4.75rem;
}

.flo-chip {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.05rem;
  min-width: 4.35rem;
  min-height: 3.1rem;
  padding: 0.4rem 0.45rem;
  border: 1px solid var(--color-line);
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  touch-action: manipulation;
  scroll-snap-align: start;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease,
    transform 0.15s ease;
}

.flo-chip:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}

.flo-chip--available:not(:disabled):hover {
  border-color: var(--color-rose);
  transform: translateY(-1px);
}

.flo-chip--selected {
  border-color: var(--color-rose);
  background: var(--color-rose-soft);
  box-shadow: 0 0 0 2px rgba(222, 150, 141, 0.25);
}

.flo-chip--full {
  background: #f8f8f9;
}

.flo-chip__weekday {
  font: 600 0.58rem var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.flo-chip__num {
  font: 700 1.05rem var(--font-body);
  line-height: 1.1;
  color: var(--color-ink);
}

.flo-chip__meta {
  font: 600 0.56rem var(--font-body);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.flo-chip--full .flo-chip__meta {
  color: #9b2c2c;
}

.flo-calendar__more {
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

.flo-calendar__more:hover {
  color: var(--color-rose);
}
</style>
