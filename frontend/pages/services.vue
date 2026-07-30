<template>
  <main class="services-page">
    <header class="services-hero">
      <div class="services-hero__media" aria-hidden="true">
        <img
          src="/images/stock-makeup-glam.jpg"
          alt=""
          class="services-hero__photo"
          width="1600"
          height="1000"
          fetchpriority="high"
          decoding="async"
        />
        <div class="services-hero__veil" />
      </div>
      <div class="services-hero__inner">
        <p class="label">{{ pageIntro.eyebrow }}</p>
        <h1>{{ pageIntro.title }}</h1>
        <p class="services-hero__lead">{{ pageIntro.lead }}</p>
      </div>
    </header>

    <section class="services-chooser" aria-label="Choose how you want to book">
      <p class="services-chooser__days" role="note" aria-label="Booking days">
        <span>Tue &amp; Wed packages</span>
        <span class="services-chooser__days-sep" aria-hidden="true">·</span>
        <span>{{ SINGLE_DAYS_LABEL }} treatments</span>
      </p>
      <nav class="services-doors">
        <a
          href="#full-packages"
          class="services-door services-door--packages"
          @click="scrollToSection('full-packages', $event)"
        >
          <img
            src="/images/stock-makeup-glam.jpg"
            alt=""
            class="services-door__media"
            loading="lazy"
            decoding="async"
            width="800"
            height="1000"
          />
          <span class="services-door__wash" aria-hidden="true" />
          <img
            src="/images/flower.png"
            alt=""
            class="services-door__flower"
            aria-hidden="true"
            loading="lazy"
            decoding="async"
            width="72"
            height="72"
          />
          <span class="services-door__body">
            <span class="services-door__title">Packages</span>
            <span class="services-door__sub">Tue &amp; Wed · full glow</span>
          </span>
        </a>
        <a
          href="#single-sessions"
          class="services-door services-door--treatments"
          @click="scrollToSection('single-sessions', $event)"
        >
          <img
            src="/images/stock-spa-skincare.jpg"
            alt=""
            class="services-door__media services-door__media--mono"
            loading="lazy"
            decoding="async"
            width="800"
            height="1000"
          />
          <span class="services-door__wash services-door__wash--photo" aria-hidden="true" />
          <img
            src="/images/flower.png"
            alt=""
            class="services-door__flower"
            aria-hidden="true"
            loading="lazy"
            decoding="async"
            width="72"
            height="72"
          />
          <span class="services-door__body">
            <span class="services-door__title">Treatments</span>
            <span class="services-door__sub">{{ SINGLE_DAYS_LABEL }} · one service</span>
          </span>
        </a>
      </nav>
    </section>

    <section id="full-packages" class="services-packages">
      <div class="services-packages__bg" aria-hidden="true">
        <img
          src="/images/stock-makeup-glam.jpg"
          alt=""
          class="services-packages__photo"
          loading="lazy"
          decoding="async"
          width="1600"
          height="1000"
        />
        <div class="services-packages__veil" />
      </div>
      <header class="services-section-head services-section-head--on-dark">
        <p class="label">Packages</p>
        <div class="title-lockup">
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower"
            width="48"
            height="48"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
          <h2>Complete visits</h2>
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower"
            width="48"
            height="48"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
        </div>
        <p class="services-section-head__sub">
          Tue &amp; Wed — facial, wax, massage and makeup in one booking.
        </p>
      </header>
      <div class="services-packages__grid">
        <MellisPackageCard
          v-for="pkg in packages"
          :key="pkg.name"
          :name="pkg.name"
          :text="pkg.text"
          :price="pkg.price"
          :includes="pkg.includes"
          :featured="pkg.featured"
          :badge="pkg.badge"
          :days-label="pkg.daysLabel"
          :cta-label="pkg.ctaLabel || 'Book this package'"
          :cta-to="bookHrefForPackageName(pkg.name)"
        />
      </div>
    </section>

    <section id="single-sessions" class="services-treatments">
      <header class="services-section-head">
        <p class="label">Treatments</p>
        <div class="title-lockup">
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower"
            width="48"
            height="48"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
          <h2>Choose a treatment</h2>
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower"
            width="48"
            height="48"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
        </div>
        <p class="services-section-head__sub">
          {{ SINGLE_DAYS_LABEL }}. Pick a category, then book.
        </p>
      </header>

      <div id="treatments" class="services-picker" aria-label="Treatments and prices">
        <div
          class="services-board"
          role="tablist"
          aria-label="Service categories"
        >
          <button
            v-for="(category, index) in serviceCategories"
            :id="`tab-${category.id}`"
            :key="category.id"
            type="button"
            role="tab"
            class="services-board__cell"
            :class="{ 'services-board__cell--active': activeCategoryId === category.id }"
            :aria-selected="activeCategoryId === category.id"
            :aria-controls="`panel-${category.id}`"
            @click="selectCategory(category.id)"
          >
            <img
              :src="category.image"
              alt=""
              class="services-board__photo"
              loading="lazy"
              decoding="async"
              width="480"
              height="320"
            />
            <span class="services-board__veil" aria-hidden="true" />
            <span class="services-board__copy">
              <span class="services-board__num" aria-hidden="true">{{ padIndex(index) }}</span>
              <span class="services-board__title">{{ category.cardTitle }}</span>
              <span class="services-board__line">{{ boardLine(category.id) }}</span>
            </span>
          </button>
        </div>

        <div class="services-panel-wrap">
          <Transition name="panel-fade" mode="out-in">
            <div
              :id="`panel-${activeCategory.id}`"
              :key="activeCategoryId"
              role="tabpanel"
              class="services-panel"
              :class="`services-panel--${activeCategory.id}`"
              :aria-labelledby="`tab-${activeCategory.id}`"
            >
              <div class="services-panel__intro">
                <div class="services-panel__visual">
                  <img
                    :src="activeCategory.image"
                    :alt="activeCategory.imageAlt"
                    class="services-panel__photo"
                    loading="lazy"
                    decoding="async"
                    width="720"
                    height="480"
                  />
                </div>
                <div class="services-panel__copy">
                  <p class="label">{{ activeCategory.daysNote }}</p>
                  <h2>{{ activeCategory.name }}</h2>
                  <p class="services-panel__text">{{ activeCategory.intro }}</p>
                </div>
              </div>

              <div class="services-panel__menu">
                <ServiceTreatmentCard
                  v-for="(treatment, index) in activeCategory.treatments"
                  :key="treatment.name"
                  :name="treatment.name"
                  :duration="treatment.duration"
                  :price="treatment.price"
                  :highlights="treatment.highlights"
                  :index="index"
                  :book-to="bookHrefForTreatment(activeCategoryId, treatment.name)"
                />
              </div>
            </div>
          </Transition>
        </div>

        <p class="services-packages-link">
          Prefer a full visit?
          <a href="#full-packages" @click="scrollToSection('full-packages', $event)">See packages</a>
        </p>
      </div>
    </section>

    <section class="services-cta">
      <div class="services-cta__inner">
        <h2>Ready when you are</h2>
        <p>Full package or single treatment — book online and pay to confirm your slot.</p>
        <div class="services-cta__actions">
          <SiteButton
            href="#full-packages"
            variant="primary"
            @click="scrollToSection('full-packages', $event)"
          >
            View packages
          </SiteButton>
          <SiteButton
            href="#single-sessions"
            variant="ghost-light"
            @click="scrollToSection('single-sessions', $event)"
          >
            View treatments
          </SiteButton>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  packages,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import {
  SERVICE_CATEGORY_BOARD_LINES,
  SERVICES_PAGE_INTRO,
  serviceCategories,
} from '@/landing/servicesContent'
import {
  isServiceCategoryId,
  parseServicesHash,
  type ServiceCategoryId,
} from '@/landing/servicesNavigation'
import { bookHrefForPackageName, bookHrefForTreatment } from '@/landing/bookingHandoff'

