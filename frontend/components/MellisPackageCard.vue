<template>
  <article
    class="mellis-card"
    :class="{
      'mellis-card--featured': featured,
      'mellis-card--single': variant === 'single',
      'mellis-card--no-price': hidePrice,
      'mellis-card--light': cardTheme === 'light',
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
    /** dark = obsidian/black card; light = warm spa paper white card */
    cardTheme?: 'dark' | 'light'
  }>(),
  {
    daysLabel: 'Tue & Wed only',
    ctaLabel: LANDING_PRIMARY_CTA,
    ctaTo: '/services',
    detailsLabel: 'See all options',
    hidePrice: false,
    variant: 'package',
    cardTheme: 'dark',
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
  padding: 1.15rem 1rem 1rem;
  background:
    radial-gradient(ellipse 80% 60% at 100% 0%, rgba(222, 150, 141, 0.18), transparent 58%),
    linear-gradient(165deg, #322a2b 0%, #262122 50%, #1e1a1b 100%);
  border: 1px solid rgba(222, 150, 141, 0.22);
  border-top: 3px solid var(--color-rose);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(23, 21, 22, 0.1);
  overflow: hidden;
  color: #f7f0eb;
  transition:
    transform 0.25s var(--ease-story),
    box-shadow 0.25s var(--ease-story);
}

.mellis-card::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.08;
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
  opacity: 0.2;
  filter: saturate(1.2) brightness(1.02);
}

.mellis-card__bloom--tr {
  top: -0.65rem;
  right: -0.55rem;
  width: min(5rem, 36%);
  transform: rotate(18deg);
}

.mellis-card__bloom--bl {
  left: -0.65rem;
  bottom: -0.45rem;
  width: min(4rem, 28%);
  transform: rotate(-28deg);
  opacity: 0.15;
}

.mellis-card > *:not(.mellis-card__bloom) {
  position: relative;
  z-index: 1;
}

.mellis-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 32px rgba(23, 21, 22, 0.16);
}

/* Featured card — luxury black flower obsidian design */
.mellis-card--featured {
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, rgba(222, 150, 141, 0.15), transparent 60%),
    linear-gradient(165deg, #241d1f 0%, #1a1516 50%, #120e0f 100%);
  border: 1px solid rgba(222, 150, 141, 0.35);
  border-top: 3px solid var(--color-rose);
  box-shadow:
    0 16px 36px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(222, 150, 141, 0.22);
  color: #fcf8f5;
  z-index: 2;
}

.mellis-card--featured::before {
  opacity: 0.18;
  filter: brightness(1.2) contrast(1.1);
  mix-blend-mode: soft-light;
}

.mellis-card--featured .mellis-card__bloom {
  opacity: 0.22;
}

.mellis-card--featured .mellis-card__days {
  color: #f0b8ac;
}

.mellis-card--featured .mellis-card__title {
  color: #fcf8f5;
}

.mellis-card--featured .mellis-card__price {
  color: #f0b8ac;
}

.mellis-card--featured .mellis-card__text {
  color: rgba(255, 248, 244, 0.82);
}

.mellis-card--featured .mellis-card__includes li {
  color: #fcf8f5;
}

.mellis-card--featured .mellis-card__details {
  color: #f0b8ac;
}

/* Warm Ivory Spa Porcelain Card Theme */
.mellis-card--light {
  background:
    radial-gradient(ellipse 80% 60% at 100% 0%, rgba(176, 122, 113, 0.14), transparent 58%),
    linear-gradient(165deg, #fcf8f5 0%, #f6efe9 50%, #ece4dc 100%);
  border: 1px solid rgba(176, 122, 113, 0.38);
  border-top: 3px solid var(--color-rose);
  box-shadow:
    0 8px 24px rgba(23, 21, 22, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.95) inset;
  color: #1e191b;
}

.mellis-card--light::before {
  opacity: 0.1;
  mix-blend-mode: multiply;
}

.mellis-card--light .mellis-card__days {
  color: #b56b62;
  font-weight: 700;
}

.mellis-card--light .mellis-card__title {
  font-family: var(--font-display);
  color: #1e191b;
}

.mellis-card--light .mellis-card__price {
  font-family: var(--font-display);
  color: #b56b62;
}

.mellis-card--light .mellis-card__text {
  color: #59504c;
}

.mellis-card--light .mellis-card__includes li {
  color: #1e191b;
}

.mellis-card--light .mellis-card__details {
  color: #b56b62;
}

.mellis-card--light :deep(.site-btn) {
  background: #1e191b;
  color: #fff;
  border-color: #1e191b;
}

.mellis-card--light :deep(.site-btn:hover) {
  background: #342d2e;
}

.mellis-card :deep(.site-btn) {
  width: 100%;
  max-width: 14rem;
  min-height: 2.35rem;
  padding-inline: 0.95rem;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  margin-top: auto;
  border-radius: 6px;
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
  min-height: 2rem;
  margin-top: 0.35rem;
  padding: 0.25rem 0.45rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.1em;
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

.mellis-card__badge {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  padding: 0.3rem 0.85rem;
  background: var(--color-rose);
  color: #fff;
  font: 700 0.62rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  white-space: nowrap;
  z-index: 2;
  border-radius: 999px;
  box-shadow: 0 4px 12px rgba(222, 150, 141, 0.35);
}

.mellis-card__days {
  margin: 0.15rem 0 0.25rem;
  font: 700 0.62rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #f0b8ac;
}

.mellis-card__title {
  margin: 0 0 0.2rem;
  font-family: var(--font-display);
  font-size: clamp(1.15rem, 2.2vw, 1.35rem);
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #f8f2ee;
}

.mellis-card__price {
  margin: 0 0 0.45rem;
  font-family: var(--font-display);
  font-size: clamp(1.2rem, 2.4vw, 1.4rem);
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #f0b8ac;
  line-height: 1.2;
}

.mellis-card__text {
  margin: 0 0 0.65rem;
  max-width: 32ch;
  font: 400 0.8rem/1.45 var(--font-body);
  color: rgba(255, 248, 244, 0.8);
}

.mellis-card__includes {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.25rem 0.65rem;
  list-style: none;
  margin: 0 0 0.85rem;
  padding: 0;
  width: 100%;
  text-align: left;
}

.mellis-card__includes li {
  position: relative;
  padding: 0.12rem 0 0.12rem 1.05rem;
  font: 500 0.76rem/1.3 var(--font-body);
  color: rgba(255, 252, 249, 0.92);
}

.mellis-card__includes li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0.12rem;
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--color-rose);
}

@media (min-width: 768px) {
  .mellis-card {
    padding: 1.35rem 1.2rem 1.15rem;
  }
}
</style>
