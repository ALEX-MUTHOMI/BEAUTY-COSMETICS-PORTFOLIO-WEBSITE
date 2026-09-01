<script setup lang="ts">
/**
 * Bare `/book` and legacy query handoffs.
 * - With allowlisted query → redirect to clean SEO path
 * - Otherwise → /services (generic booking entry)
 * When public booking is closed, stay on this page with HTTP 503.
 */
import BookingClosedNotice from '~/components/booking/BookingClosedNotice.vue'
import { isPublicBookingEnabled } from '~/src/booking/publicBookingGate'
import {
  canonicalBookPath,
  parseBookHandoffQuery,
  SERVICES_BOOK_ENTRY,
} from '@/landing/bookingHandoff'

definePageMeta({ layout: 'landing' })

const route = useRoute()
const bookingEnabled = isPublicBookingEnabled(useRuntimeConfig().public.bookingEnabled)
const handoff = parseBookHandoffQuery(route.query as Record<string, unknown>)
const target = handoff ? canonicalBookPath(handoff) : SERVICES_BOOK_ENTRY

if (bookingEnabled) {
  await navigateTo(target, { redirectCode: 302, replace: true })
} else if (import.meta.server) {
  setResponseStatus(503)
}
</script>

<template>
  <BookingClosedNotice v-if="!bookingEnabled" />
  <main v-else class="book-redirect">
    <p>Taking you to booking…</p>
  </main>
</template>

<style scoped>
.book-redirect {
  min-height: 40vh;
  display: grid;
  place-items: center;
  color: var(--color-muted);
  font: 0.95rem var(--font-body);
}
</style>
