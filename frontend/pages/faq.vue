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
        <div class="faq__title-lockup">
          <img
            :src="flowerSrc"
            alt=""
            class="faq__title-flower faq__title-flower--left"
            aria-hidden="true"
            width="44"
            height="44"
            decoding="async"
          />
          <h1 class="faq__title">Frequently Asked Questions</h1>
          <img
            :src="flowerSrc"
            alt=""
            class="faq__title-flower faq__title-flower--right"
            aria-hidden="true"
            width="44"
            height="44"
            decoding="async"
          />
        </div>
      </div>
    </header>

    <div class="faq__body">
      <div class="faq__grid" role="region" aria-label="Questions list">
        <article
          v-for="item in CLIENT_FAQ_ITEMS"
          :key="item.id"
          class="faq__card"
          :class="{ 'faq__card--open': openId === item.id }"
        >
          <button
            type="button"
            class="faq__card-trigger"
            :aria-expanded="openId === item.id"
            :aria-controls="`answer-${item.id}`"
            @click="toggleItem(item.id)"
          >
            <div class="faq__card-head">
              <span class="faq__card-category">{{ item.categoryLabel }}</span>
              <h2 class="faq__card-question">{{ item.question }}</h2>
            </div>
            <span class="faq__card-icon" aria-hidden="true">
              {{ openId === item.id ? '−' : '+' }}
            </span>
          </button>

          <Transition name="faq-expand">
            <div
              v-show="openId === item.id"
              :id="`answer-${item.id}`"
              class="faq__card-answer"
            >
              <p>{{ item.answer }}</p>
            </div>
          </Transition>
        </article>
      </div>

      <aside class="faq__aside" aria-label="Still need help">
        <div class="faq__aside-card">
          <p class="faq__aside-eyebrow">Direct Assistance</p>
          <h2 class="faq__aside-title">Still have a question?</h2>
          <p class="faq__aside-copy">
            We are here to help you get ready for your visit. Contact us directly or choose your date to book online.
          </p>
          <div class="faq__aside-actions">
            <SiteButton to="/services" variant="outline">View services</SiteButton>
            <SiteButton to="/book" variant="primary">Book now</SiteButton>
          </div>
        </div>
      </aside>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { buildFaqPageJsonLd } from '@/landing/agentSeo'
import {
  CLIENT_FAQ_ITEMS,
  FAQ_CATEGORIES,
  filterFaqItems,
  type FaqCategoryOption,
} from '@/landing/clientFaqArchitecture'
import { MELLIS_FLOWER_SRC } from '@/landing/clientPagesContent'

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
const activeCategory = ref<FaqCategoryOption['id']>('all')
const openId = ref<string | null>('faq-days')

const filteredItems = computed(() => filterFaqItems(CLIENT_FAQ_ITEMS, activeCategory.value))

function toggleItem(id: string) {
  openId.value = openId.value === id ? null : id
}
</script>

<style scoped>
.faq {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(176, 122, 113, 0.12), transparent 55%),
    linear-gradient(180deg, var(--color-paper) 0%, var(--color-parchment) 100%);
  min-height: 70vh;
}

.faq__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.22;
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
  padding: clamp(2.5rem, 6vh, 4rem) 1rem 2rem;
  border-bottom: 1px solid var(--color-line);
}

.faq__hero-inner {
  width: var(--container);
  max-width: 44rem;
  margin: 0 auto;
  text-align: center;
}

.faq__eyebrow {
  margin: 0 0 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-rose);
}

.faq__title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.5rem, 2vw, 0.9rem);
  margin: 0 0 0.85rem;
}

.faq__title-flower {
  width: clamp(1.8rem, 4vw, 2.4rem);
  height: auto;
  object-fit: contain;
  opacity: 0.82;
  flex-shrink: 0;
}

.faq__title-flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.faq__title-flower--right {
  transform: rotate(8deg);
}

