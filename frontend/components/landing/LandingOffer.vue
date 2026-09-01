<template>
  <!-- Treatments — dark chapter with soft massage photo atmosphere -->
  <section id="services" class="offer home-section">
    <div class="offer__bg" aria-hidden="true">
      <img
        src="/images/hero-massage.jpg"
        alt=""
        class="offer__photo"
        width="1600"
        height="1067"
        loading="lazy"
        decoding="async"
        fetchpriority="low"
      />
      <div class="offer__veil" />
    </div>
    <div class="offer__chapter">
      <div class="offer__inner">
        <header class="offer__head">
          <div class="title-lockup title-lockup--on-dark">
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--left"
              width="72"
              height="72"
              aria-hidden="true"
              loading="lazy"
              decoding="async"
            />
            <h2 id="offer-heading">What we offer</h2>
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--right"
              width="72"
              height="72"
              aria-hidden="true"
              loading="lazy"
              decoding="async"
            />
          </div>
        </header>

        <ul class="offer__board" aria-label="Core treatments">
          <li v-for="(item, index) in offerShowcase" :key="item.label">
            <ScrollReveal variant="up" :delay="60 + index * 70">
              <NuxtLink :to="item.to" class="offer__cell">
                <span class="offer__index" aria-hidden="true">{{ item.index }}</span>
                <span class="offer__name">{{ item.label }}</span>
                <span class="offer__detail">{{ item.perk }}</span>
                <span class="offer__go" aria-hidden="true">Explore →</span>
              </NuxtLink>
            </ScrollReveal>
          </li>
        </ul>

        <ScrollReveal variant="up" :delay="220">
          <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="offer__cta">
            <span class="offer__cta-copy">
              <span class="offer__cta-label">Tue &amp; Wed only</span>
              <span class="offer__cta-title">One booking. Full glow.</span>
              <span class="offer__cta-meta">Facial, wax, massage &amp; makeup · from {{ LANDING_PACKAGE_FLOOR_SHORT }}</span>
            </span>
            <span class="offer__cta-action">
              View packages
              <span class="offer__cta-arrow" aria-hidden="true">→</span>
            </span>
          </NuxtLink>
        </ScrollReveal>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { LANDING_PACKAGE_FLOOR_SHORT } from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const offerShowcase = [
  { index: '01', label: 'Facials', perk: 'Deep cleansing facials', to: `${SERVICES_ROUTES.page}#facials` },
  { index: '02', label: 'Massage', perk: 'Hot stone massage', to: `${SERVICES_ROUTES.page}#massage` },
  { index: '03', label: 'Waxing', perk: 'Brow shaping', to: `${SERVICES_ROUTES.page}#waxing` },
  { index: '04', label: 'Makeup', perk: 'Bridal & event glam', to: `${SERVICES_ROUTES.page}#makeup` },
]
</script>

<style scoped>
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.65rem, 2.2vw, 1.15rem);
  max-width: 100%;
}

.title-lockup h2 {
  margin: 0;
  flex: 0 1 auto;
  min-width: 0;
}

.title-lockup__flower {
  width: clamp(2.85rem, 6.5vw, 3.85rem);
  height: auto;
  flex-shrink: 0;
  opacity: 0.78;
  pointer-events: none;
  user-select: none;
}

.title-lockup__flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.title-lockup__flower--right {
  transform: rotate(8deg);
}

.title-lockup--on-dark .title-lockup__flower {
  opacity: 1;
  filter: brightness(1.22) saturate(1.35) drop-shadow(0 0 10px rgba(240, 184, 172, 0.35));
}

@media (max-width: 479px) {
  .title-lockup__flower {
    width: clamp(1.55rem, 7.5vw, 2rem);
    opacity: 0.68;
  }

  .title-lockup {
    gap: 0.4rem;
  }

  .title-lockup h2 {
    font-size: clamp(1.55rem, 7.2vw, 1.95rem);
  }
}

/* Treatments — Mellis static-bg scroll chapter + colored Shee board */
.offer.home-section {
  content-visibility: visible;
  contain-intrinsic-size: none;
}

.offer {
  position: relative;
  padding: 0;
  overflow: hidden;
  background: var(--color-card-dark);
  border-block: var(--home-seam);
}

.offer__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.offer__photo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 70% 40%;
  transform: scale(1.04);
  /* Keep enough tone so the massage scene holds attention under the veil */
  filter: grayscale(0.18) contrast(1.08) brightness(0.88) saturate(0.92);
}

.offer__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(28, 18, 22, 0.58) 0%,
      rgba(22, 16, 18, 0.42) 38%,
      rgba(18, 14, 15, 0.62) 100%
    ),
    linear-gradient(
      90deg,
      rgba(28, 18, 22, 0.32) 0%,
      rgba(18, 14, 15, 0.12) 48%,
      rgba(28, 18, 22, 0.28) 100%
    );
}

.offer__chapter {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  padding: clamp(3.5rem, 8vh, 6rem) 1.25rem;
}

.offer__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.85rem, 4.5vh, 3rem);
}

.offer__head {
  display: flex;
  justify-content: center;
  text-align: center;
}

.offer__head .title-lockup {
  padding: 0.35rem 0 0.5rem;
  gap: clamp(0.85rem, 2.4vw, 1.6rem);
}

.offer__head .title-lockup h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2.65rem, 7.5vw, 4.15rem);
  font-weight: 500;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: #fff;
  text-shadow: none;
}

.offer__head .title-lockup__flower {
  width: clamp(2.9rem, 7vw, 4.25rem);
  opacity: 1;
}

.offer__board {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.95rem;
}

.offer__board > li {
  min-width: 0;
  height: 100%;
}

.offer__board > li :deep(.reveal),
.offer__board > li :deep(.reveal > *) {
  height: 100%;
}

