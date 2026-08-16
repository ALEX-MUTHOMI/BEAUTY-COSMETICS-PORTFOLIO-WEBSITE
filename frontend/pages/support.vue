<template>
  <main class="support-page">
    <div class="support-page__inner">
      <!-- Header -->
      <header class="support-page__header">
        <p class="support-page__script" aria-hidden="true">{{ CUSTOMER_SUPPORT_PAGE.script }}</p>
        <span class="support-page__eyebrow">{{ CUSTOMER_SUPPORT_PAGE.eyebrow }}</span>

        <div class="title-lockup">
          <img
            :src="flowerSrc"
            alt=""
            class="title-lockup__flower title-lockup__flower--left"
            width="36"
            height="36"
            aria-hidden="true"
          />
          <h1 class="support-page__title">{{ CUSTOMER_SUPPORT_PAGE.title }}</h1>
          <img
            :src="flowerSrc"
            alt=""
            class="title-lockup__flower title-lockup__flower--right"
            width="36"
            height="36"
            aria-hidden="true"
          />
        </div>

        <p class="support-page__lead">{{ CUSTOMER_SUPPORT_PAGE.lead }}</p>
      </header>

      <!-- Contact Doors Grid (Matching Services Door aesthetic) -->
      <section class="support-doors" aria-label="Direct contact channels">
        <!-- WhatsApp Door (Rich Obsidian Accent) -->
        <a
          :href="whatsappUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="support-door support-door--dark"
        >
          <img
            :src="flowerSrc"
            alt=""
            class="support-door__bloom"
            aria-hidden="true"
            width="80"
            height="80"
          />
          <div class="support-door__body">
            <span class="support-door__tag">Direct Chat</span>
            <h2 class="support-door__title">WhatsApp</h2>
            <p class="support-door__desc">Chat with Shee for quick questions, special slots, or rescheduling.</p>
            <span class="support-door__cta">Open WhatsApp &rarr;</span>
          </div>
        </a>

        <!-- Phone Door (Warm Parchment) -->
        <a
          :href="`tel:${CUSTOMER_SUPPORT_PAGE.phoneE164}`"
          class="support-door support-door--light"
        >
          <div class="support-door__body">
            <span class="support-door__tag">Telephone</span>
            <h2 class="support-door__title">Studio Call</h2>
            <p class="support-door__desc">{{ CUSTOMER_SUPPORT_PAGE.phoneDisplay }}</p>
            <span class="support-door__cta">Call Desk &rarr;</span>
          </div>
        </a>

        <!-- Email Door (Warm Parchment) -->
        <a
          :href="`mailto:${CUSTOMER_SUPPORT_PAGE.email}`"
          class="support-door support-door--light"
        >
          <div class="support-door__body">
            <span class="support-door__tag">Email Desk</span>
            <h2 class="support-door__title">Inquiries</h2>
            <p class="support-door__desc">{{ CUSTOMER_SUPPORT_PAGE.email }}</p>
            <span class="support-door__cta">Send Email &rarr;</span>
          </div>
        </a>
      </section>

      <!-- Studio Location & Schedule Strip -->
      <section class="support-studio" aria-label="Studio Location and Hours">
        <div class="studio-card">
          <div class="studio-card__header">
            <h2 class="studio-card__title">{{ CUSTOMER_SUPPORT_PAGE.studioTitle }}</h2>
            <p class="studio-card__address">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
              <span>{{ CUSTOMER_SUPPORT_PAGE.studioAddress }}</span>
            </p>
          </div>

          <div class="studio-card__schedule">
            <div class="schedule-item">
              <span class="schedule-item__days">Tuesday &amp; Wednesday</span>
              <span class="schedule-item__note">{{ CUSTOMER_SUPPORT_PAGE.packageDays }}</span>
            </div>
            <div class="schedule-item">
              <span class="schedule-item__days">Mon, Thu &ndash; Sat</span>
              <span class="schedule-item__note">{{ CUSTOMER_SUPPORT_PAGE.treatmentDays }}</span>
            </div>
            <div class="schedule-item schedule-item--muted">
              <span class="schedule-item__days">Sunday</span>
              <span class="schedule-item__note">{{ CUSTOMER_SUPPORT_PAGE.sundayNotice }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Practical Notes (Calm, non-glaring) -->
      <section class="support-tips" aria-label="Helpful Notes">
        <h2 class="support-tips__heading">Helpful notes for your visit</h2>
        <div class="tips-grid">
          <div class="tip-card">
            <h3 class="tip-card__title">M-Pesa payment</h3>
            <p class="tip-card__body">
              Enter your M-Pesa phone number at checkout to receive the prompt. Once approved, your slot is secured instantly.
            </p>
          </div>
          <div class="tip-card">
            <h3 class="tip-card__title">Need to reschedule?</h3>
            <p class="tip-card__body">
              Reach out via WhatsApp at least 24 hours prior to your scheduled time and we will gladly move your slot.
            </p>
          </div>
          <div class="tip-card">
            <h3 class="tip-card__title">Receipts and confirmation</h3>
            <p class="tip-card__body">
              An official PDF receipt is emailed automatically upon payment approval. Check your inbox anytime.
            </p>
          </div>
        </div>
      </section>

      <!-- Clean Navigation -->
      <nav class="support-nav" aria-label="Auxiliary Navigation">
        <NuxtLink to="/faq" class="support-nav__link">Frequently Asked Questions</NuxtLink>
        <span class="support-nav__dot" aria-hidden="true">&bull;</span>
        <NuxtLink to="/services" class="support-nav__link">View Services</NuxtLink>
        <span class="support-nav__dot" aria-hidden="true">&bull;</span>
        <NuxtLink to="/book" class="support-nav__link">Book an Appointment</NuxtLink>
      </nav>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import {
  CUSTOMER_SUPPORT_PAGE,
  MELLIS_FLOWER_SRC,
} from '~/src/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Contact Us | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content: 'Contact Shee Aesthetics in Meru Town. Direct WhatsApp, phone call, email, and studio opening hours.',
    },
  ],
})