.faq__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: clamp(1.95rem, 4.8vw, 2.75rem);
  line-height: 1.15;
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.faq__lead {
  margin: 0 auto 1.75rem;
  max-width: 36rem;
  font: 400 1.02rem/1.65 var(--font-body);
  color: var(--color-muted);
}

/* Category Filter Bar */
.faq__categories {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.faq__cat-btn {
  min-height: 2.35rem;
  padding: 0.4rem 0.95rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--color-surface-raised, #ebe7e3);
  color: var(--color-ink);
  font: 600 0.74rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    color 0.2s ease,
    transform 0.15s ease;
}

.faq__cat-btn:hover {
  border-color: var(--color-rose);
  transform: translateY(-1px);
}

.faq__cat-btn--active {
  border-color: var(--color-rose);
  background: var(--color-rose);
  color: #fff;
  box-shadow: 0 6px 16px rgba(176, 122, 113, 0.3);
}

/* Body & Interactive Cards */
.faq__body {
  position: relative;
  z-index: 1;
  width: var(--container);
  max-width: 44rem;
  margin: 0 auto;
  padding: 2.25rem 1rem 4.5rem;
}

.faq__grid {
  display: grid;
  gap: 0.85rem;
}

.faq__card {
  border: 1px solid var(--color-line);
  border-radius: 14px;
  background: var(--color-surface-raised, #ebe7e3);
  box-shadow: 0 4px 14px rgba(23, 21, 22, 0.05);
  overflow: hidden;
  transition:
    border-color 0.25s ease,
    box-shadow 0.25s ease,
    transform 0.2s ease;
}

.faq__card:hover {
  border-color: rgba(176, 122, 113, 0.45);
  transform: translateY(-1px);
}

.faq__card--open {
  border-color: var(--color-rose);
  box-shadow: 0 10px 24px rgba(176, 122, 113, 0.15);
}

.faq__card-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.35rem;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.faq__card-head {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.faq__card-category {
  font: 600 0.66rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.faq__card-question {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: clamp(1.08rem, 2.4vw, 1.25rem);
  line-height: 1.3;
  letter-spacing: -0.015em;
  color: var(--color-ink);
}

.faq__card-icon {
  display: grid;
  place-content: center;
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  border: 1px solid var(--color-line);
  background: var(--color-paper);
  color: var(--color-rose-dark);
  font: 600 1.1rem/1 var(--font-body);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease;
}

.faq__card--open .faq__card-icon {
  background: var(--color-rose);
  border-color: var(--color-rose);
  color: #fff;
}

.faq__card-answer {
  padding: 0 1.35rem 1.35rem;
  border-top: 1px dashed rgba(176, 122, 113, 0.25);
  margin-top: 0.15rem;
}

.faq__card-answer p {
  margin: 0.85rem 0 0;
  font: 400 0.96rem/1.7 var(--font-body);
  color: var(--color-muted);
}

/* Vue expand transition */
.faq-expand-enter-active,
.faq-expand-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.faq-expand-enter-from,
.faq-expand-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Direct Help Card */
.faq__aside {
  margin-top: 2.75rem;
}

.faq__aside-card {
  padding: 1.85rem 1.5rem;
  border: 1px solid var(--color-line);
  border-radius: 16px;
  background:
    radial-gradient(ellipse 70% 60% at 50% 0%, rgba(222, 150, 141, 0.15), transparent 65%),
    var(--color-surface-raised, #ebe7e3);
  text-align: center;
  box-shadow: 0 8px 20px rgba(23, 21, 22, 0.06);
}

.faq__aside-eyebrow {
  margin: 0 0 0.45rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font: 600 0.68rem/1 var(--font-body);
  color: var(--color-rose);
}

.faq__aside-title {
  margin: 0 0 0.55rem;
  font-family: var(--font-display);
  font-size: clamp(1.4rem, 3.2vw, 1.75rem);
  font-weight: 500;
  color: var(--color-ink);
}

.faq__aside-copy {
  margin: 0 auto 1.35rem;
  max-width: 32ch;
  font: 400 0.94rem/1.6 var(--font-body);
  color: var(--color-muted);
}

.faq__aside-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}
</style>
