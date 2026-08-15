<template>
  <div>
    <SiteLoader
      variant="services"
      :assets="[
        '/images/logo-mark.png',
        '/images/flower.png',
        '/images/icon-facial.png',
        '/images/icon-massage.png',
        '/images/icon-waxing.png',
        '/images/icon-makeup.png',
      ]"
    />
    <main class="services-page">
      <header class="services-hero">
        <img
          src="/images/flower.png"
          alt=""
          class="services-hero__bloom services-hero__bloom--tl"
          aria-hidden="true"
          width="120"
          height="120"
          decoding="async"
        />
        <img
          src="/images/flower.png"
          alt=""
          class="services-hero__bloom services-hero__bloom--br"
          aria-hidden="true"
          width="140"
          height="140"
          decoding="async"
        />
        <div class="services-hero__inner">
          <div class="title-lockup">
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--left"
              width="44"
              height="44"
              aria-hidden="true"
            />
            <h1>{{ pageIntro.title }}</h1>
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--right"
              width="44"
              height="44"
              aria-hidden="true"
            />
          </div>
        </div>
      </header>

      <section class="services-chooser" aria-label="Choose how you want to book">
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--chooser-l"
          aria-hidden="true"
          width="100"
          height="100"
          loading="lazy"
          decoding="async"
        />
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--chooser-r"
          aria-hidden="true"
          width="110"
          height="110"
          loading="lazy"
          decoding="async"
        />
        <div class="services-chooser__inner">
          <nav class="services-doors" aria-label="Visit type">
            <a
              href="#full-packages"
              class="services-door services-door--packages"
              @click="scrollToSection('full-packages', $event)"
            >
              <img
                src="/images/flower.png"
                alt=""
                class="services-door__flower services-door__flower--main"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
                width="100"
                height="100"
              />
              <img
                src="/images/flower.png"
                alt=""
                class="services-door__flower services-door__flower--accent"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
                width="56"
                height="56"
              />
              <span class="services-door__body">
                <span class="services-door__num" aria-hidden="true">01</span>
                <span class="services-door__title">Packages</span>
                <span class="services-door__sub">Full visit · Tue &amp; Wed</span>
                <span class="services-door__cta">See packages</span>
              </span>
            </a>
            <a
              href="#single-sessions"
              class="services-door services-door--treatments"
              @click="scrollToSection('single-sessions', $event)"
            >
              <img
                src="/images/flower.png"
                alt=""
                class="services-door__flower services-door__flower--main"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
                width="100"
                height="100"
              />
              <img
                src="/images/flower.png"
                alt=""
                class="services-door__flower services-door__flower--accent"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
                width="56"
                height="56"
              />
              <span class="services-door__body">
                <span class="services-door__num" aria-hidden="true">02</span>
                <span class="services-door__title">Treatments</span>
                <span class="services-door__sub">One service · {{ SINGLE_DAYS_LABEL }}</span>
                <span class="services-door__cta">Browse &amp; book</span>
              </span>
            </a>
          </nav>
        </div>
      </section>

      <section id="full-packages" class="services-packages">
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--pkg-tl"
          aria-hidden="true"
          width="120"
          height="120"
          loading="lazy"
          decoding="async"
        />
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--pkg-br"
          aria-hidden="true"
          width="140"
          height="140"
          loading="lazy"
          decoding="async"
        />
        <header class="services-section-head">
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
            One booking. Full glow. Tue &amp; Wed only.
          </p>
        </header>
        <div class="services-packages__scroll">
          <div class="services-packages__grid">
            <MellisPackageCard
              v-for="(pkg, index) in packages"
              :key="pkg.name"
              :name="pkg.name"
              :text="pkg.text"
              :price="pkg.price"
              hide-price
              :includes="pkg.includes"
              :featured="pkg.featured"
              :card-theme="index % 2 === 1 ? 'light' : 'dark'"
              :badge="pkg.badge"
              :days-label="pkg.daysLabel"
              :cta-label="pkg.ctaLabel || 'Book this package'"
              :cta-to="bookHrefForPackageName(pkg.name)"
            />
          </div>
        </div>
      </section>

      <section id="single-sessions" class="services-treatments">
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--treat-l"
          aria-hidden="true"
          width="110"
          height="110"
          loading="lazy"
          decoding="async"
        />
        <img
          src="/images/flower.png"
          alt=""
          class="services-bloom services-bloom--treat-r"
          aria-hidden="true"
          width="130"
          height="130"
          loading="lazy"
          decoding="async"
        />
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
            Pick a category, then book the exact service.
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
              :class="{
                'services-board__cell--active': activeCategoryId === category.id,
                'services-board__cell--light': index % 2 === 1,
              }"
              :aria-selected="activeCategoryId === category.id"
              :aria-controls="`panel-${category.id}`"
              @click="selectCategory(category.id)"
            >
              <img
                src="/images/flower.png"
                alt=""
                class="services-board__flower"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
                width="48"
                height="48"
              />
              <span class="services-board__icon-wrap" aria-hidden="true">
                <img
                  :src="category.icon"
                  alt=""
                  class="services-board__icon"
                  loading="lazy"
                  decoding="async"
                  width="48"
                  height="48"
                />
              </span>
              <span class="services-board__copy">
                <span class="services-board__num" aria-hidden="true">{{ padIndex(index) }}</span>
                <span class="services-board__title">{{ category.cardTitle }}</span>
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
                  <img
                    :src="activeCategory.icon"
                    alt=""
                    class="services-panel__icon"
                    loading="lazy"
                    decoding="async"
                    width="40"
                    height="40"
                    aria-hidden="true"
                  />
                  <div class="services-panel__copy">
                    <p class="label">{{ activeCategory.daysNote }}</p>
                    <h2>{{ activeCategory.name }}</h2>
                    <p class="services-panel__hint">Tap Book on any row to reserve your slot.</p>
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
          <img
            src="/images/flower.png"
            alt=""
            class="services-cta__flower"
            aria-hidden="true"
            loading="lazy"
            decoding="async"
            width="72"
            height="72"
          />
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  packages,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import {
  SERVICES_CITATION_LINE,
  SERVICES_PAGE_INTRO,
  serviceCategories,
} from '@/landing/servicesContent'
import { buildServicesOfferCatalogJsonLd } from '@/landing/agentSeo'
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
  robots: 'index, follow',
})

useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}/services` }],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify(buildServicesOfferCatalogJsonLd(siteUrl)),
    },
  ],
})
</script>

<style scoped>
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

/* Hero — question only */
.services-hero {
  position: relative;
  overflow: hidden;
  padding: clamp(1.75rem, 5vh, 3rem) 1rem 0.85rem;
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(222, 150, 141, 0.12), transparent 68%),
    var(--color-paper, #e5e1dc);
  text-align: center;
}

.services-hero__bloom {
  position: absolute;
  pointer-events: none;
  opacity: 0.28;
  filter: saturate(1.25);
}

.services-hero__bloom--tl {
  top: -1.5rem;
  left: -1rem;
  width: min(140px, 30vw);
}

.services-hero__bloom--br {
  right: -1.25rem;
  bottom: -2rem;
  width: min(160px, 34vw);
  transform: rotate(160deg);
}

.services-hero__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  max-width: 40rem;
}

.services-hero__cite {
  margin: 1rem auto 0;
  max-width: 42rem;
  font: 400 0.98rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.services-hero h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 6.5vw, 2.75rem);
  font-weight: 400;
  line-height: 1.15;
  color: var(--color-ink);
}

/* Soft flower accents in white space */
.services-bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.2;
  filter: saturate(1.3) brightness(1.02);
}

.services-bloom--chooser-l {
  left: max(0.25rem, env(safe-area-inset-left));
  top: 10%;
  width: min(88px, 18vw);
  transform: rotate(-20deg);
}

.services-bloom--chooser-r {
  right: max(0.25rem, env(safe-area-inset-right));
  bottom: 5%;
  width: min(96px, 20vw);
  transform: rotate(25deg);
}

.services-bloom--pkg-tl {
  top: 0.5rem;
  left: max(0.5rem, env(safe-area-inset-left));
  width: min(110px, 22vw);
  opacity: 0.22;
}

.services-bloom--pkg-br {
  right: max(0.5rem, env(safe-area-inset-right));
  bottom: 1rem;
  width: min(130px, 26vw);
  transform: rotate(150deg);
  opacity: 0.2;
}

.services-bloom--treat-l {
  left: max(0.35rem, env(safe-area-inset-left));
  top: 2.5rem;
  width: min(100px, 20vw);
  transform: rotate(-15deg);
}

.services-bloom--treat-r {
  right: max(0.35rem, env(safe-area-inset-right));
  top: 1rem;
  width: min(120px, 24vw);
  transform: rotate(40deg);
}

/* Path cards — horizontal scroll on mobile */
.services-chooser {
  position: relative;
  margin: 0;
  padding: 0.5rem 0 1.25rem;
  background: var(--color-paper, #e5e1dc);
  overflow: hidden;
}

.services-chooser__inner {
  position: relative;
  z-index: 1;
  width: 100%;
  margin: 0 auto;
  padding: 0;
}

.services-doors {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  width: 100%;
  padding: 0.15rem 1rem 0.35rem;
  padding-left: max(1rem, env(safe-area-inset-left));
  padding-right: max(1rem, env(safe-area-inset-right));
}

@media (min-width: 520px) {
  .services-doors {
    grid-template-columns: 1fr 1fr;
    gap: 0.9rem;
  }
}

.services-doors::-webkit-scrollbar {
  display: none;
}

.services-door {
  position: relative;
  width: 100%;
  min-width: 0;
  display: block;
  min-height: 6.5rem;
  overflow: hidden;
  text-decoration: none;
  color: #f7f0eb;
  background:
    radial-gradient(ellipse 75% 60% at 100% 0%, rgba(222, 150, 141, 0.2), transparent 55%),
    linear-gradient(155deg, #322a2b 0%, #262122 52%, #1e1a1b 100%);
  border: 1px solid rgba(222, 150, 141, 0.28);
  border-radius: 10px;
  box-shadow:
    0 8px 20px rgba(23, 21, 22, 0.08),
    0 1px 0 rgba(255, 255, 255, 0.12) inset;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition:
    transform 0.3s var(--ease-story, ease),
    box-shadow 0.3s var(--ease-story, ease);
}

/* Ivory Spa Porcelain Card — blends 100% harmoniously with Black Obsidian card */
.services-door--treatments {
  color: #1f1a1b;
  background:
    radial-gradient(ellipse 75% 60% at 0% 0%, rgba(176, 122, 113, 0.16), transparent 55%),
    linear-gradient(160deg, #f7f1eb 0%, #ebe3db 52%, #dfd6cd 100%);
  border: 1px solid rgba(176, 122, 113, 0.38);
  border-radius: 10px;
  box-shadow:
    0 8px 20px rgba(23, 21, 22, 0.06),
    0 1px 0 rgba(255, 255, 255, 0.9) inset;
}

.services-door--treatments .services-door__num {
  color: #b56b62;
  font-weight: 700;
}

.services-door--treatments .services-door__title {
  color: #1f1a1b;
  word-break: break-word;
}

.services-door--treatments .services-door__sub {
  color: #6b605c;
}

.services-door--treatments .services-door__cta {
  background: #1f1a1b;
  color: #fff;
  border-color: #1f1a1b;
}

@media (min-width: 640px) {
  .services-chooser__inner {
    width: var(--container);
    padding: 0 max(1rem, env(safe-area-inset-left));
  }

  .services-doors {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    overflow: visible;
    padding: 0;
  }

  .services-door {
    flex: none;
    min-height: 7.5rem;
  }
}

@media (hover: hover) {
  .services-door:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(23, 21, 22, 0.12);
  }

  .services-door:hover .services-door__cta {
    background: var(--color-rose);
    color: #fff;
  }
}

.services-door:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

.services-door__flower {
  position: absolute;
  pointer-events: none;
  z-index: 0;
  filter: saturate(1.15) brightness(1.02);
}

.services-door__flower--main {
  right: 0.35rem;
  bottom: 0.25rem;
  width: min(64px, 24%);
  opacity: 0.24;
}

.services-door__flower--accent {
  top: 0.4rem;
  right: 0.5rem;
  width: min(36px, 14%);
  opacity: 0.18;
  transform: rotate(22deg);
}

.services-door__body {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.15rem;
  height: 100%;
  min-height: inherit;
  padding: 0.85rem 1rem;
}

.services-door__num {
  font: 700 0.65rem/1 var(--font-body);
  letter-spacing: 0.16em;
  color: #f0b8ac;
}

.services-door__title {
  font-family: var(--font-script);
  font-size: clamp(1.4rem, 4vw, 1.85rem);
  line-height: 1.1;
  color: #fff;
}

.services-door__sub {
  font: 500 0.78rem/1.35 var(--font-body);
  letter-spacing: 0.01em;
  color: rgba(255, 248, 244, 0.78);
}

.services-door__cta {
  display: inline-flex;
  align-items: center;
  align-self: flex-start;
  margin-top: 0.45rem;
  min-height: 2rem;
  padding: 0.35rem 0.75rem;
  font: 700 0.64rem/1 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #fff;
  background: rgba(222, 150, 141, 0.92);
  border-radius: 4px;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

/* Packages */
.services-packages {
  position: relative;
  overflow: hidden;
  padding: clamp(1.85rem, 4.5vh, 2.85rem) 0;
  margin-top: 0;
  background:
    radial-gradient(ellipse 60% 40% at 50% 0%, rgba(176, 122, 113, 0.12), transparent 70%),
    var(--color-paper, #e5e1dc);
  border-top: 1px solid var(--color-line);
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-section-head {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto 0.35rem;
  max-width: 40rem;
  padding: 0 max(1rem, env(safe-area-inset-left));
  text-align: center;
}

.services-section-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.2vw, 1.95rem);
  font-weight: 400;
  line-height: 1.25;
  color: var(--color-ink);
}

.services-section-head__sub {
  margin: 0.55rem 0 0;
  font: 400 0.9rem/1.55 var(--font-body);
  color: var(--color-muted);
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
  opacity: 0.85;
  filter: saturate(1.2) brightness(0.95);
}

.services-packages__scroll {
  position: relative;
  z-index: 1;
  padding: 1.15rem 0 0.5rem;
}

.services-packages__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  width: 100%;
  max-width: 24rem;
  margin: 0 auto;
  padding: 0 max(1rem, env(safe-area-inset-left));
  padding-right: max(1rem, env(safe-area-inset-right));
}

.services-packages__grid > * {
  width: 100%;
  max-width: 100%;
  flex: none;
  display: flex;
}

@media (min-width: 768px) {
  .services-packages {
    padding-left: max(1rem, env(safe-area-inset-left));
    padding-right: max(1rem, env(safe-area-inset-right));
  }

  .services-packages__grid {
    grid-template-columns: repeat(3, 1fr);
    align-items: stretch;
    gap: clamp(1.25rem, 2.2vw, 2rem);
    max-width: var(--container, 76rem);
    width: 100%;
    margin: 0 auto;
    padding: 0 clamp(1rem, 2.5vw, 2rem);
  }
}

/* Treatments — icon cards + horizontal scroll */
.services-treatments {
  position: relative;
  overflow: hidden;
  padding: clamp(1.85rem, 4.5vh, 2.85rem) 0;
  background: var(--color-paper, #e5e1dc);
  border-top: 1px solid var(--color-line);
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

.services-picker {
  position: relative;
  z-index: 1;
  width: 100%;
  margin: 1rem auto 0;
  padding: 0 0 0.5rem;
  scroll-margin-top: calc(var(--header-height) + 0.5rem);
}

@media (min-width: 640px) {
  .services-treatments {
    padding-left: max(1rem, env(safe-area-inset-left));
    padding-right: max(1rem, env(safe-area-inset-right));
  }

  .services-picker {
    width: 100%;
    max-width: var(--container, 76rem);
    margin: 1rem auto 0;
  }
}

.services-packages-link {
  margin: 1.5rem 1rem 0;
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

.services-packages-link a:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-board {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.65rem;
  width: 100%;
  max-width: 100%;
  margin: 0 auto 1.25rem;
  padding: 0 max(1rem, env(safe-area-inset-left));
  padding-right: max(1rem, env(safe-area-inset-right));
}

.services-board__cell {
  position: relative;
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
  min-height: 3.25rem;
  padding: 0.45rem 0.75rem;
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  background: var(--color-surface-raised, #ebe7e3);
  color: var(--color-ink, #252223);
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(23, 21, 22, 0.04);
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.18s ease,
    background 0.18s ease,
    transform 0.18s ease;
}

.services-board__cell:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-board__cell--active {
  background: var(--color-card-dark, #1e191b);
  color: #fff;
  border-color: var(--color-rose);
  box-shadow: 0 6px 18px rgba(23, 21, 22, 0.18);
}

.services-board__icon-wrap {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: rgba(176, 122, 113, 0.12);
}

.services-board__cell--active .services-board__icon-wrap {
  background: rgba(240, 184, 172, 0.2);
}

.services-board__icon {
  width: 1.1rem;
  height: 1.1rem;
  object-fit: contain;
}

.services-board__copy {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.services-board__num {
  font: 700 0.65rem/1 var(--font-body);
  letter-spacing: 0.1em;
  color: #b56b62;
  flex-shrink: 0;
}

.services-board__cell--active .services-board__num {
  color: #f0b8ac;
}

.services-board__title {
  margin: 0;
  font: 700 0.78rem/1.2 var(--font-body);
  letter-spacing: 0.03em;
  text-transform: uppercase;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (min-width: 640px) {
  .services-board {
    grid-template-columns: repeat(4, 1fr);
    gap: clamp(0.75rem, 1.5vw, 1.25rem);
    max-width: var(--container, 76rem);
    padding: 0 clamp(1rem, 2.5vw, 2rem);
    margin-bottom: 1.5rem;
  }

  .services-board__cell {
    justify-content: center;
    min-height: 3.5rem;
    padding: 0.55rem 1rem;
  }
}

.services-panel-wrap {
  position: relative;
  min-height: 10rem;
  width: 100%;
  max-width: var(--container, 76rem);
  margin: 0 auto;
  padding: 0 max(1rem, env(safe-area-inset-left));
  padding-right: max(1rem, env(safe-area-inset-right));
}

@media (min-width: 640px) {
  .services-panel-wrap {
    padding: 0 clamp(1rem, 2.5vw, 2rem);
  }
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
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(222, 150, 141, 0.22);
  background:
    radial-gradient(ellipse 65% 50% at 100% 0%, rgba(222, 150, 141, 0.16), transparent 55%),
    linear-gradient(165deg, #322a2b 0%, #262122 52%, #1e1a1b 100%);
  box-shadow: 0 10px 28px rgba(23, 21, 22, 0.1);
  border-radius: 12px;
}

.services-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.08;
  background-image: url('/images/flower.png');
  background-size: 5.5rem;
  background-repeat: repeat;
  filter: saturate(1.2);
  mix-blend-mode: soft-light;
}

.services-panel__intro {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.95rem;
  border-bottom: 1px solid rgba(248, 242, 238, 0.12);
}

.services-panel__icon {
  flex: 0 0 auto;
  width: 1.85rem;
  height: 1.85rem;
  object-fit: contain;
  filter: brightness(0) invert(1) opacity(0.9);
}

.services-panel__copy {
  flex: 1 1 auto;
  min-width: 0;
}

.services-panel__copy .label {
  color: #f0b8ac;
  margin-bottom: 0.1rem;
}

.services-panel__copy h2 {
  margin: 0 0 0.45rem;
  font-family: var(--font-display);
  font-size: clamp(1.55rem, 3.5vw, 2.05rem);
  font-weight: 500;
  line-height: 1.2;
  color: #fff;
}

.services-panel__hint {
  margin: 0;
  font: 600 0.82rem/1.4 var(--font-body);
  color: #f0b8ac;
}

.services-panel__menu {
  position: relative;
  z-index: 1;
  padding: 0 1rem 0.35rem;
}

@media (min-width: 768px) {
  .services-panel__intro {
    padding: 1.35rem 1.35rem 1.15rem;
  }

  .services-panel__menu {
    padding: 0 1.35rem 0.5rem;
  }
}

.services-cta {
  position: relative;
  overflow: hidden;
  padding: clamp(2.5rem, 6vh, 4rem) 1rem;
  background: #171516;
  color: #fff;
  text-align: center;
}

.services-cta__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  max-width: 36rem;
}

.services-cta__flower {
  width: 56px;
  margin-bottom: 0.85rem;
  opacity: 0.55;
  filter: saturate(1.2);
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

@media (min-width: 1024px) {
  .services-door {
    min-height: 16.5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .panel-fade-enter-active,
  .panel-fade-leave-active {
    transition: none;
  }

  .services-door,
  .services-board__cell {
    transition: none;
  }
}
</style>
