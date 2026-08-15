<template>
  <!-- Hero — Mellis-style fade gallery (Parisienne title + Manrope eyebrow + rose CTA) -->
  <section
    class="hero"
    data-home-hero
    role="region"
    aria-label="Shee studio gallery"
    :data-hero-service="currentHero.service"
    :style="{
      '--hero-crossfade-ms': `${HERO_CROSSFADE_MS}ms`,
      '--hero-copy-fade-ms': `${HERO_COPY_FADE_MS}ms`,
    }"
  >
    <div class="hero__track" aria-hidden="true">
      <article
        v-for="(slide, index) in heroSlides"
        :key="slide.service"
        class="hero__slide"
        :class="{ 'hero__slide--active': activeSlide === index }"
        :data-service="slide.service"
      >
        <picture v-if="mountedHeroSlides.has(index)">
          <img
            :src="slide.image"
            :srcset="slide.srcset"
            :sizes="slide.sizes"
            :alt="slide.alt"
            class="hero__bg"
            :style="{ objectPosition: slide.objectPosition }"
            :loading="index === 0 ? 'eager' : 'lazy'"
            :fetchpriority="index === 0 ? 'high' : 'auto'"
            decoding="async"
            :width="slide.width"
            :height="slide.height"
          />
        </picture>
      </article>
    </div>
    <div class="hero__overlay" aria-hidden="true" />
    <div class="hero__content" aria-live="polite">
      <!-- Single copy node — no Transition leave/enter stack (prevents ghosted titles) -->
      <div :key="currentHero.service" class="hero__copy">
        <p class="hero__eyebrow">{{ currentHero.eyebrow }}</p>
        <HeroHandwriteTitle :text="currentHero.headline" class="hero__title" />
        <SiteButton
          v-if="heroCtaIsExternal"
          :href="heroCta.to"
          variant="primary"
          class="hero__cta"
          @click="onHeroBook"
        >
          {{ heroCta.label }}
        </SiteButton>
        <SiteButton
          v-else
          :to="heroCta.to"
          variant="primary"
          class="hero__cta"
          @click="onHeroBook"
        >
          {{ heroCta.label }}
        </SiteButton>
      </div>
    </div>
    <div class="hero__controls" aria-label="Gallery controls">
      <button
        type="button"
        class="hero__nav hero__nav--prev"
        aria-label="Previous slide"
        @click="prevHeroSlide"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path
            fill="currentColor"
            d="M15.41 7.41 14 6l-6 6 6 6 1.41-1.41L10.83 12z"
          />
        </svg>
      </button>
      <div class="hero__dots" role="tablist" aria-label="Gallery slides">
        <button
          v-for="(slide, index) in heroSlides"
          :key="`dot-${slide.service}`"
          type="button"
          class="hero__dot"
          :class="{ 'hero__dot--active': activeSlide === index }"
          role="tab"
          :aria-selected="activeSlide === index"
          :aria-label="slide.headline"
          @click="goToHeroSlide(index)"
        />
      </div>
      <button
        type="button"
        class="hero__nav hero__nav--next"
        aria-label="Next slide"
        @click="nextHeroSlide"
      >
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
          <path
            fill="currentColor"
            d="M10 6 8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"
          />
        </svg>
      </button>
    </div>
    <!-- Soft wave seam into Get to know us (paper) -->
    <svg class="hero__wave" viewBox="0 0 1440 72" preserveAspectRatio="none" aria-hidden="true">
      <path
        fill="var(--color-paper)"
        d="M0,32 C240,72 480,0 720,28 C960,56 1200,8 1440,36 L1440,72 L0,72 Z"
      />
    </svg>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  HERO_COPY_FADE_MS,
  HERO_CROSSFADE_MS,
  HERO_FADE_MS,
  heroSlides,
  shouldMountHeroImage,
} from '@/landing/heroMedia'
import { useLandingContact } from '~/composables/useLandingContact'
import { heroCtaForSlide, primaryBookIsExternal } from '@/landing/primaryBookHref'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const contact = useLandingContact()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl

