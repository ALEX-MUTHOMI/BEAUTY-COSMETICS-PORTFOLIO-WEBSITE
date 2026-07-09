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

    <template v-else>
      <section
        v-for="week in weeks"
        :key="week.week_start"
        class="flo-week"
        :aria-label="weekLabel(week.week_start)"
      >
        <h3 class="flo-week__label">{{ weekLabel(week.week_start) }}</h3>
        <div class="flo-week__grid" :class="gridClass">
          <button
            v-for="day in week.days"
            :key="day.date"
            type="button"
            class="flo-day"
            :class="dayClasses(day)"
            :disabled="!isDaySelectable(day) || isDayInteractionBlocked(day)"
            :aria-pressed="selectedDate === day.date"
            :aria-label="ariaForDay(day)"
            @click="emit('select', day.date)"
          >
            <span class="flo-day__weekday">{{ weekdayShort(day.weekday) }}</span>
            <span class="flo-day__num">{{ dayNumber(day.date) }}</span>
            <span class="flo-day__meta">{{ dayStatusLabel(day) }}</span>
            <span v-if="day.status === 'available'" class="flo-day__remain">
              {{ day.capacity.remaining }} left
            </span>
          </button>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  dayStatusLabel,
  isDaySelectable,
  type CalendarDay,
  type CalendarWeek,
} from '@/booking/bookingPublicApi'

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

const weeks = computed<CalendarWeek[]>(() => {
  if (props.weeks?.length) return props.weeks
  if (!props.days.length) return []
  const buckets = new Map<string, CalendarDay[]>()
  const order: string[] = []
  for (const day of props.days) {
    const weekStart = weekStartFor(day.date)
    if (!buckets.has(weekStart)) {
      buckets.set(weekStart, [])
      order.push(weekStart)
    }
    buckets.get(weekStart)!.push(day)
  }
  return order.map((week_start) => ({ week_start, days: buckets.get(week_start)! }))
})

const gridClass = computed(() =>
  props.layout === 'package_pairs' ? 'flo-week__grid--pairs' : 'flo-week__grid--singles',
)

const rangeLabel = computed(() => {
  if (!props.range) return 'Upcoming dates'
  const start = formatShort(props.range.start)
  const end = formatShort(props.range.end)
  return `${start} – ${end}`
})

function weekStartFor(isoDate: string): string {
  const parts = isoDate.split('-').map(Number)
  const year = parts[0]
  const month = parts[1]
  const day = parts[2]
  if (!year || !month || !day) return isoDate
  const utc = new Date(Date.UTC(year, month - 1, day, 12, 0, 0))
  const weekday = utc.getUTCDay()
  const mondayOffset = weekday === 0 ? -6 : 1 - weekday
  utc.setUTCDate(utc.getUTCDate() + mondayOffset)
  return utc.toISOString().slice(0, 10)
}

function weekLabel(weekStart: string): string {
  return `Week of ${formatShort(weekStart)}`
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

function weekdayShort(weekday: number): string {
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][weekday] ?? ''
}

function dayNumber(isoDate: string): number {
  return Number(isoDate.split('-')[2]) || 0
}

function dayClasses(day: CalendarDay): Record<string, boolean> {
  return {
    'flo-day--selected': props.selectedDate === day.date,
    'flo-day--available': day.status === 'available',
    'flo-day--full': day.status === 'capacity_full' || day.status === 'no_slots',
    'flo-day--locked': isDayInteractionBlocked(day),
  }
}

function isDayInteractionBlocked(day: CalendarDay): boolean {
  if (!props.interactionLocked) return false
  return props.selectedDate !== day.date
}

function ariaForDay(day: CalendarDay): string {
  const label = `${weekdayShort(day.weekday)} ${formatShort(day.date)}`
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

.flo-week + .flo-week {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--color-line);
}

.flo-week__label {
  margin: 0 0 0.65rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.flo-week__grid {
  display: grid;
  gap: 0.5rem;
}

.flo-week__grid--pairs {
  grid-template-columns: repeat(2, 1fr);
}

.flo-week__grid--singles {
  grid-template-columns: repeat(auto-fill, minmax(5.5rem, 1fr));
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
  opacity: 0.85;
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

.flo-day__weekday {
  font: 600 0.58rem var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
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

.flo-day__remain {
  font: 500 0.58rem var(--font-body);
  color: var(--color-muted);
}
</style>