const flowerSrc = MELLIS_FLOWER_SRC

const whatsappUrl = computed(() => {
  const text = encodeURIComponent('Hello Shee, I have an inquiry regarding an appointment at Shee Aesthetics.')
  return `https://wa.me/${CUSTOMER_SUPPORT_PAGE.whatsappE164}?text=${text}`
})
</script>

<style scoped>
.support-page {
  min-height: 100vh;
  padding: clamp(2.5rem, 5vh, 4.5rem) 1.25rem 5rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
}

.support-page__inner {
  max-width: 62rem;
  margin: 0 auto;
}

.support-page__header {
  text-align: center;
  max-width: 38rem;
  margin: 0 auto clamp(2rem, 4vh, 3rem);
}

.support-page__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 5.5vw, 3rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.support-page__eyebrow {
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

.support-page__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.support-page__lead {
  margin: 0 auto;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Doors Grid (harmonious with Services Doors) */
.support-doors {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(17rem, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.support-door {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: 10px;
  padding: 1.5rem;
  text-decoration: none;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.support-door:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(23, 21, 22, 0.1);
}

.support-door--dark {
  background:
    radial-gradient(ellipse 90% 70% at 100% 100%, rgba(176, 122, 113, 0.22), transparent 60%),
    linear-gradient(165deg, #241e20 0%, #171516 100%);
  border: 1px solid rgba(176, 122, 113, 0.35);
  color: #ffffff;
}

.support-door--dark .support-door__tag {
  color: #f0b8ac;
}

.support-door--dark .support-door__title {
  color: #ffffff;
}

.support-door--dark .support-door__desc {
  color: rgba(255, 248, 244, 0.78);
}

.support-door--dark .support-door__cta {
  background: var(--color-rose, #b07a71);
  color: #ffffff;
}

.support-door--light {
  background:
    radial-gradient(ellipse 75% 60% at 0% 0%, rgba(176, 122, 113, 0.12), transparent 55%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  color: var(--color-ink, #252223);
  box-shadow: 0 4px 14px rgba(23, 21, 22, 0.03);
}

.support-door--light .support-door__tag {
  color: var(--color-rose-dark, #965f57);
}

.support-door--light .support-door__title {
  color: var(--color-ink, #252223);
}

.support-door--light .support-door__desc {
  color: var(--color-muted, #6b605c);
}

.support-door--light .support-door__cta {
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
}

.support-door__bloom {
  position: absolute;
  right: -0.5rem;
  bottom: -0.5rem;
  opacity: 0.18;
  pointer-events: none;
}

.support-door__body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.support-door__tag {
  font: 700 0.65rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.65rem;
}

.support-door__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.35rem;
}

.support-door__desc {
  margin: 0 0 1.25rem;
  font: 400 0.88rem/1.55 var(--font-body);
  flex-grow: 1;
}

.support-door__cta {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  padding: 0.45rem 0.85rem;
  border-radius: 999px;
  font: 700 0.68rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: opacity 0.18s ease;
}

.support-door:hover .support-door__cta {
  opacity: 0.9;
}

/* Studio Section */
.support-studio {
  margin-bottom: 2rem;
}

.studio-card {
  background:
    radial-gradient(ellipse 80% 60% at 50% 0%, rgba(176, 122, 113, 0.08), transparent 60%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 10px;
  padding: clamp(1.4rem, 3.5vw, 1.85rem);
  box-shadow: 0 4px 14px rgba(23, 21, 22, 0.03);
}

.studio-card__header {
  margin-bottom: 1.15rem;
  border-bottom: 1px solid rgba(176, 122, 113, 0.2);
  padding-bottom: 0.85rem;
}

.studio-card__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.3rem;
  color: var(--color-ink, #252223);
}

.studio-card__address {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  margin: 0;
  font: 500 0.9rem/1.4 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.studio-card__schedule {
  display: grid;
  gap: 0.6rem;
}

.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  font: 400 0.9rem/1.4 var(--font-body);
}

.schedule-item__days {
  font-weight: 600;
  color: var(--color-ink, #252223);
  min-width: 10rem;
}

.schedule-item__note {
  color: var(--color-muted, #6b605c);
}

.schedule-item--muted .schedule-item__days,
.schedule-item--muted .schedule-item__note {
  opacity: 0.65;
}

/* Tips */
.support-tips {
  margin-bottom: 2.5rem;
}

.support-tips__heading {
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.2rem;
  color: var(--color-ink, #252223);
  margin: 0 0 1rem;
  text-align: center;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}

.tip-card {
  background: rgba(235, 230, 225, 0.7);
  border: 1px solid rgba(44, 44, 48, 0.08);
  border-radius: 8px;
  padding: 1.15rem;
}

.tip-card__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.05rem;
  color: var(--color-ink, #252223);
}

.tip-card__body {
  margin: 0;
  font: 400 0.86rem/1.55 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Nav */
.support-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.support-nav__link {
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark, #965f57);
  transition: color 0.18s ease;
}

.support-nav__link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.support-nav__dot {
  color: var(--color-muted, #6b605c);
  opacity: 0.4;
}

@media (max-width: 640px) {
  .schedule-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.15rem;
  }
}
</style>
