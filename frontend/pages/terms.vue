<template>
  <main class="terms-page">
    <div class="terms-page__inner">
      <!-- Header -->
      <header class="terms-page__header">
        <p class="terms-page__script" aria-hidden="true">Shee</p>
        <span class="terms-page__eyebrow">Studio Policies</span>

        <div class="title-lockup">
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--left"
            width="36"
            height="36"
            aria-hidden="true"
          />
          <h1 class="terms-page__title">Terms of Service</h1>
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--right"
            width="36"
            height="36"
            aria-hidden="true"
          />
        </div>

        <p class="terms-page__lead">
          Clear, simple guidelines so every client enjoys a relaxing and timely appointment at our Meru studio.
        </p>
      </header>

      <!-- Policy Sections Stack (Gentle parchment, relaxed line-height) -->
      <div class="terms-sections">
        <article
          v-for="(section, index) in TERMS_SECTIONS"
          :key="section.id"
          class="terms-section"
        >
          <div class="terms-section__header">
            <span class="terms-section__num">0{{ index + 1 }}</span>
            <h2 class="terms-section__title">{{ section.title }}</h2>
          </div>

          <ul class="terms-section__list">
            <li v-for="(point, pIdx) in section.points" :key="pIdx" class="terms-section__item">
              <span class="terms-section__bullet" aria-hidden="true">&bull;</span>
              <span>{{ point }}</span>
            </li>
          </ul>
        </article>
      </div>

      <!-- Footer Help & Links -->
      <footer class="terms-page__footer">
        <p class="terms-page__support-text">
          Questions about booking, packages, or arrival times?
        </p>
        <div class="terms-page__actions">
          <NuxtLink to="/support" class="terms-btn terms-btn--outline">Contact Us</NuxtLink>
          <NuxtLink to="/book" class="terms-btn terms-btn--primary">Book Appointment</NuxtLink>
        </div>
        <div class="terms-page__sublinks">
          <NuxtLink to="/privacy" class="terms-page__link">Privacy Policy</NuxtLink>
          <span class="terms-page__sep" aria-hidden="true">&bull;</span>
          <NuxtLink to="/faq" class="terms-page__link">FAQ</NuxtLink>
          <span class="terms-page__sep" aria-hidden="true">&bull;</span>
          <NuxtLink to="/" class="terms-page__link">Home</NuxtLink>
        </div>
      </footer>
    </div>
  </main>
</template>

<script setup lang="ts">
/**
 * Terms of Service Page
 * Displays studio policies, guidelines, and booking conditions.
 */
import { TERMS_SECTIONS } from '~/src/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Terms of Service | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content: 'Appointment guidelines, package days, M-Pesa payments, and reschedule terms for Shee Aesthetics in Meru Town.',
    },
  ],
})
</script>

<style scoped>
.terms-page {
  min-height: 100vh;
  padding: clamp(2.5rem, 5vh, 4.5rem) 1.25rem 5rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
}

.terms-page__inner {
  max-width: 44rem;
  margin: 0 auto;
}

.terms-page__header {
  text-align: center;
  margin: 0 auto clamp(2rem, 4vh, 3rem);
}

.terms-page__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 5.5vw, 3rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.terms-page__eyebrow {
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

.terms-page__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.terms-page__lead {
  margin: 0 auto;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Sections */
.terms-sections {
  display: grid;
  gap: 1.15rem;
  margin-bottom: 3rem;
}

.terms-section {
  background:
    radial-gradient(ellipse 80% 60% at 0% 0%, rgba(176, 122, 113, 0.08), transparent 60%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  padding: clamp(1.35rem, 3.5vw, 1.75rem);
  box-shadow: 0 2px 8px rgba(23, 21, 22, 0.02);
}

.terms-section__header {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid rgba(176, 122, 113, 0.18);
  padding-bottom: 0.5rem;
}

.terms-section__num {
  font-family: var(--font-display);
  font-size: 1.15rem;
  color: var(--color-rose-dark, #965f57);
  opacity: 0.85;
  line-height: 1;
}

.terms-section__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.15rem;
  color: var(--color-ink, #252223);
}

.terms-section__list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.55rem;
}

.terms-section__item {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  font: 400 0.9rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.terms-section__bullet {
  color: var(--color-rose, #b07a71);
  font-size: 1rem;
  line-height: 1.4;
}

/* Footer */
.terms-page__footer {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.terms-page__support-text {
  font: 400 0.92rem/1.5 var(--font-body);
  color: var(--color-muted, #6b605c);
  margin-bottom: 1rem;
}

.terms-page__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1.5rem;
}

.terms-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  text-decoration: none;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: opacity 0.18s ease;
}

.terms-btn--primary {
  background: var(--color-rose, #b07a71);
  color: #ffffff;
}

.terms-btn--outline {
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
}

.terms-btn:hover {
  opacity: 0.9;
}

.terms-page__sublinks {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.terms-page__link {
  font: 600 0.74rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark, #965f57);
  transition: color 0.18s ease;
}

.terms-page__link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.terms-page__sep {
  color: var(--color-muted, #6b605c);
  opacity: 0.4;
}
</style>
