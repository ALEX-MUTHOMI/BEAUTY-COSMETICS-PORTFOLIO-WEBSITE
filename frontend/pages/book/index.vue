<script setup lang="ts">
/**
 * Bare `/book` and legacy query handoffs.
 * - With allowlisted query → redirect to clean SEO path
 * - Otherwise → /services (generic booking entry)
 */
import {
  canonicalBookPath,
  parseBookHandoffQuery,
  SERVICES_BOOK_ENTRY,
} from '@/landing/bookingHandoff'

definePageMeta({ layout: 'landing' })

const route = useRoute()
const handoff = parseBookHandoffQuery(route.query as Record<string, unknown>)
const target = handoff ? canonicalBookPath(handoff) : SERVICES_BOOK_ENTRY

await navigateTo(target, { redirectCode: 302, replace: true })
</script>

<template>
  <main class="book-redirect">
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
