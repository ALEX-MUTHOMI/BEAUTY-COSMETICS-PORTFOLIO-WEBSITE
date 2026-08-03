<template>
  <main class="faq">
    <div class="faq__inner">
      <!-- Hero Header -->
      <header class="faq__hero">
        <p class="faq__script" aria-hidden="true">Shee</p>
        <span class="faq__eyebrow">Help &amp; Questions</span>
        <div class="title-lockup">
          <img
            :src="flowerSrc"
            alt=""
            class="title-lockup__flower title-lockup__flower--left"
            aria-hidden="true"
            width="36"
            height="36"
            decoding="async"
          />
          <h1 class="faq__title">Frequently asked questions</h1>
          <img
            :src="flowerSrc"
            alt=""
            class="title-lockup__flower title-lockup__flower--right"
            aria-hidden="true"
            width="36"
            height="36"
            decoding="async"
          />
        </div>
        <p class="faq__lead">Answers to common questions about booking, payments, and appointments in Meru.</p>

        <!-- Search Bar (Soft, no glare) -->
        <div class="faq__search-wrap">
          <div class="faq__search-box">
            <svg class="faq__search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search (e.g. M-Pesa, packages, facial)..."
              class="faq__search-input"
              aria-label="Search questions"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="faq__search-clear"
              aria-label="Clear search"
              @click="searchQuery = ''"
            >
              &times;
            </button>
          </div>
        </div>

        <!-- Category Filter Tabs (Harmonious with Services Board) -->
        <div class="faq__category-nav" role="tablist" aria-label="Filter by Category">
          <button
            v-for="cat in FAQ_CATEGORIES"
            :key="cat.id"
            type="button"
            role="tab"
            :aria-selected="activeCategory === cat.id"
            class="faq__category-btn"
            :class="{ 'faq__category-btn--active': activeCategory === cat.id }"
            @click="activeCategory = cat.id"
          >
            {{ cat.label }}
          </button>
        </div>
      </header>

      <!-- Questions & Aside Grid -->
      <div class="faq__body">
        <div class="faq__grid" role="region" aria-label="Questions list">
          <div v-if="filteredItems.length === 0" class="faq__empty">
            <p>No questions matched your search.</p>
            <button type="button" class="faq__reset-btn" @click="resetFilters">Show all questions</button>
          </div>

          <article
            v-for="item in filteredItems"
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
                <h2 class="faq__card-question">{{ item.q }}</h2>
              </div>
              <span class="faq__card-icon" aria-hidden="true">
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  :class="{ 'faq__icon-rotated': openId === item.id }"
                >
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </span>
            </button>

            <Transition name="faq-expand">
              <div
                v-show="openId === item.id"
                :id="`answer-${item.id}`"
                class="faq__card-answer"
              >
                <p>{{ item.a }}</p>
              </div>
            </Transition>
          </article>
        </div>

        <!-- Aside Help Card (Rich Obsidian Accent) -->
        <aside class="faq__aside" aria-label="Direct Assistance">
          <div class="faq__aside-card">
            <span class="faq__aside-tag">Direct Desk</span>
            <h2 class="faq__aside-title">Need help with something else?</h2>
            <p class="faq__aside-copy">
              We are happy to answer any questions or help arrange a special time for your visit.
            </p>
            <div class="faq__aside-actions">
              <NuxtLink to="/support" class="faq__aside-btn faq__aside-btn--outline">
                Contact Us
              </NuxtLink>
              <NuxtLink to="/book" class="faq__aside-btn faq__aside-btn--primary">
                Book appointment
              </NuxtLink>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
/**
 * FAQ Page
 * Renders frequently asked questions regarding services, payments, and appointments.
 */
import { computed, ref } from 'vue'

import { buildFaqPageJsonLd } from '~/src/landing/agentSeo'
import {
  FAQ_CATEGORIES,
  FAQ_ITEMS,
  MELLIS_FLOWER_SRC,
  type FaqItem,
} from '~/src/landing/clientPagesContent'

definePageMeta({ layout: 'landing' })

const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'
const title = 'FAQ | Shee Aesthetics Meru'
const description =
  'Answers for booking appointments at Shee Aesthetics in Meru Town: facials, waxing, massage, makeup, M-Pesa payments, and rescheduling.'

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
const activeCategory = ref<string>('all')
const searchQuery = ref('')
const openId = ref<string | null>('faq-booking')

const filteredItems = computed(() => {
  let list: FaqItem[] =
    activeCategory.value === 'all'
      ? FAQ_ITEMS
      : FAQ_ITEMS.filter((item) => item.category === activeCategory.value)

  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      (item) =>
        item.q.toLowerCase().includes(q) ||
        item.a.toLowerCase().includes(q) ||
        item.categoryLabel.toLowerCase().includes(q),
    )
  }
  return list
})

function toggleItem(id: string) {
  openId.value = openId.value === id ? null : id
}

function resetFilters() {
  activeCategory.value = 'all'
  searchQuery.value = ''
}
</script>

<style scoped>
.faq {
  min-height: 100vh;
  padding: clamp(2.5rem, 5vh, 4.5rem) 1.25rem 5rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
}

.faq__inner {
  max-width: 62rem;
  margin: 0 auto;
}

.faq__hero {
  text-align: center;
  max-width: 42rem;
  margin: 0 auto clamp(2rem, 4vh, 2.75rem);
}

