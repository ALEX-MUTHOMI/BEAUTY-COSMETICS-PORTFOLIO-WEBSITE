import { computed, ref, watch, type Ref } from 'vue'
import type { ResolvedBookHandoff } from '@/landing/bookingHandoff'
import { BookingRequestGovernor, GENERIC_BOOKING_THROTTLE_ERROR } from './bookingRequestGovernor'
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
  const governor = new BookingRequestGovernor()
  const loading = ref(false)
  const slotsLoading = ref(false)
  const error = ref<string | null>(null)
  const selection = ref<ResolvedSelection | null>(null)
  const calendar = ref<BookingCalendar | null>(null)
  const selectedDate = ref<string | null>(null)
  const daySlots = ref<BookingSlot[]>([])
  const selectedSlot = ref<BookingSlot | null>(null)
  const calendarInteractionLocked = ref(false)

  const calendarDays = computed<CalendarDay[]>(() => calendar.value?.days ?? [])

  const selectedDay = computed(
    () => calendarDays.value.find((day) => day.date === selectedDate.value) ?? null,
  )

  const canContinue = computed(() => Boolean(selectedSlot.value && selectedDay.value))

  async function loadCalendar() {
    if (!handoff.value) return
    const loadToken = governor.beginCalendarLoad()
    if (loadToken < 0) {
      error.value = GENERIC_BOOKING_THROTTLE_ERROR
      return
    }

    loading.value = true
    calendarInteractionLocked.value = true
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
    if (governor.isCalendarLoadStale(loadToken)) return
    if ('error' in resolved) {
      error.value = resolved.error
      loading.value = false
      calendarInteractionLocked.value = false
      return
    }
    selection.value = resolved.data

    const calendarResult = await fetchCalendar(apiBaseUrl, resolved.data)
    if (governor.isCalendarLoadStale(loadToken)) return
    loading.value = false
    if ('error' in calendarResult) {
      error.value = calendarResult.error
      calendarInteractionLocked.value = false
      return
    }
    calendar.value = calendarResult.data
    calendarInteractionLocked.value = false

    const preferredDate = handoff.value.date
    if (preferredDate) {
      const preferredDay = calendarResult.data.days.find((day) => day.date === preferredDate)
      if (preferredDay && isDaySelectable(preferredDay)) {
        await selectDate(preferredDate)
      }
    }
  }

  async function selectDate(isoDate: string) {
    if (calendarInteractionLocked.value || slotsLoading.value) return
    if (selectedDate.value === isoDate && daySlots.value.length > 0) return

    const day = calendarDays.value.find((entry) => entry.date === isoDate)
    if (!day || !isDaySelectable(day) || !selection.value) return
    if (!governor.canFetchDaySlots()) {
      error.value = GENERIC_BOOKING_THROTTLE_ERROR
      return
    }

    const signal = governor.beginDaySlotFetch()
    selectedDate.value = isoDate
    selectedSlot.value = null
    slotsLoading.value = true
    calendarInteractionLocked.value = true
    daySlots.value = []
    error.value = null

    const slotsResult = await fetchDaySlots(apiBaseUrl, selection.value, isoDate, { signal })
    governor.clearDaySlotFetch()
    slotsLoading.value = false
    calendarInteractionLocked.value = false

    if (selectedDate.value !== isoDate) return
    if ('error' in slotsResult) {
      error.value = slotsResult.error
      return
    }
    daySlots.value = slotsResult.data
  }

  function selectSlot(slot: BookingSlot) {
    if (slotsLoading.value || loading.value) return
    // Bind full slot identity — startsAt alone lets bots swap resource/service IDs.
    if (
      !daySlots.value.some(
        (entry) =>
          entry.startsAt === slot.startsAt &&
          entry.resourcePublicId === slot.resourcePublicId &&
          entry.servicePublicId === slot.servicePublicId,
      )
    ) {
      return
    }
    selectedSlot.value = slot
  }

  watch(handoff, () => {
    if (handoff.value) void loadCalendar()
    else {
      governor.reset()
      selection.value = null
      calendar.value = null
      selectedDate.value = null
      selectedSlot.value = null
      daySlots.value = []
      error.value = null
      loading.value = false
      slotsLoading.value = false
      calendarInteractionLocked.value = false
    }
  }, { immediate: true })

  return {
    loading,
    slotsLoading,
    calendarInteractionLocked,
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
