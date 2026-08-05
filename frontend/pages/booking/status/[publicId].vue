<template>
  <BookingStatusCard :booking-public-id="publicId" mode="status" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

import BookingStatusCard from '@/components/booking/BookingStatusCard.vue'

const route = useRoute()

definePageMeta({ layout: 'landing' })

useSeoMeta({
  title: 'Booking Status | Shee Aesthetics Meru',
  robots: 'noindex,nofollow',
})

const publicId = computed(() => String(route.params.publicId ?? ''))
</script>

<style scoped>
.book-status {
  min-height: 70vh;
  padding: 2rem 1rem;
  background: linear-gradient(180deg, #fff 0%, #fafafa 100%);
}

.book-status__card {
  width: var(--container);
  max-width: 36rem;
  margin: 0 auto;
  display: grid;
  gap: 1.25rem;
  padding: 1.75rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 1.25rem;
  background: #fff;
}

.book-status__eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b4a3a;
}

.book-status__card h1 {
  margin: 0;
  font-size: 1.75rem;
}

.book-status__lead,
.book-status__polling,
.book-status__error {
  margin: 0;
}

.book-status__error {
  color: #8b1e1e;
}

.book-status__meta {
  display: grid;
  gap: 0.75rem;
  margin: 0;
}

.book-status__meta div {
  display: grid;
  gap: 0.2rem;
}

.book-status__meta dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6b6b6b;
}

.book-status__meta dd {
  margin: 0;
  font-weight: 600;
}

.book-status__retry {
  display: grid;
  gap: 0.75rem;
}

.book-status__retry label {
  display: grid;
  gap: 0.4rem;
  font-weight: 600;
}

.book-status__retry input {
  min-height: 2.75rem;
  padding: 0 0.75rem;
  border: 1px solid rgba(0, 0, 0, 0.14);
  border-radius: 0.75rem;
}

.book-status__retry-btn {
  min-height: 2.75rem;
  padding: 0 1.25rem;
  border: 0;
  border-radius: 0.75rem;
  font-weight: 700;
  color: #fff;
  background: #241611;
  cursor: pointer;
}

.book-status__retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.book-status__remember {
  display: grid;
  gap: 0.75rem;
  padding: 0.85rem 0.9rem;
  border-radius: 0.85rem;
  background: #faf6f5;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.book-status__remember-label {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  font-size: 0.88rem;
  line-height: 1.45;
  color: #3a2a24;
}

.book-status__remember-btn {
  min-height: 2.5rem;
  padding: 0 1rem;
  border: 0;
  border-radius: 999px;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff;
  background: var(--color-rose, #de968d);
  cursor: pointer;
  justify-self: start;
}

.book-status__remember-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.book-status__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
