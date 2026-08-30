<template>
  <main class="not-found">
    <div class="not-found__inner">
      <!-- Brand Script -->
      <span class="not-found__brand">Shee Aesthetics</span>

      <!-- Eyebrow Tag -->
      <span class="not-found__eyebrow">{{ NOT_FOUND_PAGE.eyebrow }}</span>

      <!-- Centered Title -->
      <h1 class="not-found__title">{{ NOT_FOUND_PAGE.title }}</h1>

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
import { NOT_FOUND_PAGE } from '~/src/landing/clientPagesContent'

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

.not-found__brand {
  display: block;
  font-family: var(--font-script, 'Parisienne', cursive);
  font-size: clamp(2rem, 4.5vw, 3rem);
  color: var(--color-rose, #b07a71);
  line-height: 1.1;
  margin-bottom: 0.35rem;
}

.not-found__eyebrow {
  display: inline-block;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 700 0.72rem/1 var(--font-body);
  color: var(--color-muted, #786f6a);
}

.not-found__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2.2rem, 5vw, 3.2rem);
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
