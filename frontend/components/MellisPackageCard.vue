<template>
  <article
    class="mellis-card"
    :class="{
      'mellis-card--featured': featured,
      'mellis-card--single': variant === 'single',
    }"
  >
    <p v-if="badge" class="mellis-card__badge">{{ badge }}</p>
    <p v-if="daysLabel && variant !== 'single'" class="mellis-card__days">{{ daysLabel }}</p>
    <h3 class="mellis-card__title">{{ name }}</h3>
    <p class="mellis-card__price">{{ price }}</p>
    <p v-if="variant !== 'single'" class="mellis-card__text">{{ text }}</p>
    <ul
      v-if="visibleIncludes.length"
      class="mellis-card__includes"
      aria-label="What's included"
    >
      <li v-for="item in visibleIncludes" :key="item">{{ item }}</li>
    </ul>
    <SiteButton :to="ctaTo" :variant="featured || variant === 'single' ? 'primary' : 'outline'">
      {{ ctaLabel }}
    </SiteButton>
    <NuxtLink v-if="detailsTo" :to="detailsTo" class="mellis-card__details">
      {{ detailsLabel }}
    </NuxtLink>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'

const props = withDefaults(
  defineProps<{
    name: string
    text: string
    price: string
    includes: string[]
    featured?: boolean
    badge?: string
    daysLabel?: string
    ctaLabel?: string
    ctaTo?: string
    detailsTo?: string
    detailsLabel?: string
    /** package = full visit card; single = lean treatment tile for carousel */
    variant?: 'package' | 'single'
  }>(),
  {
    daysLabel: 'Tue & Wed only',
    ctaLabel: LANDING_PRIMARY_CTA,
    ctaTo: '/services',
    detailsLabel: 'See all options',
    variant: 'package',
  },
)

const visibleIncludes = computed(() =>
  props.variant === 'single' ? props.includes.slice(0, 2) : props.includes,
)
</script>

<style scoped>
.mellis-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
  width: 100%;
  min-width: 0;
  padding: 1.35rem 1.1rem 1.25rem;
  background: #fff;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  overflow: visible;
  transition:
    transform 0.35s var(--ease-story),
    box-shadow 0.35s var(--ease-story),
    border-color 0.3s;
}

.mellis-card::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.03;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 6c-5 11-14 13-14 22a14 14 0 0 0 28 0c0-9-9-11-14-22z' fill='%23de968d'/%3E%3C/svg%3E");
  background-size: 72px;
}

.mellis-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 32px rgba(39, 37, 42, 0.1);
  border-top-color: var(--color-rose-dark);
}

.mellis-card--featured {
  background: var(--color-cream);
  border-top-width: 4px;
  box-shadow: 0 16px 40px rgba(176, 122, 113, 0.18);
  margin-top: 0.75rem;
  padding: 1.75rem 1.35rem 1.5rem;
}

.mellis-card--featured .mellis-card__title {
  font-size: clamp(1.35rem, 2.8vw, 1.55rem);
}

.mellis-card--featured .mellis-card__price {
  font-size: clamp(1.55rem, 3vw, 1.85rem);
  margin-bottom: 0.75rem;
}

.mellis-card--featured .mellis-card__text {
  max-width: 32ch;
  font-size: 0.92rem;
}

.mellis-card--featured :deep(.site-btn) {
  max-width: 16rem;
  min-height: 2.9rem;
}

/* Lean singles tile — title + price + 2 bullets + calm Select */
.mellis-card--single {
  align-items: flex-start;
  text-align: left;
  padding: 1rem 0.95rem 0.95rem;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  border-radius: 0;
  background: #fff;
  box-shadow: var(--shadow-card);
}

.mellis-card--single::after {
  display: none;
}

.mellis-card--single:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(39, 37, 42, 0.09);
}

.mellis-card--single .mellis-card__title {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 0.2rem;
}

.mellis-card--single .mellis-card__price {
  font-size: 1.05rem;
  margin-bottom: 0.55rem;
}

.mellis-card--single .mellis-card__includes {
  margin-bottom: 0.75rem;
}

.mellis-card--single .mellis-card__includes li {
  padding-top: 0.18rem;
  padding-bottom: 0.18rem;
  font-size: 0.78rem;
  border-bottom: 0;
}

.mellis-card--single :deep(.site-btn) {
  width: 100%;
  max-width: none;
  margin-top: auto;
  min-height: 2.5rem;
}

.mellis-card--single .mellis-card__details {
  width: 100%;
  justify-content: flex-start;
  margin-top: 0.25rem;
  min-height: 2rem;
}

.mellis-card :deep(.site-btn) {
  width: 100%;
  max-width: 14rem;
}

.mellis-card__details {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.5rem;
  margin-top: 0.55rem;
  padding: 0.25rem 0.4rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark);
  transition: color 0.15s ease;
}

.mellis-card__details:hover {
  color: var(--color-rose);
  text-decoration: underline;
}

.mellis-card__details:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

@media (max-width: 767px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.25rem 1rem 1.1rem;
  }

  .mellis-card--featured {
    padding-top: 1.5rem;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__title {
    font-size: 1.12rem;
    line-height: 1.25;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__price {
    font-size: 1.28rem;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__text {
    max-width: none;
    font-size: 0.84rem;
    line-height: 1.45;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__includes li {
    font-size: 0.8rem;
    padding-left: 1.2rem;
    padding-top: 0.28rem;
    padding-bottom: 0.28rem;
  }

  .mellis-card:not(.mellis-card--single) :deep(.site-btn) {
    max-width: none;
    width: 100%;
    margin-top: auto;
    min-height: 2.75rem;
  }

  .mellis-card__details {
    min-height: 2.25rem;
  }
}

@media (min-width: 480px) and (max-width: 767px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.3rem 1.05rem 1.15rem;
  }
}

@media (min-width: 768px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.5rem 1.3rem 1.35rem;
  }

  .mellis-card--single {
    padding: 1.25rem 1.2rem 1.15rem;
  }

  .mellis-card--single .mellis-card__title {
    font-size: 1.25rem;
  }

  .mellis-card:not(.mellis-card--single) :deep(.site-btn) {
    max-width: 14rem;
  }
}

@media (min-width: 1024px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.65rem 1.4rem 1.45rem;
  }
}

.mellis-card__badge {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  padding: 0.35rem 1rem;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  white-space: nowrap;
  z-index: 1;
}

.mellis-card__days {
  margin: 0 0 0.45rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.mellis-card__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: clamp(1.28rem, 2.4vw, 1.45rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.mellis-card__price {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.35rem, 2.6vw, 1.55rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-rose-dark);
  line-height: 1.2;
}

.mellis-card__text {
  margin: 0 0 0.85rem;
  max-width: 28ch;
  font: 400 0.88rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.mellis-card__includes {
  list-style: none;
  margin: 0 0 1.1rem;
  padding: 0;
  width: 100%;
  text-align: left;
}

.mellis-card__includes li {
  position: relative;
  padding: 0.3rem 0 0.3rem 1.35rem;
  font: 500 0.84rem var(--font-body);
  color: var(--color-ink);
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
}

.mellis-card__includes li:last-child {
  border-bottom: none;
}

.mellis-card__includes li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0.3rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-rose);
}
</style>