const activeSlide = ref(0)
/** Retain frames once mounted so crossfades never remount mid-fade. */
const retainedHeroSlides = ref(new Set<number>())
const mountedHeroSlides = computed(() => retainedHeroSlides.value)

watch(
  activeSlide,
  (active) => {
    const next = new Set(retainedHeroSlides.value)
    heroSlides.forEach((_, index) => {
      if (shouldMountHeroImage(active, index, heroSlides.length)) next.add(index)
    })
    retainedHeroSlides.value = next
  },
  { immediate: true },
)

const currentHero = computed(() => heroSlides[activeSlide.value] ?? heroSlides[0]!)
const heroCta = computed(() =>
  heroCtaForSlide(currentHero.value, new Date(), {
    contactIsLive: contactIsLive.value,
    whatsappUrl: whatsappUrl.value,
  }),
)
const heroCtaIsExternal = computed(() => primaryBookIsExternal(heroCta.value.to))

function onHeroBook() {
  trackFunnelEvent('cta_book_click', { surface: 'hero', href: heroCta.value.to })
}

let heroTimer: ReturnType<typeof setInterval> | null = null

function advanceHero() {
  if (typeof document !== 'undefined' && document.hidden) return
  activeSlide.value = (activeSlide.value + 1) % heroSlides.length
}

function goToHeroSlide(index: number) {
  activeSlide.value = index
  startHeroAutoplay()
}

function nextHeroSlide() {
  activeSlide.value = (activeSlide.value + 1) % heroSlides.length
  startHeroAutoplay()
}

function prevHeroSlide() {
  activeSlide.value = (activeSlide.value - 1 + heroSlides.length) % heroSlides.length
  startHeroAutoplay()
}

function startHeroAutoplay() {
  stopHeroAutoplay()
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return
  }
  heroTimer = setInterval(advanceHero, HERO_FADE_MS)
}

function stopHeroAutoplay() {
  if (heroTimer) {
    clearInterval(heroTimer)
    heroTimer = null
  }
}

function onHeroVisibility() {
  if (document.hidden) stopHeroAutoplay()
  else startHeroAutoplay()
}

onMounted(() => {
  startHeroAutoplay()
  document.addEventListener('visibilitychange', onHeroVisibility)
})

onUnmounted(() => {
  stopHeroAutoplay()
  document.removeEventListener('visibilitychange', onHeroVisibility)
})
</script>

<style scoped>
/* Hero — full photo + wave seam into paper (no ash fog) */
.hero {
  position: relative;
  width: 100%;
  /* Locked: mobile 92dvh — soft floor so short phones stay inside the viewport */
  height: 92svh;
  height: 92dvh;
  min-height: 28rem;
  overflow: hidden;
  background: var(--color-ink);
  --hero-crossfade-ms: 2800ms;
  --hero-copy-fade-ms: 1400ms;
}

@media (max-width: 767px) {
  .hero {
    height: calc(100svh - var(--home-hero-chrome, 0px));
    height: calc(100dvh - var(--home-hero-chrome, 0px));
    min-height: 22rem;
  }

  .hero__eyebrow {
    letter-spacing: 0.16em;
  }

  /* Sticky mobile book bar owns the primary Book CTA */
  .hero__cta {
    display: none !important;
  }
}

.hero__track {
  position: absolute;
  inset: 0;
}

.hero__slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  overflow: hidden;
  transition: opacity var(--hero-crossfade-ms) cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity;
  pointer-events: none;
}

.hero__slide--active {
  opacity: 1;
  z-index: 1;
}

.hero__slide picture {
  display: block;
  width: 100%;
  height: 100%;
}

.hero__bg {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  /* Subtle settle — avoid heavy blur from oversized Ken Burns */
  transform: scale(1.03);
  transition: transform var(--hero-crossfade-ms) cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

.hero__slide--active .hero__bg {
  transform: scale(1);
}

.hero__overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  /* Lighter veil — keep photos sharp; copy still readable */
  background:
    linear-gradient(
      180deg,
      rgba(20, 16, 18, 0.22) 0%,
      rgba(20, 16, 18, 0.12) 42%,
      rgba(20, 16, 18, 0.34) 100%
    );
}

