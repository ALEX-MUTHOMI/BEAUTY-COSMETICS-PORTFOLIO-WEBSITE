<template>
  <main class="services-page">
    <header class="services-hero">
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
        <span>{{ SINGLE_DAYS_LABEL }} singles</span>
      </p>
      <nav class="services-paths">
        <a
          href="#full-packages"
          class="services-path services-path--primary"
          @click="scrollToSection('full-packages', $event)"
        >
          <span class="services-path__icon" aria-hidden="true">◆</span>
          <span class="services-path__copy">
            <strong>Package</strong>
            <span>Facial, wax, massage &amp; makeup</span>
          </span>
        </a>
        <a
          href="#single-sessions"
          class="services-path"
          @click="scrollToSection('single-sessions', $event)"
        >
          <span class="services-path__icon" aria-hidden="true">◇</span>
          <span class="services-path__copy">
            <strong>Singles</strong>
            <span>One service</span>
          </span>
        </a>
      </nav>
    </section>

    <section id="full-packages" class="services-packages">
      <header class="services-section-head">
        <p class="label">Packages</p>
        <h2>Complete visits</h2>
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

    <section id="single-sessions" class="services-packages services-packages--singles">
      <header class="services-section-head">
        <p class="label">Singles</p>
        <h2>Choose a treatment</h2>
        <p class="services-section-head__sub">
          {{ SINGLE_DAYS_LABEL }}. Pick a category, then book.
        </p>
      </header>

      <div id="treatments" class="services-picker" aria-label="Treatments and prices">
        <div
          class="services-tabs"
          role="tablist"
          aria-label="Service categories"
        >
          <button
            v-for="category in serviceCategories"
            :id="`tab-${category.id}`"
            :key="category.id"
            type="button"
            role="tab"
            class="services-tab"
            :class="{ 'services-tab--active': activeCategoryId === category.id }"
            :aria-selected="activeCategoryId === category.id"
            :aria-controls="`panel-${category.id}`"
            @click="selectCategory(category.id)"
          >
            <span class="services-tab__icon-wrap" aria-hidden="true">
              <img :src="category.icon" alt="" class="services-tab__icon" width="22" height="22" />
            </span>
            <span class="services-tab__label">{{ category.cardTitle }}</span>
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
              <div class="services-panel__inner">
                <div class="services-panel__intro">
                  <div class="services-panel__visual">
                    <img
                      :src="activeCategory.image"
                      :alt="activeCategory.imageAlt"
                      class="services-panel__photo"
                      loading="lazy"
                      decoding="async"
                      width="400"
                      height="400"
                    />
                    <span class="services-panel__icon-wrap" aria-hidden="true">
                      <img :src="activeCategory.icon" alt="" width="26" height="26" />
                    </span>
                  </div>
                  <div class="services-panel__copy">
                    <p class="label">{{ activeCategory.daysNote }}</p>
                    <h2>{{ activeCategory.name }}</h2>
                    <p class="services-panel__text">{{ activeCategory.intro }}</p>
                    <p class="services-panel__hint">
                      Tap a treatment below to select it, then book your visit.
                    </p>
                  </div>
                </div>

                <div class="services-panel__grid">
                  <ServiceTreatmentCard
                    v-for="(treatment, index) in activeCategory.treatments"
                    :key="treatment.name"
                    :name="treatment.name"
                    :description="treatment.description"
                    :duration="treatment.duration"
                    :price="treatment.price"
                    :highlights="treatment.highlights"
                    :index="index"
                    :variant="activeCategory.id"
                    :selected="selectedTreatmentName === treatment.name"
                    @select="selectTreatment(treatment.name)"
                  />
                </div>

                <div class="services-panel__book" :class="{ 'services-panel__book--ready': selectedTreatmentName }">
                  <p v-if="selectedTreatmentName" class="services-panel__chosen">
                    You selected <strong>{{ selectedTreatmentName }}</strong>
                  </p>
                  <p v-else class="services-panel__chosen services-panel__chosen--muted">
                    Select a treatment above to continue
                  </p>
                  <SiteButton
                    :to="treatmentBookHref"
                    variant="primary"
                    class="services-panel__cta"
                    :class="{ 'services-panel__cta--disabled': !selectedTreatmentName }"
                  >
                    {{
                      selectedTreatmentName
                        ? `Book ${selectedTreatmentName}`
                        : LANDING_PRIMARY_CTA
                    }}
                  </SiteButton>
                </div>
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
          <SiteButton to="/services#full-packages" variant="primary">View packages</SiteButton>
          <SiteButton to="/services#single-sessions" variant="outline">View singles</SiteButton>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  LANDING_PRIMARY_CTA,
  packages,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import {
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
const selectedTreatmentName = ref<string | null>(null)

const activeCategory = computed(
  () => serviceCategories.find((c) => c.id === activeCategoryId.value) ?? serviceCategories[0]!,
)

const treatmentBookHref = computed(() =>
  bookHrefForTreatment(activeCategoryId.value, selectedTreatmentName.value),
)

function selectCategory(id: string) {
  if (!isServiceCategoryId(id) || activeCategoryId.value === id) return
  activeCategoryId.value = id
  selectedTreatmentName.value = null
  if (import.meta.client) {
    window.history.replaceState(null, '', `#${id}`)
  }
}

function selectTreatment(name: string) {
  selectedTreatmentName.value = name
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
    selectedTreatmentName.value = null
    requestAnimationFrame(() => {
      document.getElementById('treatments')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  }
}

function syncFromHash() {
  if (!import.meta.client) return
  applyHash(window.location.hash)
}

function scrollToSection(id: string, event: MouseEvent) {
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
/* Page shell — calm white base, room for fixed mobile book bar */
.services-page {
  background: #fff;
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

/* Hero — light, low-contrast wash */
.services-hero {
  position: relative;
  overflow: hidden;
  padding: 1rem max(1rem, env(safe-area-inset-left)) 0.5rem;
  background: #fff;
}

.services-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 80% 50% at 50% 0%, rgba(222, 150, 141, 0.05), transparent 70%);
}

.services-hero::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.02;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M30 6c-5 11-14 13-14 22a14 14 0 0 0 28 0c0-9-9-11-14-22z' fill='%23de968d'/%3E%3C/svg%3E");
  background-size: 96px;
}

.services-hero__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
  text-align: center;
}