.offer__cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  height: 100%;
  min-height: 9.5rem;
  padding: 1.35rem 1.15rem 1.2rem;
  color: #fff;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(245, 216, 208, 0.18);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  cursor: pointer;
  transition:
    background 0.25s ease,
    border-color 0.25s ease,
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease;
}

.offer__cell:hover,
.offer__cell:focus-visible {
  background: rgba(176, 122, 113, 0.28);
  border-color: rgba(245, 216, 208, 0.45);
  transform: translateY(-4px);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  outline: none;
}

.offer__cell:hover .offer__name,
.offer__cell:focus-visible .offer__name {
  color: #f5d8d0;
}

.offer__cell:hover .offer__go,
.offer__cell:focus-visible .offer__go {
  opacity: 1;
  transform: translateX(0);
}

.offer__index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.7rem;
  height: 1.7rem;
  padding: 0 0.35rem;
  margin-bottom: 0.15rem;
  border: 1px solid rgba(240, 184, 172, 0.55);
  border-radius: 999px;
  background: rgba(222, 150, 141, 0.18);
  font: 600 0.62rem/1 var(--font-body);
  letter-spacing: 0.12em;
  color: #f5d8d0;
}

.offer__name {
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 4.6vw, 1.95rem);
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  text-shadow: none;
  transition: color 0.2s ease;
}

.offer__detail {
  margin: 0;
  font: 400 0.82rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.88);
  text-shadow: none;
}

.offer__go {
  margin-top: auto;
  padding-top: 0.65rem;
  font: 600 0.68rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #f0b8ac;
  opacity: 0.72;
  transform: translateX(-0.15rem);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.offer__cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem 1.5rem;
  width: 100%;
  margin-top: 0.25rem;
  padding: 1.45rem 1.5rem;
  background:
    linear-gradient(135deg, rgba(176, 122, 113, 0.92) 0%, rgba(140, 88, 82, 0.95) 100%);
  border: 1px solid rgba(245, 216, 208, 0.35);
  color: #fff;
  text-decoration: none;
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  transition:
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease,
    filter 0.25s ease;
}

.offer__cta:hover,
.offer__cta:focus-visible {
  transform: translateY(-3px);
  filter: brightness(1.05);
  outline: none;
}

.offer__cta-copy {
  display: grid;
  gap: 0.28rem;
  min-width: 0;
  text-align: left;
}

.offer__cta-label {
  font: 600 0.68rem/1.2 var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 245, 240, 0.88);
}

.offer__cta-title {
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.5vw, 1.95rem);
  font-weight: 400;
  line-height: 1.15;
  color: #fff;
}

.offer__cta-meta {
  font: 400 0.86rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.9);
}

.offer__cta-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  padding: 0.85rem 1.15rem;
  background: var(--color-surface-raised);
  color: var(--color-ink);
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  box-shadow: none;
  transition: transform 0.2s ease, background 0.2s ease;
}

.offer__cta:hover .offer__cta-action,
.offer__cta:focus-visible .offer__cta-action {
  background: var(--color-paper);
}

.offer__cta-arrow {
  font-size: 1rem;
  line-height: 1;
  letter-spacing: 0;
  transition: transform 0.2s ease;
}

.offer__cta:hover .offer__cta-arrow,
.offer__cta:focus-visible .offer__cta-arrow {
  transform: translateX(0.2rem);
}

@media (max-width: 767px) {
  .offer__chapter {
    padding: clamp(3.25rem, 8vh, 5rem) 1.15rem;
  }

  .offer__inner {
    gap: 1.75rem;
  }

  .offer__head {
    margin-bottom: 0.35rem;
  }

  .offer__cta {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 1.1rem;
    padding: 1.35rem 1.2rem 1.25rem;
  }

  .offer__cta-action {
    justify-content: center;
    width: 100%;
  }

  .offer__board {
    gap: 0.85rem;
  }

  .offer__cell {
    min-height: 9.25rem;
    padding: 1.2rem 1rem 1.1rem;
  }

  .offer__go {
    opacity: 0.85;
    transform: none;
  }
}

/* Narrow phones — stack offer board for readable copy */
@media (max-width: 419px) {
  .offer__board {
    grid-template-columns: 1fr;
    gap: 0.7rem;
  }

  .offer__cell {
    min-height: 7.5rem;
    padding: 1.15rem 1.05rem 1.05rem;
  }
}

@media (min-width: 768px) {
  .offer__chapter {
    padding: clamp(4rem, 9vh, 6.5rem) 1.5rem;
  }

  .offer__inner {
    gap: clamp(2.15rem, 5vh, 3.25rem);
  }

  .offer__board {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.15rem;
  }

  .offer__cell {
    min-height: 12.5rem;
    padding: clamp(1.45rem, 2.8vh, 1.9rem) clamp(1.1rem, 1.5vw, 1.4rem);
    gap: 0.45rem;
  }

  .offer__name {
    font-size: clamp(1.55rem, 2vw, 1.95rem);
  }

  .offer__detail {
    font-size: 0.88rem;
    max-width: 14ch;
  }
}

@media (min-width: 1024px) {
  .offer__head .title-lockup h2 {
    font-size: clamp(3.1rem, 3.8vw, 4.25rem);
  }

  .offer__cta {
    padding: 1.55rem 1.85rem;
  }

  .offer__name {
    font-size: clamp(1.7rem, 1.9vw, 2.1rem);
  }

  .offer__detail {
    font-size: 0.92rem;
  }

  .offer__cell {
    min-height: 13.25rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .offer__cell:hover,
  .offer__cell:focus-visible,
  .offer__cta:hover,
  .offer__cta:focus-visible {
    transform: none;
    filter: none;
  }
}
</style>