.hero__wave {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  z-index: 5;
  width: 100%;
  height: clamp(2.5rem, 6vw, 4.5rem);
  display: block;
  pointer-events: none;
}

.hero__content {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: grid;
  place-items: center;
  text-align: center;
  /* Center in the band below the Home 3 header, not under the logo stack */
  padding:
    max(var(--site-header-height, 3.75rem), env(safe-area-inset-top, 0px))
    1.15rem
    calc(var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px) + 1.1rem);
  color: #fff;
  pointer-events: none;
}

.hero__copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(1rem, 2.6vh, 2.35rem);
  text-align: center;
  max-width: min(94vw, 56rem);
  margin: 0;
  transform: none;
  position: relative;
  animation: hero-copy-in 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.hero__content :deep(.site-btn) {
  pointer-events: auto;
}

@keyframes hero-copy-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero__eyebrow {
  margin: 0;
  font-family: var(--font-body);
  font-size: clamp(0.72rem, 1.15vw, 1.05rem);
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.95);
}

.hero__title {
  /* Handwriting title owns type scale; keep as flex child */
  margin: 0;
}

.hero__cta {
  display: inline-flex;
  min-height: 3.1rem;
  margin-top: 0.15rem;
  padding: 1rem 2.15rem !important;
  border-radius: 0 !important;
  font-size: 0.76rem !important;
  letter-spacing: 0.16em !important;
}

.hero__controls {
  position: absolute;
  left: 50%;
  bottom: calc(
    var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px) + 0.75rem
  );
  z-index: 4;
  display: flex;
  align-items: center;
  gap: 0.2rem;
  transform: translateX(-50%);
  padding: 0;
  background: transparent;
  border: 0;
}

.hero__nav {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.78);
  background: rgba(20, 16, 18, 0.28);
  cursor: pointer;
  box-shadow: none;
  transition: color 0.2s ease, background 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.hero__nav svg {
  width: 16px;
  height: 16px;
}

.hero__nav:hover,
.hero__nav:focus-visible {
  color: #fff;
  background: rgba(20, 16, 18, 0.48);
  outline: none;
}

.hero__nav:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.7);
  outline-offset: 2px;
}

.hero__nav:active {
  transform: scale(0.96);
}

.hero__dots {
  display: flex;
  align-items: center;
  gap: 0.05rem;
}

.hero__dot {
  position: relative;
  width: 1.65rem;
  height: 1.65rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.hero__dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0.32rem;
  height: 0.32rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.42);
  transform: translate(-50%, -50%);
  transition:
    background-color 0.25s ease,
    width 0.25s ease;
}

.hero__dot--active::after {
  background: #fff;
  width: 0.85rem;
}

.hero__dot:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 479px) {
  .hero__content {
    padding-inline: 1rem;
    gap: 0;
  }
}

/* Tablet and up — progressive enhancement */
@media (min-width: 768px) {
  .hero {
    /* Locked: tablet/iPad 92vh — Mellis-tall */
    height: 92vh;
    min-height: 38rem;
  }

  .hero__content {
    padding:
      max(var(--site-header-height, 8.5rem), env(safe-area-inset-top, 0px))
      1.5rem
      2.5rem;
  }

  .hero__copy {
    transform: none;
  }

  @keyframes hero-copy-in {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .hero__controls {
    bottom: 2.35rem;
  }

  .hero__nav {
    width: 2.15rem;
    height: 2.15rem;
  }

  .hero__eyebrow {
    font-size: clamp(0.9rem, 1.15vw, 1.1rem);
    letter-spacing: 0.3em;
  }
}

@media (min-width: 1024px) {
  .hero {
    /* Locked: desktop 100vh — Mellis full viewport */
    height: 100vh;
    min-height: 44rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__slide,
  .hero__bg,
  .hero__content,
  .hero__copy {
    animation: none !important;
    transition: none !important;
  }

  .hero__bg {
    transform: none !important;
  }
}
</style>