.services-hero h1 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 4.5vw, 2.45rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
}

.services-hero__lead {
  margin: 0;
  font: 400 0.95rem/1.55 var(--font-body);
  color: var(--color-muted);
}

/* One chooser: day caption + path tiles */
.services-chooser {
  width: var(--container);
  margin: 0.35rem auto 0;
  padding: 0.75rem 0.85rem;
  border: 1px solid var(--color-line);
  border-radius: 2px;
  background: #fff;
}

.services-chooser__days {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.25rem 0.4rem;
  margin: 0 0 0.65rem;
  font: 500 0.72rem/1.4 var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-muted);
  text-align: center;
}

.services-chooser__days-sep {
  color: var(--color-line);
}

.services-paths {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
}

@media (max-width: 420px) {
  .services-paths {
    grid-template-columns: 1fr;
  }
}

.services-path {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  min-height: 2.75rem;
  padding: 0.65rem 0.7rem;
  border: 1px solid var(--color-line);
  border-radius: 2px;
  background: #fff;
  text-decoration: none;
  color: inherit;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.15s ease,
    background-color 0.15s ease,
    box-shadow 0.15s ease;
}

@media (hover: hover) {
  .services-path:hover {
    border-color: rgba(222, 150, 141, 0.45);
    background: #fafafa;
    box-shadow: 0 4px 14px rgba(39, 37, 42, 0.05);
    transform: translateY(-1px);
  }
}

.services-path:active {
  background: #f7f7f8;
}

.services-path--primary {
  border-color: rgba(222, 150, 141, 0.35);
  border-left: 3px solid var(--color-rose);
  background: #fff;
  box-shadow: none;
}

.services-path--primary .services-path__icon {
  color: var(--color-rose-dark);
  background: var(--color-rose-soft);
}

@media (hover: hover) {
  .services-path--primary:hover {
    background: #fafafa;
  }
}

.services-path:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-path__icon {
  display: none;
  flex-shrink: 0;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  font-size: 0.85rem;
  color: var(--color-rose-dark);
  background: var(--color-rose-soft);
}

