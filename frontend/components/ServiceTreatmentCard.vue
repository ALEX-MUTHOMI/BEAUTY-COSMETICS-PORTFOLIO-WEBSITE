<template>
  <article class="service-treatment">
    <div class="service-treatment__head">
      <h3 class="service-treatment__name">{{ name }}</h3>
      <p class="service-treatment__meta">
        <span>{{ duration }}</span>
        <span class="service-treatment__dot" aria-hidden="true">·</span>
        <span class="service-treatment__price">{{ price }}</span>
      </p>
    </div>
    <p class="service-treatment__text">{{ description }}</p>
    <ul class="service-treatment__list">
      <li v-for="item in highlights" :key="item">{{ item }}</li>
    </ul>
    <SiteButton to="/book" variant="text" class="service-treatment__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
  </article>
</template>

<script setup lang="ts">
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'

defineProps<{
  name: string
  description: string
  duration: string
  price: string
  highlights: string[]
}>()
</script>

<style scoped>
.service-treatment {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1.35rem 1.25rem 1.15rem;
  background: #fff;
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-rose);
}

.service-treatment__head {
  margin-bottom: 0.75rem;
}

.service-treatment__name {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-ink);
}

.service-treatment__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.service-treatment__dot {
  opacity: 0.6;
}

.service-treatment__text {
  margin: 0 0 1rem;
  font: 400 0.92rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.service-treatment__list {
  margin: 0 0 1rem;
  padding: 0;
  list-style: none;
  flex: 1;
}

.service-treatment__list li {
  position: relative;
  padding-left: 1rem;
  font: 400 0.85rem/1.55 var(--font-body);
  color: var(--color-ink);
}

.service-treatment__list li + li {
  margin-top: 0.35rem;
}

.service-treatment__list li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.55em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-rose);
}

.service-treatment__cta {
  align-self: flex-start;
}
</style>
