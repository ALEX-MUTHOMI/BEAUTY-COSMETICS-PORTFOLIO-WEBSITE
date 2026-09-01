<template>
  <main class="not-found">
    <!-- Watermark blooms -->
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
      <!-- Brand Script -->
      <p class="not-found__script" aria-hidden="true">{{ NOT_FOUND_PAGE.script }}</p>

      <!-- Eyebrow Tag -->
      <div class="not-found__eyebrow-wrapper">
        <span class="not-found__eyebrow">{{ NOT_FOUND_PAGE.eyebrow }}</span>
      </div>

      <!-- Centered Title Lockup -->
      <div class="title-lockup">
        <img
          :src="flowerSrc"
          alt=""
          class="title-lockup__flower title-lockup__flower--left"
          width="36"
          height="36"
          aria-hidden="true"
        />
        <h1 class="not-found__title">{{ NOT_FOUND_PAGE.title }}</h1>
        <img
          :src="flowerSrc"
          alt=""
          class="title-lockup__flower title-lockup__flower--right"
          width="36"
          height="36"
          aria-hidden="true"
        />
      </div>

      <!-- Lead copy -->
      <p class="not-found__lead">{{ NOT_FOUND_PAGE.lead }}</p>

      <!-- Primary Action Buttons -->
      <div class="not-found__actions">
        <SiteButton to="/" variant="outline">Home</SiteButton>
        <SiteButton to="/services" variant="outline">Services</SiteButton>
        <SiteButton to="/book" variant="primary">Book now</SiteButton>
      </div>

      <!-- Help links -->
      <div class="not-found__footer-links">
        <NuxtLink to="/faq" class="not-found__link">{{ NOT_FOUND_PAGE.faqLink }}</NuxtLink>
        <span class="not-found__sep" aria-hidden="true">•</span>
        <NuxtLink to="/support" class="not-found__link">Customer Support</NuxtLink>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { MELLIS_FLOWER_SRC, NOT_FOUND_PAGE } from '~/src/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

setResponseStatus(404)

useHead({
  title: 'Page not found | Shee Aesthetics',
  meta: [
    {
      name: 'description',
      content:
        'The requested page could not be found. Navigate back to Shee Aesthetics beauty services and booking.',
    },
    { name: 'robots', content: 'noindex, follow' },
  ],
})

const flowerSrc = MELLIS_FLOWER_SRC
</script>

<style scoped>
.not-found {
  position: relative;
  isolation: isolate;
  min-height: min(76vh, 44rem);
  display: grid;
  place-items: center;
  padding: clamp(3.5rem, 10vh, 6.5rem) 1.25rem;
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(176, 122, 113, 0.12), transparent 60%),
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
  width: min(34rem, 100%);
  text-align: center;
  background: rgba(252, 248, 245, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(176, 122, 113, 0.22);
  border-radius: 1.25rem;
  padding: clamp(2rem, 5vw, 3.25rem) clamp(1.25rem, 4vw, 2.25rem);
  box-shadow:
    0 12px 36px rgba(44, 44, 48, 0.04),
    0 2px 8px rgba(176, 122, 113, 0.06);
}

.not-found__script {
  margin: 0 0 0.25rem;
  font-family: var(--font-script);
  font-size: clamp(2.4rem, 8vw, 3.4rem);
  line-height: 1;
  color: var(--color-rose);
  opacity: 0.9;
}

.not-found__eyebrow-wrapper {
  margin-bottom: 0.85rem;
}

.not-found__eyebrow {
  display: inline-block;
  padding: 0.3rem 0.85rem;
  border-radius: 999px;
  background: rgba(176, 122, 113, 0.12);
  text-transform: uppercase;
  letter-spacing: 0.24em;
  font: 700 0.68rem/1 var(--font-body);
  color: var(--color-rose-dark);
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1rem;
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

.not-found__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 5vw, 2.75rem);
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.not-found__lead {
  margin: 0 auto 2rem;
  max-width: 38ch;
  font: 400 1rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.not-found__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}

.not-found__footer-links {
  margin-top: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
}

.not-found__link {
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose);
  transition: color 0.2s ease;
}

.not-found__link:hover {
  color: var(--color-rose-dark);
  text-decoration: underline;
}

.not-found__sep {
  color: var(--color-muted);
  opacity: 0.4;
}
</style>
