<template>
  <article
    class="mellis-card"
    :class="{
      'mellis-card--featured': featured,
      'mellis-card--single': variant === 'single',
      'mellis-card--no-price': hidePrice,
    }"
  >
    <img
      src="/images/flower.png"
      alt=""
      class="mellis-card__bloom mellis-card__bloom--tr"
      width="96"
      height="96"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
    <img
      src="/images/flower.png"
      alt=""
      class="mellis-card__bloom mellis-card__bloom--bl"
      width="72"
      height="72"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
    <p v-if="badge" class="mellis-card__badge">{{ badge }}</p>
    <p v-if="daysLabel && variant !== 'single'" class="mellis-card__days">{{ daysLabel }}</p>
    <h3 class="mellis-card__title">{{ name }}</h3>
    <p v-if="!hidePrice" class="mellis-card__price">{{ price }}</p>
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
    /** Hide price — services catalog prefers info + CTA only */
    hidePrice?: boolean
    /** package = full visit card; single = lean treatment tile for carousel */
    variant?: 'package' | 'single'
  }>(),
  {
    daysLabel: 'Tue & Wed only',
    ctaLabel: LANDING_PRIMARY_CTA,
    ctaTo: '/services',
    detailsLabel: 'See all options',
    hidePrice: false,
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
  padding: 1.55rem 1.3rem 1.4rem;
  /* Calm warm charcoal — palette without choking text */
  background:
    radial-gradient(ellipse 80% 60% at 100% 0%, rgba(222, 150, 141, 0.18), transparent 58%),
    linear-gradient(165deg, #322a2b 0%, #262122 50%, #1e1a1b 100%);
  border: 1px solid rgba(222, 150, 141, 0.22);
  border-top: 3px solid var(--color-rose);
  box-shadow: 0 10px 28px rgba(23, 21, 22, 0.12);
  overflow: hidden;
  color: #f7f0eb;
  transition:
    transform 0.35s var(--ease-story),
    box-shadow 0.35s var(--ease-story);
}

.mellis-card::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.1;
  background-image: url('/images/flower.png');
  background-size: 5.5rem;
  background-repeat: repeat;
  filter: saturate(1.2) brightness(1.08);
  mix-blend-mode: soft-light;
}

.mellis-card__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.26;
  filter: saturate(1.2) brightness(1.02);
}

.mellis-card__bloom--tr {
  top: -0.85rem;
  right: -0.65rem;
  width: min(6.5rem, 42%);
  transform: rotate(18deg);
}

.mellis-card__bloom--bl {
  left: -0.85rem;
  bottom: -0.55rem;
  width: min(5rem, 34%);
  transform: rotate(-28deg);
  opacity: 0.2;
}

.mellis-card > *:not(.mellis-card__bloom) {
  position: relative;
  z-index: 1;
}

.mellis-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 44px rgba(23, 21, 22, 0.2);
}

/* Most booked — white stage, stands out in the middle */
.mellis-card--featured {
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(222, 150, 141, 0.18), transparent 65%),
    #fff;
  border: 1px solid rgba(222, 150, 141, 0.45);
  border-top: 4px solid var(--color-rose);
  box-shadow:
    0 18px 48px rgba(222, 150, 141, 0.22),
    0 8px 24px rgba(23, 21, 22, 0.08);
  margin-top: 0;
  padding: 1.95rem 1.5rem 1.6rem;
  color: var(--color-ink);
  z-index: 2;
}

.mellis-card--featured::before {
  opacity: 0.12;
  filter: saturate(1.3) brightness(1.05);
  mix-blend-mode: multiply;
}

.mellis-card--featured .mellis-card__bloom {
  opacity: 0.38;
  filter: saturate(1.15) brightness(1);
}