.services-path__copy {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.services-path__copy strong {
  font: 700 0.8rem var(--font-body);
  letter-spacing: 0.03em;
  color: var(--color-ink);
}

.services-path__copy span {
  font: 400 0.72rem/1.35 var(--font-body);
  color: var(--color-muted);
}

/* Package sections — unified neutral sections, no heavy pink blocks */
.services-packages {
  padding: clamp(1.75rem, 4vh, 2.75rem) max(1rem, env(safe-area-inset-left));
  margin-top: 0.5rem;
  background: #fff;
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-packages--singles {
  background: #fafafa;
  border-top: 1px solid var(--color-line);
}

.services-packages--singles .services-picker {
  width: var(--container);
  margin: 0.85rem auto 0;
  padding: 0 0 0.5rem;
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-packages-link {
  margin: 1.25rem 0 0;
  text-align: center;
  font: 500 0.88rem/1.5 var(--font-body);
  color: var(--color-muted);
}

.services-packages-link a {
  font-weight: 700;
  color: var(--color-rose-dark);
  text-decoration: underline;
  text-underline-offset: 2px;
}

.services-packages-link a:hover {
  color: var(--color-rose);
}

.services-packages-link a:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-section-head {
  width: var(--container);
  margin: 0 auto 0.35rem;
  max-width: 40rem;
  text-align: center;
}

.services-section-head h2 {
  margin: 0 0 0.4rem;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.2vw, 1.9rem);
  font-weight: 400;
  line-height: 1.25;
  color: var(--color-ink);
}

.services-section-head__sub {
  margin: 0;
  font: 400 0.9rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.services-packages__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  width: var(--container);
  margin: 0 auto;
  padding-top: 0.85rem;
  align-items: stretch;
}

.services-packages__grid > * {
  min-width: 0;
}

.services-packages__grid--singles {
  grid-template-columns: 1fr;
}

/* Treatment picker */
.services-picker {
  width: var(--container);
  margin: 0 auto;
  padding: 0 0 calc(2rem + env(safe-area-inset-bottom, 0px));
  scroll-margin-top: 5.5rem;
}

.services-tabs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.services-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  min-height: 3.25rem;
  padding: 0.7rem 0.45rem;
  border: 1px solid var(--color-line);
  border-radius: 2px;
  background: #fff;
  cursor: pointer;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.12s ease,
    background-color 0.12s ease,
    box-shadow 0.12s ease,
    color 0.12s ease;
}

@media (hover: hover) {
  .services-tab:hover:not(.services-tab--active) {
    border-color: rgba(222, 150, 141, 0.35);
    background: #fafafa;
  }
}

.services-tab:active:not(.services-tab--active) {
  background: #f3f3f4;
}

.services-tab:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-tab--active {
  border-color: var(--color-rose);
  background: var(--color-rose-soft);
  box-shadow: none;
  color: var(--color-ink);
}

.services-tab__icon-wrap {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-rose-soft);
}

.services-tab--active .services-tab__icon-wrap {
  background: rgba(222, 150, 141, 0.2);
}

.services-tab__icon {
  object-fit: contain;
  filter: brightness(0) saturate(100%) invert(72%) sepia(18%) saturate(749%) hue-rotate(319deg) brightness(92%) contrast(89%);
}

.services-tab--active .services-tab__icon {
  filter: brightness(0) saturate(100%) invert(72%) sepia(18%) saturate(749%) hue-rotate(319deg) brightness(92%) contrast(89%);
}

.services-tab__label {
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-align: center;
  line-height: 1.25;
}

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
  border-radius: 2px;
  border: 1px solid var(--color-line);
  overflow: hidden;
  background: #fff;
}

.services-panel--facials,
.services-panel--massage,
.services-panel--waxing,
.services-panel--makeup {
  background: #fff;
}

.services-panel__inner {
  padding: 1.5rem 1rem 1.25rem;
}

.services-panel__intro {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(39, 37, 42, 0.08);
}

.services-panel__visual {
  position: relative;
  width: min(160px, 42vw);
  margin: 0 auto;
  aspect-ratio: 1;
}

.services-panel__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 10px 32px rgba(39, 37, 42, 0.12);
}

