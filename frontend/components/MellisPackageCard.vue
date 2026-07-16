<template>
  <article
    class="mellis-card"
    :class="{ 'mellis-card--featured': featured }"
  >
    <p v-if="badge" class="mellis-card__badge">{{ badge }}</p>
    <p v-if="daysLabel" class="mellis-card__days">{{ daysLabel }}</p>
    <h3 class="mellis-card__title">{{ name }}</h3>
    <p class="mellis-card__price">{{ price }}</p>
    <p class="mellis-card__text">{{ text }}</p>
    <ul class="mellis-card__includes" aria-label="What's included">
      <li v-for="item in includes" :key="item">{{ item }}</li>
    </ul>
    <SiteButton :to="ctaTo" :variant="featured ? 'primary' : 'outline'">
      {{ ctaLabel }}
    </SiteButton>
    <NuxtLink v-if="detailsTo" :to="detailsTo" class="mellis-card__details">
      {{ detailsLabel }}
    </NuxtLink>
  </article>
</template>

<script setup lang="ts">
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'

withDefaults(
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
  }>(),
  {
    daysLabel: 'Tue & Wed only',
    ctaLabel: LANDING_PRIMARY_CTA,
    ctaTo: '/services',
    detailsLabel: 'See all options',
  },
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
  box-shadow: 0 12px 28px rgba(222, 150, 141, 0.14);
  margin-top: 0.5rem;
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
  .mellis-card {
    padding: 1.35rem 1rem 1.15rem;
  }

  .mellis-card--featured {
    padding-top: 1.55rem;
  }

  .mellis-card__title {
    font-size: 1.15rem;
  }

  .mellis-card__price {
    font-size: 1.35rem;
  }

  .mellis-card__text {
    max-width: none;
    font-size: 0.86rem;
  }

  .mellis-card__includes li {
    font-size: 0.82rem;
    padding-left: 1.25rem;
  }

  .mellis-card :deep(.site-btn) {
    max-width: none;
    margin-top: auto;
  }
}

@media (min-width: 768px) {
  .mellis-card {
    padding: 1.6rem 1.4rem 1.45rem;
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
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-ink);
}

.mellis-card__price {
  margin: 0 0 0.65rem;
  font: 700 1.4rem var(--font-display);
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