.faq__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 5.5vw, 3rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.faq__eyebrow {
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

.faq__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.faq__lead {
  margin: 0 auto 1.5rem;
  max-width: 36ch;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Search bar (calm, non-glaring) */
.faq__search-wrap {
  max-width: 26rem;
  margin: 0 auto 1.25rem;
}

.faq__search-box {
  position: relative;
  display: flex;
  align-items: center;
  background: #ded8d2;
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 999px;
  padding: 0.45rem 0.9rem;
  transition: border-color 0.18s ease;
}

.faq__search-box:focus-within {
  border-color: var(--color-rose, #b07a71);
}

.faq__search-icon {
  color: var(--color-muted, #6b605c);
  flex-shrink: 0;
  margin-right: 0.5rem;
}

.faq__search-input {
  width: 100%;
  border: none;
  background: transparent;
  font: 400 0.9rem/1 var(--font-body);
  color: var(--color-ink, #252223);
  outline: none;
}

.faq__search-input::placeholder {
  color: var(--color-muted, #6b605c);
  opacity: 0.7;
}

.faq__search-clear {
  background: transparent;
  border: none;
  color: var(--color-muted, #6b605c);
  cursor: pointer;
  padding: 0.15rem 0.35rem;
  font-size: 1rem;
}

/* Category Filter Nav */
.faq__category-nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
}

.faq__category-btn {
  padding: 0.38rem 0.85rem;
  border-radius: 999px;
  border: 1px solid rgba(176, 122, 113, 0.24);
  background: #ded8d2;
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-ink, #252223);
  cursor: pointer;
  transition: all 0.18s ease;
}

.faq__category-btn:hover {
  border-color: var(--color-rose, #b07a71);
  color: var(--color-rose-dark, #965f57);
}

.faq__category-btn--active {
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
  border-color: var(--color-card-dark, #1e191b);
}

/* Body & Grid */
.faq__body {
  display: grid;
  grid-template-columns: 1fr 18rem;
  gap: 1.5rem;
  align-items: start;
}

.faq__grid {
  display: grid;
  gap: 0.75rem;
}

.faq__empty {
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: #ded8d2;
  border-radius: 8px;
  color: var(--color-muted, #6b605c);
}

.faq__reset-btn {
  margin-top: 0.5rem;
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  background: var(--color-card-dark, #1e191b);
  color: #fff;
  border: none;
  font: 600 0.78rem/1 var(--font-body);
  cursor: pointer;
}

.faq__card {
  background:
    radial-gradient(ellipse 80% 60% at 0% 0%, rgba(176, 122, 113, 0.08), transparent 60%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(23, 21, 22, 0.02);
  transition: border-color 0.18s ease;
}

.faq__card:hover {
  border-color: rgba(176, 122, 113, 0.45);
}

.faq__card--open {
  border-color: var(--color-rose, #b07a71);
}

.faq__card-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.25rem;
  background: transparent;
  border: none;
  text-align: left;
  cursor: pointer;
}

.faq__card-head {
  display: grid;
  gap: 0.15rem;
}

.faq__card-category {
  font: 700 0.65rem/1 var(--font-body);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-rose-dark, #965f57);
}

.faq__card-question {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.05rem;
  line-height: 1.35;
  color: var(--color-ink, #252223);
}

.faq__card-icon {
  flex-shrink: 0;
  color: var(--color-rose, #b07a71);
  display: grid;
  place-items: center;
}

.faq__card-icon svg {
  transition: transform 0.2s ease;
}

.faq__icon-rotated {
  transform: rotate(180deg);
}

.faq__card-answer {
  padding: 0 1.25rem 1.25rem;
  border-top: 1px solid rgba(176, 122, 113, 0.15);
  padding-top: 0.75rem;
}

.faq__card-answer p {
  margin: 0;
  font: 400 0.9rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Aside Card (Dark obsidian tone) */
.faq__aside {
  position: sticky;
  top: 5.5rem;
}

.faq__aside-card {
  background:
    radial-gradient(ellipse 90% 70% at 100% 100%, rgba(176, 122, 113, 0.2), transparent 60%),
    linear-gradient(165deg, #241e20 0%, #171516 100%);
  border: 1px solid rgba(176, 122, 113, 0.35);
  border-radius: 10px;
  padding: 1.4rem;
  color: #ffffff;
  box-shadow: 0 8px 20px rgba(23, 21, 22, 0.08);
}

.faq__aside-tag {
  display: inline-block;
  font: 700 0.65rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #f0b8ac;
  margin-bottom: 0.5rem;
}

.faq__aside-title {
  margin: 0 0 0.45rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.15rem;
  color: #ffffff;
}

.faq__aside-copy {
  margin: 0 0 1.25rem;
  font: 400 0.86rem/1.55 var(--font-body);
  color: rgba(255, 248, 244, 0.78);
}

.faq__aside-actions {
  display: grid;
  gap: 0.5rem;
}

.faq__aside-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  text-decoration: none;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  transition: opacity 0.18s ease;
}

.faq__aside-btn--primary {
  background: var(--color-rose, #b07a71);
  color: #ffffff;
}

.faq__aside-btn--outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.faq__aside-btn:hover {
  opacity: 0.9;
}

@media (max-width: 900px) {
  .faq__body {
    grid-template-columns: 1fr;
  }

  .faq__aside {
    position: static;
  }
}
</style>