.mellis-card--featured .mellis-card__days {
  color: var(--color-rose-dark, #b56b62);
}

.mellis-card--featured .mellis-card__title {
  font-size: clamp(1.4rem, 3vw, 1.7rem);
  color: var(--color-ink);
}

.mellis-card--featured .mellis-card__price {
  font-size: clamp(1.55rem, 3vw, 1.85rem);
  margin-bottom: 0.75rem;
  color: var(--color-rose-dark, #b56b62);
}

.mellis-card--featured .mellis-card__text {
  max-width: 32ch;
  font-size: 0.95rem;
  color: var(--color-muted);
}

.mellis-card--featured .mellis-card__includes li {
  color: var(--color-ink);
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
}

.mellis-card--featured .mellis-card__includes li:last-child {
  border-bottom: none;
}

.mellis-card--featured .mellis-card__details {
  color: var(--color-rose-dark, #b56b62);
}

.mellis-card--featured :deep(.site-btn) {
  max-width: 16rem;
  min-height: 2.9rem;
}

.mellis-card--no-price .mellis-card__text {
  margin-top: 0.15rem;
}

/* Lean singles tile */
.mellis-card--single {
  align-items: flex-start;
  text-align: left;
  padding: 1rem 0.95rem 0.95rem;
  border-radius: 0;
}

.mellis-card--single .mellis-card__bloom {
  display: none;
}

.mellis-card--single:hover {
  transform: translateY(-2px);
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
  margin-top: auto;
}

.mellis-card :deep(.site-btn--outline) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(245, 216, 208, 0.5);
}

.mellis-card :deep(.site-btn--outline:hover),
.mellis-card :deep(.site-btn--outline:focus-visible) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(245, 216, 208, 0.85);
  color: #fff;
}

.mellis-card__details {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  margin-top: 0.55rem;
  padding: 0.45rem 0.55rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  color: #f0b8ac;
  transition: color 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.mellis-card__details:hover {
  color: #f5d8d0;
  text-decoration: underline;
}

.mellis-card__details:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

@media (max-width: 767px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.35rem 1.05rem 1.15rem;
  }

  .mellis-card--featured {
    padding-top: 1.65rem;
    transform: scale(1.01);
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__title {
    font-size: 1.18rem;
    line-height: 1.25;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__price {
    font-size: 1.28rem;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__text {
    max-width: none;
    font-size: 0.88rem;
    line-height: 1.5;
  }

  .mellis-card:not(.mellis-card--single) .mellis-card__includes li {
    font-size: 0.84rem;
    padding-left: 1.2rem;
    padding-top: 0.32rem;
    padding-bottom: 0.32rem;
  }

  .mellis-card:not(.mellis-card--single) :deep(.site-btn) {
    max-width: none;
    width: 100%;
    margin-top: auto;
    min-height: 2.85rem;
  }

  .mellis-card__details {
    min-height: 2.75rem;
    width: 100%;
  }
}

@media (min-width: 768px) {
  .mellis-card:not(.mellis-card--single) {
    padding: 1.5rem 1.3rem 1.35rem;
  }

  .mellis-card--featured {
    transform: scale(1.03);
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

  .mellis-card--featured {
    transform: scale(1.045);
  }
}

.mellis-card__badge {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  padding: 0.4rem 1.1rem;
  background: var(--color-rose);
  color: #fff;
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  white-space: nowrap;
  z-index: 2;
  box-shadow: 0 6px 16px rgba(222, 150, 141, 0.35);
}

.mellis-card__days {
  margin: 0.35rem 0 0.45rem;
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #f0b8ac;
}

.mellis-card__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: clamp(1.28rem, 2.4vw, 1.5rem);
  font-weight: 600;
  letter-spacing: -0.02em;
  color: #f8f2ee;
}

.mellis-card__price {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.35rem, 2.6vw, 1.55rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #f0b8ac;
  line-height: 1.2;
}

.mellis-card__text {
  margin: 0 0 0.85rem;
  max-width: 30ch;
  font: 500 0.9rem/1.55 var(--font-body);
  color: rgba(255, 248, 244, 0.82);
}

.mellis-card__includes {
  list-style: none;
  margin: 0 0 1.15rem;
  padding: 0;
  width: 100%;
  text-align: left;
}

.mellis-card__includes li {
  position: relative;
  padding: 0.35rem 0 0.35rem 1.35rem;
  font: 600 0.88rem/1.35 var(--font-body);
  color: rgba(255, 252, 249, 0.95);
}

.mellis-card__includes li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0.35rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-rose);
}
</style>