const pageIntro = SERVICES_PAGE_INTRO
const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'

const categoryIds = serviceCategories.map((c) => c.id)
const activeCategoryId = ref<ServiceCategoryId>(
  (categoryIds[0] as ServiceCategoryId) ?? 'facials',
)

const activeCategory = computed(
  () => serviceCategories.find((c) => c.id === activeCategoryId.value) ?? serviceCategories[0]!,
)

function padIndex(index: number) {
  return String(index + 1).padStart(2, '0')
}

function boardLine(id: string) {
  return SERVICE_CATEGORY_BOARD_LINES[id] ?? ''
}

function selectCategory(id: string) {
  if (!isServiceCategoryId(id) || activeCategoryId.value === id) return
  activeCategoryId.value = id
  if (import.meta.client) {
    window.history.replaceState(null, '', `#${id}`)
  }
}

function applyHash(raw: string) {
  const { section, category } = parseServicesHash(raw)
  if (!section && !category) return

  if (section) {
    requestAnimationFrame(() => {
      document.getElementById(section)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
    return
  }

  if (category) {
    activeCategoryId.value = category
    requestAnimationFrame(() => {
      document.getElementById('treatments')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

function syncFromHash() {
  if (!import.meta.client) return
  applyHash(window.location.hash)
}

function scrollToSection(id: string, event: Event) {
  event.preventDefault()
  const { section } = parseServicesHash(`#${id}`)
  if (!section) return
  document.getElementById(section)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  if (import.meta.client) {
    window.history.replaceState(null, '', `#${section}`)
  }
}

function onPopState() {
  syncFromHash()
}

onMounted(() => {
  syncFromHash()
  window.addEventListener('popstate', onPopState)
})

onUnmounted(() => {
  if (import.meta.client) {
    window.removeEventListener('popstate', onPopState)
  }
})

definePageMeta({ layout: 'landing' })

const title = 'Services | Facials, Massage, Waxing & Makeup — Shee Aesthetics Meru'
const description =
  'Explore Shee Aesthetics services in Meru Town: full packages Tue & Wed, single treatments Mon Thu–Sat, and detailed facials, massage, waxing and makeup menu. Book online.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogUrl: `${siteUrl}/services`,
  ogType: 'website',
  twitterCard: 'summary_large_image',
})

useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}/services` }],
})
</script>

<style scoped>
.services-page {
  background: var(--color-paper);
  padding-bottom: calc(var(--mobile-book-bar-height) + env(safe-area-inset-bottom, 0px));
}

@media (min-width: 768px) {
  .services-page {
    padding-bottom: 0;
  }
}

.label {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

/* Hero — full-bleed visual plane */
.services-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  place-items: end center;
  min-height: clamp(16rem, 42vh, 22rem);
  padding: 0;
  color: #f8f2ee;
}

@media (min-width: 768px) {
  .services-hero {
    min-height: clamp(20rem, 48vh, 28rem);
  }
}

.services-hero__media {
  position: absolute;
  inset: 0;
}

.services-hero__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 28%;
  transform: scale(1.04);
  animation: services-hero-drift 18s ease-in-out infinite alternate;
}

.services-hero__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(18, 14, 16, 0.35) 0%, rgba(18, 14, 16, 0.72) 55%, rgba(18, 14, 16, 0.92) 100%);
}

.services-hero__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
  padding: 2.5rem 1rem 2rem;
  text-align: center;
}

.services-hero .label {
  color: rgba(240, 184, 172, 0.95);
}

.services-hero h1 {
  margin: 0 0 0.5rem;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 4.8vw, 2.65rem);
  font-weight: 400;
  line-height: 1.15;
  color: #f8f2ee;
}

.services-hero__lead {
  margin: 0;
  font: 400 0.95rem/1.55 var(--font-body);
  color: rgba(248, 242, 238, 0.78);
}

@keyframes services-hero-drift {
  from { transform: scale(1.04); }
  to { transform: scale(1.1); }
}

@media (prefers-reduced-motion: reduce) {
  .services-hero__photo {
    animation: none;
  }
}

/* Twin path doors */
.services-chooser {
  width: var(--container);
  margin: -1.5rem auto 0;
  position: relative;
  z-index: 2;
  padding: 0 0 0.5rem;
}

.services-chooser__days {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.25rem 0.4rem;
  margin: 0 0 0.85rem;
  padding: 0 1rem;
  font: 500 0.72rem/1.4 var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-muted);
  text-align: center;
}

.services-chooser__days-sep {
  color: var(--color-line);
}

.services-doors {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.65rem;
}

@media (min-width: 640px) {
  .services-doors {
    grid-template-columns: 1fr 1fr;
    gap: 0;
  }
}

.services-door {
  position: relative;
  display: block;
  min-height: 11.5rem;
  overflow: hidden;
  text-decoration: none;
  color: #f4ebe6;
  background: var(--color-card-dark);
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition: transform 0.35s var(--ease-story, ease);
}

@media (min-width: 640px) {
  .services-door {
    min-height: 15rem;
  }
}

@media (hover: hover) {
  .services-door:hover {
    transform: translateY(-2px);
  }

  .services-door:hover .services-door__media {
    transform: scale(1.06);
  }
}

.services-door:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

.services-door__media {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 28%;
  transition: transform 0.7s var(--ease-story, ease);
}

.services-door__media--mono {
  filter: grayscale(0.88) contrast(1.08) brightness(0.7);
}

.services-door__wash {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      105deg,
      rgba(22, 16, 18, 0.9) 0%,
      rgba(22, 16, 18, 0.72) 40%,
      rgba(22, 16, 18, 0.42) 100%
    );
  pointer-events: none;
}

.services-door__wash--photo {
  background:
    linear-gradient(
      105deg,
      rgba(24, 16, 20, 0.88) 0%,
      rgba(28, 18, 22, 0.62) 45%,
      rgba(22, 16, 18, 0.4) 100%
    );
}

.services-door__flower {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
  width: min(64px, 18%);
  opacity: 0.55;
  pointer-events: none;
  filter: saturate(1.15) brightness(0.95);
}

.services-door__body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 0.35rem;
  height: 100%;
  min-height: inherit;
  padding: 1.35rem 1.25rem;
}

.services-door__title {
  font-family: var(--font-script);
  font-size: clamp(2rem, 4.5vw, 2.75rem);
  line-height: 1.1;
  color: #f8f2ee;
}

.services-door__sub {
  font: 500 0.78rem/1.4 var(--font-body);
  letter-spacing: 0.04em;
  color: rgba(248, 242, 238, 0.78);
}

/* Package stage — dark atmosphere */
.services-packages {
  position: relative;
  overflow: clip;
  padding: clamp(2.25rem, 6vh, 3.5rem) max(1rem, env(safe-area-inset-left));
  margin-top: 1.25rem;
  background: #171516;
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-packages__bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.services-packages__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
  filter: grayscale(0.7) contrast(1.05) brightness(0.45) saturate(0.7);
  opacity: 0.55;
}

.services-packages__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(23, 21, 22, 0.55) 0%, rgba(23, 21, 22, 0.88) 55%, #171516 100%);
}

.services-section-head {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto 0.35rem;
  max-width: 40rem;
  text-align: center;
}

.services-section-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.2vw, 1.9rem);
  font-weight: 400;
  line-height: 1.25;
  color: var(--color-ink);
}

.services-section-head__sub {
  margin: 0.55rem 0 0;
  font: 400 0.9rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.services-section-head--on-dark h2 {
  color: #f8f2ee;
}

.services-section-head--on-dark .services-section-head__sub {
  color: rgba(248, 242, 238, 0.72);
}

.services-section-head--on-dark .label {
  color: rgba(240, 184, 172, 0.95);
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
}

.title-lockup__flower {
  width: 40px;
  height: 40px;
  opacity: 0.75;
  filter: saturate(1.15) brightness(0.95);
}

.services-packages__grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  width: var(--container);
  margin: 0 auto;
  padding-top: 1rem;
  align-items: stretch;
}

.services-packages__grid > * {
  min-width: 0;
}

/* Treatments section */
.services-treatments {
  padding: clamp(2rem, 5vh, 3.25rem) max(1rem, env(safe-area-inset-left));
  background: #1a1718;
  border-top: 1px solid rgba(248, 242, 238, 0.06);
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-treatments .services-section-head h2 {
  color: #f8f2ee;
}

.services-treatments .services-section-head__sub {
  color: rgba(248, 242, 238, 0.7);
}

.services-treatments .label {
  color: rgba(240, 184, 172, 0.95);
}

.services-picker {
  width: var(--container);
  margin: 1rem auto 0;
  padding: 0 0 0.5rem;
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-packages-link {
  margin: 1.5rem 0 0;
  text-align: center;
  font: 500 0.88rem/1.5 var(--font-body);
  color: rgba(248, 242, 238, 0.65);
}

.services-packages-link a {
  font-weight: 700;
  color: var(--color-rose);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.services-packages-link a:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

/* Category photo board */
.services-board {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 1.15rem;
}

.services-board__cell {
  position: relative;
  display: block;
  min-height: 7.5rem;
  padding: 0;
  border: 1px solid transparent;
  overflow: hidden;
  background: #121012;
  color: #f8f2ee;
  cursor: pointer;
  text-align: left;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.18s ease,
    transform 0.2s ease;
}

.services-board__cell:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-board__cell--active {
  border-color: var(--color-rose);
  box-shadow: 0 0 0 1px rgba(222, 150, 141, 0.35);
}

.services-board__cell:not(.services-board__cell--active) .services-board__veil {
  background: linear-gradient(180deg, rgba(12, 10, 11, 0.45), rgba(12, 10, 11, 0.88));
}

.services-board__cell--active .services-board__veil {
  background: linear-gradient(180deg, rgba(28, 18, 20, 0.28), rgba(28, 18, 20, 0.72));
}

@media (hover: hover) {
  .services-board__cell:hover:not(.services-board__cell--active) {
    transform: translateY(-1px);
  }
}

.services-board__photo {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.35) brightness(0.75);
}

.services-board__cell--active .services-board__photo {
  filter: grayscale(0.1) brightness(0.9);
}

.services-board__veil {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.services-board__copy {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  gap: 0.2rem;
  height: 100%;
  min-height: inherit;
  padding: 0.85rem 0.8rem;
}

.services-board__num {
  font: 700 0.68rem/1 var(--font-body);
  letter-spacing: 0.14em;
  color: var(--color-rose);
}

.services-board__title {
  font: 700 0.78rem/1.25 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.services-board__line {
  font: 400 0.72rem/1.35 var(--font-body);
  color: rgba(248, 242, 238, 0.7);
}

/* Active panel */
.services-panel-wrap {
  position: relative;
  min-height: 12rem;
}

.panel-fade-enter-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.panel-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.services-panel {
  border: 1px solid rgba(248, 242, 238, 0.1);
  background: rgba(23, 21, 22, 0.92);
  overflow: hidden;
}

.services-panel__intro {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
  padding: 1.15rem 1rem 1.25rem;
  border-bottom: 1px solid rgba(248, 242, 238, 0.1);
}

.services-panel__visual {
  position: relative;
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.services-panel__photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.15) contrast(1.05) brightness(0.9);
}

.services-panel__copy .label {
  color: rgba(240, 184, 172, 0.95);
}

.services-panel__copy h2 {
  margin: 0 0 0.55rem;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.2vw, 1.95rem);
  font-weight: 400;
  line-height: 1.25;
  color: #f8f2ee;
}

.services-panel__text {
  margin: 0;
  font: 400 0.95rem/1.7 var(--font-body);
  color: rgba(248, 242, 238, 0.75);
}

.services-panel__menu {
  padding: 0 1rem 0.35rem;
}

.services-cta {
  padding: clamp(2.5rem, 6vh, 4rem) 1rem;
  background: var(--color-footer);
  color: #fff;
  text-align: center;
}

.services-cta__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 36rem;
}

.services-cta h2 {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 4vw, 2.15rem);
  font-weight: 400;
  color: #fff;
}

.services-cta p {
  margin: 0 0 1.5rem;
  font: 400 0.95rem/1.7 var(--font-body);
  color: rgba(255, 255, 255, 0.78);
}

.services-cta__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
}

.services-cta__actions :deep(.site-btn) {
  min-width: 11rem;
}

@media (max-width: 639px) {
  .services-chooser {
    margin-left: max(1rem, env(safe-area-inset-left));
    margin-right: max(1rem, env(safe-area-inset-right));
    width: auto;
  }
}

@media (min-width: 640px) {
  .services-board {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.55rem;
  }

  .services-board__cell {
    min-height: 9rem;
  }

  .services-packages__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .services-panel__intro {
    grid-template-columns: minmax(220px, 0.9fr) 1.1fr;
    gap: 1.5rem;
    align-items: center;
    padding: 1.35rem 1.35rem 1.4rem;
  }

  .services-panel__visual {
    aspect-ratio: 4 / 5;
    max-height: 20rem;
  }

  .services-panel__menu {
    padding: 0 1.35rem 0.5rem;
  }
}

@media (min-width: 1024px) {
  .services-packages__grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .services-door {
    min-height: 17rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .panel-fade-enter-active,
  .panel-fade-leave-active {
    transition: none;
  }

  .services-door,
  .services-door__media,
  .services-board__cell {
    transition: none;
  }
}
</style>
