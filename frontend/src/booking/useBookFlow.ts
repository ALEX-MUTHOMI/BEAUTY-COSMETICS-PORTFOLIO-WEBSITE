import { computed, ref, watch, type Ref } from 'vue'
import type { ResolvedBookHandoff } from '@/landing/bookingHandoff'
import {
  fetchCalendar,
  fetchDaySlots,
  isDaySelectable,
  resolveHandoff,
  type BookingCalendar,
  type BookingSlot,
  type CalendarDay,
  type ResolvedSelection,
} from './bookingPublicApi'

export function useBookFlow(handoff: Ref<ResolvedBookHandoff | null>, apiBaseUrl: string) {
  const loading = ref(false)
  const slotsLoading = ref(false)
  const error = ref<string | null>(null)
  const selection = ref<ResolvedSelection | null>(null)
  const calendar = ref<BookingCalendar | null>(null)
  const selectedDate = ref<string | null>(null)
  const daySlots = ref<BookingSlot[]>([])
  const selectedSlot = ref<BookingSlot | null>(null)

  const calendarDays = computed<CalendarDay[]>(() => calendar.value?.days ?? [])

  const selectedDay = computed(
    () => calendarDays.value.find((day) => day.date === selectedDate.value) ?? null,
  )

  const canContinue = computed(() => Boolean(selectedSlot.value && selectedDay.value))

  async function loadCalendar() {
    if (!handoff.value) return
    loading.value = true
    error.value = null
    selectedDate.value = null
    selectedSlot.value = null
    daySlots.value = []

    const query: { type: string; plan?: string; category?: string; treatment?: string } = {
      type: handoff.value.type === 'package' ? 'package' : 'single',
    }
    if (handoff.value.plan) query.plan = handoff.value.plan
    if (handoff.value.category) query.category = handoff.value.category
    if (handoff.value.treatment) query.treatment = handoff.value.treatment

    const resolved = await resolveHandoff(apiBaseUrl, query)
    if ('error' in resolved) {
      error.value = resolved.error
      loading.value = false
      return
    }
    selection.value = resolved.data

    const calendarResult = await fetchCalendar(apiBaseUrl, resolved.data)
    loading.value = false
    if ('error' in calendarResult) {
      error.value = calendarResult.error
      return
    }
    calendar.value = calendarResult.data
  }

  async function selectDate(isoDate: string) {
    const day = calendarDays.value.find((entry) => entry.date === isoDate)
    if (!day || !isDaySelectable(day) || !selection.value) return

    selectedDate.value = isoDate
    selectedSlot.value = null
    slotsLoading.value = true
    daySlots.value = []

    const slotsResult = await fetchDaySlots(apiBaseUrl, selection.value, isoDate)
    slotsLoading.value = false
    if ('error' in slotsResult) {
      error.value = slotsResult.error
      return
    }
    daySlots.value = slotsResult.data
  }

  function selectSlot(slot: BookingSlot) {
    if (!daySlots.value.some((entry) => entry.startsAt === slot.startsAt)) return
    selectedSlot.value = slot
  }

  watch(handoff, () => {
    if (handoff.value) void loadCalendar()
    else {
      selection.value = null
      calendar.value = null
      error.value = null
    }
  }, { immediate: true })

  return {
    loading,
    slotsLoading,
    error,
    selection,
    calendar,
    calendarDays,
    selectedDate,
    selectedDay,
    daySlots,
    selectedSlot,
    canContinue,
    selectDate,
    selectSlot,
  }
}
