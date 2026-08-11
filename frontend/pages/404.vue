<template>
  <main class="not-found">
    <img
      :src="flowerSrc"
      alt=""
      class="not-found__bloom not-found__bloom--tl"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="120"
      height="120"
      decoding="async"
    />
    <img
      :src="flowerSrc"
      alt=""
      class="not-found__bloom not-found__bloom--br"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="140"
      height="140"
      decoding="async"
    />
    <div class="not-found__inner">
      <div class="title-lockup">
        <img
          :src="flowerSrc"
          alt=""
          class="title-lockup__flower title-lockup__flower--left"
          width="36"
          height="36"
          aria-hidden="true"
        />
        <h1 class="not-found__title">Page not found</h1>
        <img
          :src="flowerSrc"
          alt=""
          class="title-lockup__flower title-lockup__flower--right"
          width="36"
          height="36"
          aria-hidden="true"
        />
      </div>
      <div class="not-found__actions">
        <SiteButton to="/" variant="outline">Home</SiteButton>
        <SiteButton to="/services" variant="outline">Services</SiteButton>
        <SiteButton to="/book" variant="primary">Book now</SiteButton>
      </div>
      <NuxtLink to="/faq" class="not-found__faq">{{ NOT_FOUND_PAGE.faqLink }}</NuxtLink>
    </div>
  </main>
</template>

<script setup lang="ts">
import { MELLIS_FLOWER_SRC, NOT_FOUND_PAGE } from '@/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

useHead({ title: 'Page not found | Shee Aesthetics' })

const flowerSrc = MELLIS_FLOWER_SRC
</script>

<style scoped>
.not-found {
  position: relative;
  isolation: isolate;
  min-height: min(72vh, 40rem);
  display: grid;
  place-items: center;
  padding: clamp(3rem, 10vh, 6rem) 1.25rem;
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(176, 122, 113, 0.1), transparent 60%),
    linear-gradient(180deg, var(--color-paper) 0%, var(--color-parchment) 100%);
  overflow: hidden;
}

.not-found__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.22;
  filter: saturate(1.3) brightness(1.02);
}

.not-found__bloom--tl {
  top: 1rem;
  left: max(0.5rem, env(safe-area-inset-left));
  width: min(120px, 24vw);
  transform: rotate(-22deg);
}

.not-found__bloom--br {
  right: max(0.5rem, env(safe-area-inset-right));
  bottom: 1.5rem;
  width: min(140px, 28vw);
  transform: rotate(150deg);
}

.not-found__inner {
  position: relative;
  z-index: 1;
  width: min(32rem, 100%);
  text-align: center;
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1.5rem;
}

.title-lockup__flower {
  width: 2rem;
  height: auto;
  flex-shrink: 0;
  opacity: 0.8;
  pointer-events: none;
  user-select: none;
}

.title-lockup__flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.title-lockup__flower--right {
  transform: rotate(8deg);
}

.not-found__script {
  margin: 0 0 0.35rem;
  font-family: var(--font-script);
  font-size: clamp(2.4rem, 8vw, 3.4rem);
  line-height: 1;
  color: var(--color-rose);
  opacity: 0.85;
}

.not-found__eyebrow {
  margin: 0 0 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-muted);
}

.not-found__title {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 5vw, 2.75rem);
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.not-found__lead {
  margin: 0 auto 2rem;
  max-width: 36ch;
  font: 400 1rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.not-found__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
}

.not-found__faq {
  display: inline-block;
  margin-top: 1.75rem;
  font: 600 0.78rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose);
}

.not-found__faq:hover {
  color: var(--color-rose-dark);
}
</style>
