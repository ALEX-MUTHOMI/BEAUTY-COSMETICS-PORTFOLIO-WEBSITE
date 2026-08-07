<template>
  <main class="faq">
    <img
      :src="flowerSrc"
      alt=""
      class="faq__bloom faq__bloom--tl"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="120"
      height="120"
      decoding="async"
    />
    <img
      :src="flowerSrc"
      alt=""
      class="faq__bloom faq__bloom--br"
      data-testid="mellis-flower"
      aria-hidden="true"
      width="140"
      height="140"
      decoding="async"
    />

    <header class="faq__hero">
      <div class="faq__hero-inner">
        <p class="faq__eyebrow">{{ FAQ_PAGE.eyebrow }}</p>
        <div class="faq__title-lockup">
          <img
            :src="flowerSrc"
            alt=""
            class="faq__title-flower"
            aria-hidden="true"
            width="40"
            height="40"
            decoding="async"
          />
          <h1 class="faq__title">{{ FAQ_PAGE.title }}</h1>
          <img
            :src="flowerSrc"
            alt=""
            class="faq__title-flower"
            aria-hidden="true"
            width="40"
            height="40"
            decoding="async"
          />
        </div>
        <p class="faq__lead">{{ FAQ_PAGE.lead }}</p>
      </div>
    </header>

    <div class="faq__body">
      <div class="faq__list" role="list">
        <article
          v-for="item in FAQ_ITEMS"
          :key="item.id"
          class="faq__item"
          role="listitem"
        >
          <h2 class="faq__question" :id="item.id">{{ item.q }}</h2>
          <p class="faq__answer">{{ item.a }}</p>
        </article>
      </div>

      <aside class="faq__aside" aria-label="Still need help">
        <p class="faq__aside-eyebrow">{{ FAQ_PAGE.asideEyebrow }}</p>
        <p class="faq__aside-copy">{{ FAQ_PAGE.asideCopy }}</p>
        <div class="faq__aside-actions">
          <SiteButton to="/services" variant="outline">View services</SiteButton>
          <SiteButton to="/book" variant="primary">Book now</SiteButton>
        </div>
      </aside>
    </div>
  </main>
</template>

<script setup lang="ts">
import { buildFaqPageJsonLd } from '@/landing/agentSeo'
import { FAQ_ITEMS, FAQ_PAGE, MELLIS_FLOWER_SRC } from '@/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'
const title = 'FAQ | Shee Aesthetics Meru — Booking, M-Pesa & Visits'
const description =
  'Answers for booking Shee Aesthetics beauty salon in Meru Town: facials, waxing, massage, makeup, M-Pesa confirmation, and how to change a visit.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogUrl: `${siteUrl}/faq`,
  robots: 'index, follow',
})

useHead({
  title,
  link: [{ rel: 'canonical', href: `${siteUrl}/faq` }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(buildFaqPageJsonLd(siteUrl)),
    },
  ],
})

const flowerSrc = MELLIS_FLOWER_SRC
</script>

<style scoped>
.faq {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(176, 122, 113, 0.08), transparent 55%),
    linear-gradient(180deg, var(--color-paper) 0%, var(--color-parchment) 100%);
  min-height: 60vh;
}

.faq__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.2;
  filter: saturate(1.3) brightness(1.02);
}

.faq__bloom--tl {
  top: 0.75rem;
  left: max(0.35rem, env(safe-area-inset-left));
  width: min(110px, 22vw);
  transform: rotate(-18deg);
}

.faq__bloom--br {
  right: max(0.35rem, env(safe-area-inset-right));
  bottom: 2rem;
  width: min(130px, 26vw);
  transform: rotate(145deg);
}

.faq__hero {
  position: relative;
  z-index: 1;
  padding: clamp(2.5rem, 7vh, 4.5rem) 1rem 2rem;
  border-bottom: 1px solid var(--color-line);
}

.faq__hero-inner {
  width: var(--container);
  max-width: 40rem;
  margin: 0 auto;
  text-align: center;
}

.faq__eyebrow {
  margin: 0 0 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-rose);
}

.faq__title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin: 0 0 1rem;
}

.faq__title-flower {
  width: 2rem;
  height: 2rem;
  object-fit: contain;
  opacity: 0.7;
  flex-shrink: 0;
}

.faq__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 5vw, 2.85rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.faq__lead {
  margin: 0;
  font: 400 1.05rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.faq__body {
  position: relative;
  z-index: 1;
  width: var(--container);
  max-width: 40rem;
  margin: 0 auto;
  padding: 2.5rem 1rem 4.5rem;
}

.faq__list {
  display: grid;
  gap: 0;
}

.faq__item {
  padding: 1.65rem 0;
  border-bottom: 1px solid var(--color-line);
}

.faq__item:first-child {
  padding-top: 0.25rem;
}

.faq__question {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: clamp(1.15rem, 2.5vw, 1.35rem);
  letter-spacing: -0.015em;
  color: var(--color-ink);
}

.faq__answer {
  margin: 0;
  font: 400 0.98rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.faq__aside {
  margin-top: 2.75rem;
  padding: 1.75rem 0 0;
  border-top: 1px solid var(--color-line);
  text-align: center;
}

.faq__aside-eyebrow {
  margin: 0 0 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font: 600 0.7rem/1 var(--font-body);
  color: var(--color-rose);
}

.faq__aside-copy {
  margin: 0 auto 1.35rem;
  max-width: 32ch;
  font: 400 0.95rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.faq__aside-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}
</style>
