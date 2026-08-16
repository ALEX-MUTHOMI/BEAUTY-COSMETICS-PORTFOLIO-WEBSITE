<template>
  <main class="not-found">
    <div class="not-found__inner">
      <!-- Brand Script -->
      <p class="not-found__script" aria-hidden="true">{{ NOT_FOUND_PAGE.script }}</p>

      <!-- Eyebrow Tag -->
      <span class="not-found__eyebrow">{{ NOT_FOUND_PAGE.eyebrow }}</span>

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

      <!-- Primary Action Buttons (Harmonious with Services Doors) -->
      <div class="not-found__actions">
        <NuxtLink to="/" class="not-found__btn not-found__btn--outline">
          Home
        </NuxtLink>
        <NuxtLink to="/services" class="not-found__btn not-found__btn--outline">
          Services
        </NuxtLink>
        <NuxtLink to="/book" class="not-found__btn not-found__btn--primary">
          Book appointment
        </NuxtLink>
      </div>

      <!-- Footer Sublinks -->
      <nav class="not-found__nav" aria-label="Helpful links">
        <NuxtLink to="/faq" class="not-found__link">FAQ</NuxtLink>
        <span class="not-found__dot" aria-hidden="true">&bull;</span>
        <NuxtLink to="/support" class="not-found__link">Contact</NuxtLink>
      </nav>
    </div>
  </main>
</template>

<script setup lang="ts">
import { MELLIS_FLOWER_SRC, NOT_FOUND_PAGE } from '~/src/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Page Not Found | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content: 'This page could not be found. Return to Shee Aesthetics home, services, or book an appointment in Meru.',
    },
    {
      name: 'robots',
      content: 'noindex, follow',
    },
  ],
})

const flowerSrc = MELLIS_FLOWER_SRC
</script>

<style scoped>
.not-found {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(3rem, 7vh, 5rem) 1.25rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
  text-align: center;
}

.not-found__inner {
  max-width: 36rem;
  margin: 0 auto;
}

.not-found__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.4rem, 6vw, 3.2rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.not-found__eyebrow {
  display: inline-block;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 700 0.7rem/1 var(--font-body);
  color: var(--color-rose-dark, #965f57);
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.title-lockup__flower {
  width: 1.85rem;
  height: auto;
  flex-shrink: 0;
  opacity: 0.65;
  pointer-events: none;
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
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.not-found__lead {
  margin: 0 auto 1.75rem;
  max-width: 32ch;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.not-found__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1.75rem;
}

.not-found__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.15rem;
  border-radius: 999px;
  text-decoration: none;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: opacity 0.18s ease;
}

.not-found__btn--primary {
  background: var(--color-rose, #b07a71);
  color: #ffffff;
}

.not-found__btn--outline {
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
}

.not-found__btn:hover {
  opacity: 0.9;
}

.not-found__nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.not-found__link {
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark, #965f57);
  transition: color 0.18s ease;
}

.not-found__link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.not-found__dot {
  color: var(--color-muted, #6b605c);
  opacity: 0.4;
}
</style>