.services-panel__icon-wrap {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-rose);
  border: 3px solid #fff;
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.45);
}

.services-panel__icon-wrap img {
  filter: brightness(0) invert(1);
}

.services-panel__copy h2 {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3.5vw, 2rem);
  font-weight: 400;
  line-height: 1.25;
  text-align: center;
  color: var(--color-ink);
}

.services-panel__text {
  margin: 0 0 0.65rem;
  font: 400 0.95rem/1.7 var(--font-body);
  color: var(--color-muted);
  text-align: center;
}

.services-panel__hint {
  margin: 0;
  font: 600 0.8rem var(--font-body);
  color: var(--color-rose-dark);
  text-align: center;
}

.services-panel__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

.services-panel__book {
  margin-top: 1.5rem;
  padding: 1.15rem 1rem;
  border-radius: 2px;
  background: #fafafa;
  border: 1px dashed var(--color-line);
  text-align: center;
  transition: border-color 0.2s, background-color 0.2s;
}

.services-panel__book--ready {
  background: #fff;
  border: 1px solid rgba(222, 150, 141, 0.35);
  box-shadow: 0 4px 16px rgba(39, 37, 42, 0.05);
}

.services-panel__book :deep(.site-btn) {
  width: 100%;
  max-width: 20rem;
  min-height: 3rem;
}

.services-panel__chosen {
  margin: 0 0 1rem;
  font: 400 0.95rem var(--font-body);
  color: var(--color-ink);
}

.services-panel__chosen--muted {
  color: var(--color-muted);
}

.services-panel__chosen strong {
  font-weight: 700;
  color: var(--color-rose-dark);
}

.services-panel__cta--disabled {
  opacity: 0.45;
  pointer-events: none;
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

@media (max-width: 767px) {
  .services-hero {
    padding: 0.85rem max(1rem, env(safe-area-inset-left)) 0.35rem;
  }

  .services-hero h1 {
    font-size: clamp(1.5rem, 6.5vw, 1.85rem);
  }

  .services-chooser {
    margin-top: 0.25rem;
    margin-left: max(1rem, env(safe-area-inset-left));
    margin-right: max(1rem, env(safe-area-inset-right));
    width: auto;
    max-width: none;
  }

  .services-packages {
    margin-top: 1.25rem;
    padding-top: 1.75rem;
  }

  .services-packages__grid {
    gap: 1rem;
  }

  .services-panel__inner {
    padding: 1.25rem 0.85rem 1rem;
  }

  .services-panel__visual {
    width: min(140px, 38vw);
  }
}

@media (min-width: 640px) {
  .services-hero {
    padding: clamp(1.25rem, 3.5vh, 2rem) max(1rem, env(safe-area-inset-left)) 0.75rem;
  }

  .services-chooser {
    margin-top: 0.65rem;
    padding: 1rem 1.1rem;
  }

  .services-chooser__days {
    margin-bottom: 0.85rem;
    font-size: 0.78rem;
  }

  .services-paths {
    gap: 0.75rem;
  }

  .services-path {
    min-height: 3.25rem;
    padding: 0.9rem 1rem;
    gap: 0.85rem;
  }

  .services-path__icon {
    display: grid;
  }

  .services-path__copy strong {
    font-size: 0.88rem;
  }

  .services-path__copy span {
    font-size: 0.8rem;
    line-height: 1.4;
  }

  .services-packages {
    margin-top: 1.5rem;
  }

  .services-tabs {
    grid-template-columns: repeat(4, 1fr);
  }

  .services-panel__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .services-packages__grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .services-packages__grid--singles {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 768px) {
  .services-panel__inner {
    padding: 2rem 1.5rem 1.5rem;
  }

  .services-panel__intro {
    grid-template-columns: auto 1fr;
    gap: 2rem;
  }

  .services-panel__visual {
    margin: 0;
    width: 180px;
  }

  .services-panel__copy h2,
  .services-panel__text,
  .services-panel__hint {
    text-align: left;
  }
}

@media (min-width: 1024px) {
  .services-panel__grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .services-packages__grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .services-packages__grid--singles {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .panel-fade-enter-active,
  .panel-fade-leave-active {
    transition: none;
  }
}
</style>
