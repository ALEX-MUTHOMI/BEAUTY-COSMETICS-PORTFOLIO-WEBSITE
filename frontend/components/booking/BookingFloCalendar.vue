<template>
  <div class="flo-calendar" role="group" :aria-label="ariaLabel">
    <header class="flo-calendar__head">
      <p class="flo-calendar__range">
        {{ rangeLabel }}
      </p>
      <p class="flo-calendar__capacity">{{ capacityHint }}</p>
    </header>

    <div v-if="loading" class="flo-calendar__loading" aria-live="polite">
      <span class="flo-calendar__spinner" aria-hidden="true" />
      Loading open dates…
    </div>

    <div v-else class="flo-calendar__weekdays" aria-hidden="true">
      <span v-for="label in weekdayLabels" :key="label">{{ label }}</span>
    </div>

    <div v-if="!loading" class="flo-calendar__grid">
      <span
        v-for="(pad, index) in leadingPads"
        :key="`pad-${index}`"
        class="flo-calendar__pad"
        aria-hidden="true"
      />
      <button
        v-for="day in days"
        :key="day.date"
        type="button"
        class="flo-day"
        :class="dayClasses(day)"
        :disabled="!isDaySelectable(day)"
        :aria-pressed="selectedDate === day.date"
        :aria-label="ariaForDay(day)"
        @click="emit('select', day.date)"
      >
        <span class="flo-day__num">{{ dayNumber(day.date) }}</span>
        <span class="flo-day__meta">{{ dayStatusLabel(day) }}</span>
        <span v-if="day.status === 'available'" class="flo-day__remain">
          {{ day.capacity.remaining }} left
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  dayStatusLabel,
  isDaySelectable,
  type CalendarDay,
} from '@/booking/bookingPublicApi'

const props = defineProps<{
  days: CalendarDay[]
  selectedDate: string | null
  range?: { start: string; end: string } | null
  loading?: boolean
  capacityHint: string
  ariaLabel?: string
}>()

const emit = defineEmits<{ select: [isoDate: string] }>()

const weekdayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const leadingPads = computed(() => {
  const first = props.days[0]
  if (!first) return []
  return Array.from({ length: first.weekday }, (_, index) => index)
})

const rangeLabel = computed(() => {
  if (!props.range) return 'Upcoming dates'
  const start = formatShort(props.range.start)
  const end = formatShort(props.range.end)
  return `${start} – ${end}`
})

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

function dayNumber(isoDate: string): number {
  return Number(isoDate.split('-')[2]) || 0
}

function dayClasses(day: CalendarDay): Record<string, boolean> {
  return {
    'flo-day--selected': props.selectedDate === day.date,
    'flo-day--available': day.status === 'available',
    'flo-day--full': day.status === 'capacity_full' || day.status === 'no_slots',
    'flo-day--muted': day.status === 'not_offered' || day.status === 'closed',
  }
}

function ariaForDay(day: CalendarDay): string {
  const label = formatShort(day.date)
  if (day.status === 'available') {
    return `${label}, ${day.slot_count} slots, ${day.capacity.remaining} spots remaining`
  }
  return `${label}, ${dayStatusLabel(day)}`
}
</script>

<style scoped>
.flo-calendar__head {
  margin-bottom: 1rem;
}

.flo-calendar__range {
  margin: 0 0 0.25rem;
  font: 600 0.95rem var(--font-body);
  color: var(--color-ink);
}

.flo-calendar__capacity {
  margin: 0;
  font: 500 0.8rem/1.5 var(--font-body);
  color: var(--color-muted);
}

.flo-calendar__loading {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 1rem 0;
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
  to { transform: rotate(360deg); }
}

.flo-calendar__weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.35rem;
  margin-bottom: 0.35rem;
  text-align: center;
  font: 600 0.62rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.flo-calendar__grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.35rem;
}

.flo-calendar__pad {
  min-height: 4.75rem;
}

.flo-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.12rem;
  min-height: 4.75rem;
  padding: 0.35rem 0.2rem;
  border: 1px solid var(--color-line);
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  touch-action: manipulation;
  transition: border-color 0.15s ease, background-color 0.15s ease, transform 0.15s ease;
}

.flo-day:disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.flo-day--available:not(:disabled):hover {
  border-color: var(--color-rose);
  transform: translateY(-1px);
}

.flo-day--selected {
  border-color: var(--color-rose);
  background: var(--color-rose-soft);
  box-shadow: 0 0 0 2px rgba(222, 150, 141, 0.25);
}

.flo-day--full {
  background: #f8f8f9;
}

.flo-day--muted {
  background: #fafafa;
  color: var(--color-muted);
}

.flo-day__num {
  font: 700 1rem var(--font-body);
  color: var(--color-ink);
}

.flo-day__meta {
  font: 600 0.58rem var(--font-body);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.flo-day--full .flo-day__meta {
  color: #9b2c2c;
}

.flo-day--muted .flo-day__meta {
  color: var(--color-muted);
}

.flo-day__remain {
  font: 500 0.58rem var(--font-body);
  color: var(--color-muted);
}
</style>
