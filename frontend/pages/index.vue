<template>
  <SiteLoader />
  <main class="home">
    <!-- Hero — Mellis-style fade gallery (Parisienne title + Manrope eyebrow + rose CTA) -->
    <section
      class="hero"
      data-home-hero
      role="region"
      aria-label="Shee studio gallery"
      :data-hero-service="currentHero.service"
      :style="{
        '--hero-crossfade-ms': `${HERO_CROSSFADE_MS}ms`,
        '--hero-copy-fade-ms': `${HERO_COPY_FADE_MS}ms`,
      }"
    >
      <div class="hero__track" aria-hidden="true">
        <article
          v-for="(slide, index) in heroSlides"
          :key="slide.service"
          class="hero__slide"
          :class="{ 'hero__slide--active': activeSlide === index }"
          :data-service="slide.service"
        >
          <picture v-if="mountedHeroSlides.has(index)">
            <img
              :src="slide.image"
              :srcset="slide.srcset"
              :sizes="slide.sizes"
              :alt="slide.alt"
              class="hero__bg"
              :style="{ objectPosition: slide.objectPosition }"
              :loading="index === 0 ? 'eager' : 'lazy'"
              :fetchpriority="index === 0 ? 'high' : 'auto'"
              decoding="async"
              :width="slide.width"
              :height="slide.height"
            />
          </picture>
        </article>
      </div>
      <div class="hero__overlay" aria-hidden="true" />
      <div class="hero__content" aria-live="polite">
        <!-- Single copy node — no Transition leave/enter stack (prevents ghosted titles) -->
        <div :key="currentHero.service" class="hero__copy">
          <p class="hero__eyebrow">{{ currentHero.eyebrow }}</p>
          <HeroHandwriteTitle :text="currentHero.headline" class="hero__title" />
          <p class="hero__price">{{ LANDING_PRICE_ANCHOR }}</p>
          <SiteButton :to="heroCta.to" variant="primary" class="hero__cta" @click="onHeroBook">
            {{ heroCta.label }}
          </SiteButton>
        </div>
      </div>
      <div class="hero__dots" role="tablist" aria-label="Gallery slides">
        <button
          v-for="(slide, index) in heroSlides"
          :key="`dot-${slide.service}`"
          type="button"
          class="hero__dot"
          :class="{ 'hero__dot--active': activeSlide === index }"
          role="tab"
          :aria-selected="activeSlide === index"
          :aria-label="slide.headline"
          @click="goToHeroSlide(index)"
        />
      </div>
      <!-- Soft wave seam into paper — structure, not ash fog -->
      <svg class="hero__wave" viewBox="0 0 1440 72" preserveAspectRatio="none" aria-hidden="true">
        <path
          fill="var(--color-paper)"
          d="M0,32 C240,72 480,0 720,28 C960,56 1200,8 1440,36 L1440,72 L0,72 Z"
        />
      </svg>
    </section>

    <!-- Welcome — short story only; booking paths come after how-it-works -->
    <section id="welcome" class="welcome home-section">
      <div class="welcome__inner">
        <ScrollReveal variant="fade" :delay="40">
          <div class="welcome__media-wrap">
            <div class="welcome__media">
              <div class="welcome__mirror" aria-hidden="true">
                <img src="/images/welcome.jpg" alt="Spa treatment room with candles and warm lighting" class="welcome__photo" loading="lazy" decoding="async" width="800" height="800" />
              </div>
              <img src="/images/flower.png" alt="" class="welcome__flower" aria-hidden="true" loading="lazy" decoding="async" width="100" height="100" />
            </div>
          </div>
        </ScrollReveal>
        <ScrollReveal variant="up" :delay="120">
          <div class="welcome__copy">
            <p class="label">{{ LANDING_LOCATION_LABEL }}</p>
            <h2>Your hour to unwind</h2>
            <p class="welcome__text">
              Clean rooms, soft light, and therapists who take their time.
            </p>
            <SiteButton :to="primaryBookHref()" variant="primary" class="welcome__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
          </div>
        </ScrollReveal>
      </div>
    </section>

    <!-- Our work — Pinterest masonry; primary proof for new clients -->
    <section id="our-work" class="work home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <h2>Clients by Shee</h2>
        </header>
      </ScrollReveal>
      <div class="work__masonry" aria-label="Shee client and studio work">
        <button
          v-for="(img, index) in workImages"
          :key="img.id"
          type="button"
          class="work__tile"
          :class="`work__tile--${img.shape}`"
          :aria-label="img.alt"
          @click="openWorkLightbox(img)"
        >
          <img
            :src="img.src"
            :alt="img.alt"
            class="work__photo"
            loading="lazy"
            decoding="async"
            :width="img.width"
            :height="img.height"
            :fetchpriority="index < 2 ? 'low' : 'auto'"
          />
        </button>
      </div>
      <ScrollReveal variant="fade" :delay="80">
        <p class="work__footer">
          <a
            :href="LANDING_INSTAGRAM_URL"
            class="home-services-link"
            target="_blank"
            rel="noopener noreferrer"
          >
            More on Instagram
          </a>
        </p>
      </ScrollReveal>
    </section>

    <!-- Treatments — Mellis height (~54vh / 120px pad) + static bg + Shee board -->
    <section id="services" class="offer home-section">
      <div class="offer__bg" aria-hidden="true">
        <div class="offer__fixed">
          <img
            src="/images/hero-massage.jpg"
            alt=""
            class="offer__photo"
            width="1600"
            height="1067"
            loading="lazy"
            decoding="async"
            fetchpriority="low"
          />
          <div class="offer__veil" />
        </div>
      </div>
      <!-- Sticky chapter: photo holds while you scroll through the runway -->
      <div class="offer__chapter">
        <div class="offer__inner">
          <header class="offer__head">
            <div class="offer__title-lockup">
              <img
                src="/images/flower.png"
                alt=""
                class="offer__title-flower offer__title-flower--left"
                width="72"
                height="72"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
              />
              <h2 id="offer-heading">What we offer</h2>
              <img
                src="/images/flower.png"
                alt=""
                class="offer__title-flower offer__title-flower--right"
                width="72"
                height="72"
                aria-hidden="true"
                loading="lazy"
                decoding="async"
              />
            </div>
          </header>

          <ul class="offer__board" aria-label="Core treatments">
            <li v-for="(item, index) in offerShowcase" :key="item.label">
              <ScrollReveal variant="up" :delay="60 + index * 70">
                <NuxtLink :to="item.to" class="offer__cell">
                  <span class="offer__index" aria-hidden="true">{{ item.index }}</span>
                  <span class="offer__name">{{ item.label }}</span>
                  <span class="offer__detail">{{ item.perk }}</span>
                  <span class="offer__go" aria-hidden="true">Explore →</span>
                </NuxtLink>
              </ScrollReveal>
            </li>
          </ul>

          <ScrollReveal variant="up" :delay="220">
            <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="offer__cta">
              <span class="offer__cta-copy">
                <span class="offer__cta-label">Tue &amp; Wed only</span>
                <span class="offer__cta-title">One booking. Full glow.</span>
                <span class="offer__cta-meta">Facial, wax, massage &amp; makeup · from KES 7,000</span>
              </span>
              <span class="offer__cta-action">
                View packages
                <span class="offer__cta-arrow" aria-hidden="true">→</span>
              </span>
            </NuxtLink>
          </ScrollReveal>
        </div>
      </div>
    </section>

    <!-- How it works — book → pay → visit (image-free, one layout all breakpoints) -->
    <section class="steps home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <h2>How booking works</h2>
        </header>
      </ScrollReveal>
      <ScrollReveal variant="up" :delay="120">
        <ol class="steps__compact" aria-label="Booking steps">
          <li v-for="step in flowSteps" :key="step.title">
            <span class="steps__compact-num" aria-hidden="true">{{ step.num }}</span>
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.text }}</p>
            </div>
          </li>
        </ol>
      </ScrollReveal>
    </section>

    <!-- Book a visit — atmospheric path through doors; packages stage follows -->
    <section id="visit-path" class="book-visit home-section">
      <div class="book-visit__path">
        <div class="book-visit__atmosphere" aria-hidden="true">
          <img
            src="/images/more-bg.jpg"
            alt=""
            class="book-visit__bg"
            width="1600"
            height="1067"
            loading="lazy"
            decoding="async"
          />
          <span class="book-visit__veil" />
        </div>

        <div class="book-visit__path-inner">
          <ScrollReveal variant="up">
            <header class="book-visit__head">
              <h2>How would you like to visit?</h2>
            </header>
          </ScrollReveal>

          <div class="book-visit__doors">
          <ScrollReveal variant="up" :delay="80">
            <NuxtLink
              :to="SERVICES_ROUTES.fullPackages"
              class="visit-card"
              :class="{ 'visit-card--focus': visitFocus === 'packages' }"
            >
              <img
                src="/images/stock-makeup-glam.jpg"
                alt=""
                class="visit-card__media visit-card__media--mono"
                width="1200"
                height="1600"
                loading="lazy"
                decoding="async"
              />
              <span class="visit-card__mist" aria-hidden="true" />
              <span
                class="visit-card__badge"
                :class="{ 'visit-card__badge--today': visitFocus === 'packages' }"
              >
                <span class="visit-card__badge-line">{{ visitFocus === 'packages' ? 'Open' : 'Tue &' }}</span>
                <span class="visit-card__badge-line">{{ visitFocus === 'packages' ? 'today' : 'Wed' }}</span>
              </span>
              <span class="visit-card__body">
                <h3 class="visit-card__title">Full packages</h3>
                <span class="visit-card__text">Facial, wax, massage &amp; makeup — one booking.</span>
                <span class="visit-card__meta">From KES 7,000</span>
                <span class="visit-card__cta">Book now</span>
              </span>
              <img
                src="/images/flower.png"
                alt=""
                class="visit-card__flower"
                width="140"
                height="140"
                loading="lazy"
                decoding="async"
                aria-hidden="true"
              />
            </NuxtLink>
          </ScrollReveal>

          <ScrollReveal variant="up" :delay="160">
            <NuxtLink
              :to="SERVICES_ROUTES.singleSessions"
              class="visit-card"
              :class="{ 'visit-card--focus': visitFocus === 'treatments' }"
            >
              <img
                src="/images/showcase-massage.jpg"
                alt=""
                class="visit-card__media"
                width="1200"
                height="720"
                loading="lazy"
                decoding="async"
              />
              <span class="visit-card__mist" aria-hidden="true" />
              <span
                class="visit-card__badge"
                :class="{ 'visit-card__badge--today': visitFocus === 'treatments' }"
              >
                <template v-if="visitFocus === 'treatments'">
                  <span class="visit-card__badge-line">Open</span>
                  <span class="visit-card__badge-line">today</span>
                </template>
                <template v-else>
                  <span class="visit-card__badge-line">Mon · Thu</span>
                  <span class="visit-card__badge-line">– Sat</span>
                </template>
              </span>
              <span class="visit-card__body">
                <h3 class="visit-card__title">Treatments</h3>
                <span class="visit-card__text">One service when that is all you need today.</span>
                <span class="visit-card__meta">From KES 1,200</span>
                <span class="visit-card__cta">Book now</span>
              </span>
              <img
                src="/images/flower.png"
                alt=""
                class="visit-card__flower visit-card__flower--right"
                width="140"
                height="140"
                loading="lazy"
                decoding="async"
                aria-hidden="true"
              />
            </NuxtLink>
          </ScrollReveal>
          </div>
        </div>
      </div>

      <div id="packages" class="book-visit__stage">
          <div class="mellis-cta__atmosphere" aria-hidden="true">
            <img
              src="/images/stock-beauty-mono.jpg"
              alt=""
              class="mellis-cta__bg"
              width="1200"
              height="1600"
              loading="lazy"
              decoding="async"
            />
            <span class="mellis-cta__veil" />
          </div>

          <div class="mellis-cta__content">
            <ScrollReveal variant="up" :delay="40">
              <header class="mellis-cta__head">
                <h2>Full packages</h2>
              </header>
            </ScrollReveal>

            <div class="mellis-cta__card-wrap packages__band">
              <img
                src="/images/flower.png"
                alt=""
                class="mellis-cta__flower mellis-cta__flower--left"
                width="140"
                height="140"
                loading="lazy"
                decoding="async"
              />
              <img
                src="/images/flower.png"
                alt=""
                class="mellis-cta__flower"
                width="140"
                height="140"
                loading="lazy"
                decoding="async"
              />
              <ScrollReveal
                v-for="(pkg, index) in featuredPackages"
                :key="pkg.name"
                variant="up"
                :delay="80 + index * 60"
              >
                <MellisPackageCard
                  class="mellis-cta__card"
                  :name="pkg.name"
                  :text="pkg.text"
                  :price="pkg.price"
                  :includes="pkg.includes"
                  featured
                  :badge="pkg.badge"
                  :days-label="pkg.daysLabel"
                  :cta-label="pkg.ctaLabel || 'Book this package'"
                  :cta-to="bookHrefForPackageName(pkg.name)"
                  :details-to="SERVICES_ROUTES.fullPackages"
                  details-label="See all packages"
                />
              </ScrollReveal>
            </div>
            <p class="mellis-cta__note">{{ packageDayUrgency }}</p>
          </div>
      </div>
    </section>

    <!-- Client reviews — Mellis-style proof cards (no reviewer photos) -->
    <section class="reviews home-section" aria-labelledby="reviews-heading">
      <div class="reviews__inner">
        <ScrollReveal variant="up">
          <header class="reviews__head">
            <h2 id="reviews-heading">What clients say</h2>
          </header>
        </ScrollReveal>

        <div class="reviews__grid">
          <ScrollReveal
            v-for="(review, index) in reviews"
            :key="review.name"
            variant="up"
            :delay="70 + index * 80"
          >
            <blockquote class="review-card">
              <div class="review-card__top">
                <div class="review-card__stars" aria-label="5 out of 5 stars">★★★★★</div>
                <span class="review-card__quote" aria-hidden="true">”</span>
              </div>
              <p class="review-card__text">{{ review.text }}</p>
              <footer class="review-card__footer">
                <cite class="review-card__name">{{ review.name }}</cite>
                <span class="review-card__service">{{ review.visitLabel }}</span>
              </footer>
            </blockquote>
          </ScrollReveal>
        </div>
      </div>
    </section>

    <!-- Visit — split hours + clipped map -->
    <section id="visit" class="visit-map home-section">
      <div class="visit-map__inner">
        <ScrollReveal variant="up" :delay="40">
          <div class="visit-map__hours-panel">
            <div class="visit-map__card-head">
              <h2>Opening Hours</h2>
              <img src="/images/icon-clock.png" alt="" width="40" height="40" />
            </div>
            <dl class="visit-map__hours">
              <div>
                <dt>Monday</dt>
                <dd>7:00 am – 7:00 pm · treatments</dd>
              </div>
              <div>
                <dt>Tue &amp; Wed</dt>
                <dd>7:00 am – 7:00 pm · packages</dd>
              </div>
              <div>
                <dt>Thu – Sat</dt>
                <dd>7:00 am – 7:00 pm · treatments</dd>
              </div>
              <div>
                <dt>Sunday</dt>
                <dd>Closed</dd>
              </div>
            </dl>
            <p class="visit-map__place">{{ LANDING_LOCATION_LABEL }}</p>
            <div class="visit-map__actions">
              <SiteButton :to="primaryBookHref()" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
              <a
                v-if="contactIsLive"
                :href="whatsappUrl"
                class="visit-map__maps"
                target="_blank"
                rel="noopener noreferrer"
                @click="trackFunnelEvent('wa_click', { surface: 'visit_map' })"
              >
                {{ whatsappLabel }}
              </a>
              <a
                :href="LANDING_MAPS_URL"
                class="visit-map__maps"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open in Maps
              </a>
            </div>
          </div>
        </ScrollReveal>
        <div class="visit-map__map-panel">
          <div class="visit-map__frame-wrap">
            <iframe
              class="visit-map__frame"
              title="Shee Aesthetics location map"
              :src="LANDING_MAPS_EMBED_URL"
              loading="lazy"
              referrerpolicy="no-referrer-when-downgrade"
              allowfullscreen
            />
          </div>
        </div>
      </div>
    </section>

    <Teleport to="body">
      <div
        v-if="lightboxImage"
        class="work-lightbox"
        role="dialog"
        aria-modal="true"
        :aria-label="lightboxImage.alt"
        @click.self="closeWorkLightbox"
      >
        <button type="button" class="work-lightbox__close" aria-label="Close" @click="closeWorkLightbox">
          Close
        </button>
        <img
          :src="lightboxImage.src"
          :alt="lightboxImage.alt"
          class="work-lightbox__photo"
          width="1200"
          height="1600"
        />
        <p class="work-lightbox__caption">{{ lightboxImage.alt }}</p>
        <div class="work-lightbox__actions">
          <SiteButton :to="primaryBookHref()" variant="primary" @click="closeWorkLightbox">
            Book this vibe
          </SiteButton>
          <a
            :href="LANDING_INSTAGRAM_URL"
            class="work-lightbox__ig"
            target="_blank"
            rel="noopener noreferrer"
          >
            More on Instagram
          </a>
        </div>
      </div>
    </Teleport>
  </main>
</template>

<script setup lang="ts">
/**
 * Homepage composition (marketing only).
 * Section order: hero → welcome → our-work → offer → packages → reviews → visit.
 * Data helpers live under `src/landing/` — keep Django as the API, not Nuxt server routes.
 */
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  flowSteps,
  getFeaturedPackages,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_MAPS_EMBED_URL,
  LANDING_MAPS_URL,
  LANDING_PRICE_ANCHOR,
  LANDING_PRIMARY_CTA,
  landingClientReviews,
  packageDayUrgency,
} from '@/landing/landingContent'
import { fetchHomeWorkGallery, STATIC_HOME_WORK, type HomeWorkImage } from '@/landing/homeWorkGallery'
import {
  HERO_COPY_FADE_MS,
  HERO_CROSSFADE_MS,
  HERO_FADE_MS,
  heroCtaForSlide,
  heroSlides,
  shouldMountHeroImage,
} from '@/landing/heroMedia'
import { useLandingSeo } from '@/landing/useLandingSeo'
import { useLandingContact } from '@/landing/useLandingContact'
import { bookHrefForPackageName } from '@/landing/bookingHandoff'
import { primaryBookHref, primaryBookHrefKind } from '@/landing/primaryBookHref'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const config = useRuntimeConfig()
const contact = useLandingContact()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel

definePageMeta({ layout: 'landing' })
useLandingSeo()

const { data: workGallery } = await useAsyncData(
  'home-work-gallery',
  () => fetchHomeWorkGallery(String(config.public.apiBaseUrl || '')),
  { default: () => STATIC_HOME_WORK },
)
const workImages = computed(() => (workGallery.value ?? STATIC_HOME_WORK).slice(0, 8))

const activeSlide = ref(0)
/** Retain frames once mounted so crossfades never remount mid-fade. */
const retainedHeroSlides = ref(new Set<number>())
const mountedHeroSlides = computed(() => retainedHeroSlides.value)

watch(
  activeSlide,
  (active) => {
    const next = new Set(retainedHeroSlides.value)
    heroSlides.forEach((_, index) => {
      if (shouldMountHeroImage(active, index, heroSlides.length)) next.add(index)
    })
    retainedHeroSlides.value = next
  },
  { immediate: true },
)

const currentHero = computed(() => heroSlides[activeSlide.value] ?? heroSlides[0]!)
const heroCta = computed(() => heroCtaForSlide(currentHero.value))

const lightboxImage = ref<HomeWorkImage | null>(null)

function openWorkLightbox(img: HomeWorkImage) {
  lightboxImage.value = img
  trackFunnelEvent('gallery_open', { id: img.id })
}

function closeWorkLightbox() {
  lightboxImage.value = null
}

function onHeroBook() {
  trackFunnelEvent('cta_book_click', { surface: 'hero', href: heroCta.value.to })
}

let heroTimer: ReturnType<typeof setInterval> | null = null

function advanceHero() {
  if (typeof document !== 'undefined' && document.hidden) return
  activeSlide.value = (activeSlide.value + 1) % heroSlides.length
}

function goToHeroSlide(index: number) {
  activeSlide.value = index
  startHeroAutoplay()
}

function startHeroAutoplay() {
  stopHeroAutoplay()
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return
  }
  heroTimer = setInterval(advanceHero, HERO_FADE_MS)
}

function stopHeroAutoplay() {
  if (heroTimer) {
    clearInterval(heroTimer)
    heroTimer = null
  }
}

function onHeroVisibility() {
  if (document.hidden) stopHeroAutoplay()
  else startHeroAutoplay()
}

onMounted(() => {
  startHeroAutoplay()
  document.addEventListener('visibilitychange', onHeroVisibility)
})

onUnmounted(() => {
  stopHeroAutoplay()
  document.removeEventListener('visibilitychange', onHeroVisibility)
})

const featuredPackages = getFeaturedPackages()

/** Day bias for visit doors — matches sticky/header Book href logic. */
const visitFocus = computed(() => primaryBookHrefKind())

const offerShowcase = [
  { index: '01', label: 'Facials', perk: 'Deep cleansing facials', to: `${SERVICES_ROUTES.page}#facials` },
  { index: '02', label: 'Massage', perk: 'Hot stone massage', to: `${SERVICES_ROUTES.page}#massage` },
  { index: '03', label: 'Waxing', perk: 'Brow shaping', to: `${SERVICES_ROUTES.page}#waxing` },
  { index: '04', label: 'Makeup', perk: 'Bridal & event glam', to: `${SERVICES_ROUTES.page}#makeup` },
]

const reviews = landingClientReviews
</script>

<style scoped>
.home {
  background: var(--color-paper);
  margin: 0;
  padding: 0;
  /* Clear section rhythm — mobile first, breathing room between chapters */
  --home-section-y: clamp(2rem, 5vh, 2.75rem);
  --home-section-y-lg: clamp(2.35rem, 5.5vh, 3.25rem);
  --home-head-gap: 1.15rem;
  --home-seam: 1px solid rgba(176, 122, 113, 0.14);
}

.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

.label {
  margin: 0 0 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.section-head {
  width: var(--container);
  margin: 0 auto var(--home-head-gap);
  text-align: center;
  padding: 0 0.25rem;
}

.section-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.95rem, 4.2vw, 2.85rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.section-head__sub {
  max-width: 52ch;
  margin: 0.65rem auto 0;
  font: 400 0.95rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.home-services-link {
  font-weight: 600;
  color: var(--color-rose);
  text-decoration: none;
  letter-spacing: 0.02em;
}

.home-services-link:hover {
  text-decoration: underline;
}

.section-head--light .label,
.section-head--light h2 {
  color: #fff;
}

/* Hero — full photo + wave seam into paper (no ash fog) */
.hero {
  position: relative;
  width: 100%;
  /* Locked: mobile 92dvh — soft floor so short phones stay inside the viewport */
  height: 92svh;
  height: 92dvh;
  min-height: 28rem;
  overflow: hidden;
  background: var(--color-ink);
  --hero-crossfade-ms: 2800ms;
  --hero-copy-fade-ms: 1400ms;
}

.hero__track {
  position: absolute;
  inset: 0;
}

.hero__slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity var(--hero-crossfade-ms) cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity;
  pointer-events: none;
}

.hero__slide--active {
  opacity: 1;
  z-index: 1;
}

.hero__slide picture {
  display: block;
  width: 100%;
  height: 100%;
}

.hero__bg {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  /* Subtle settle — avoid heavy blur from oversized Ken Burns */
  transform: scale(1.03);
  transition: transform var(--hero-crossfade-ms) cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

.hero__slide--active .hero__bg {
  transform: scale(1);
}

.hero__overlay {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  /* Lighter veil — keep photos sharp; copy still readable */
  background:
    linear-gradient(
      180deg,
      rgba(20, 16, 18, 0.22) 0%,
      rgba(20, 16, 18, 0.12) 42%,
      rgba(20, 16, 18, 0.34) 100%
    );
}

.hero__wave {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  z-index: 5;
  width: 100%;
  height: clamp(2.5rem, 6vw, 4.5rem);
  display: block;
  pointer-events: none;
}

.hero__content {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: grid;
  place-items: center;
  text-align: center;
  /* Center in the band below the Home 3 header, not under the logo stack */
  padding:
    max(var(--site-header-height, 7.5rem), env(safe-area-inset-top, 0px))
    1.25rem
    max(3.5rem, env(safe-area-inset-bottom, 0px));
  color: #fff;
  pointer-events: none;
}

.hero__copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(1rem, 2.6vh, 2.35rem);
  text-align: center;
  max-width: min(94vw, 56rem);
  margin: 0;
  transform: none;
  position: relative;
  animation: hero-copy-in 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.hero__content :deep(.site-btn) {
  pointer-events: auto;
}

@keyframes hero-copy-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero__eyebrow {
  margin: 0;
  font-family: var(--font-body);
  font-size: clamp(0.72rem, 1.15vw, 1.05rem);
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.95);
}

.hero__title {
  /* Handwriting title owns type scale; keep as flex child */
  margin: 0;
}

.hero__price {
  margin: 0.45rem 0 0;
  max-width: 22rem;
  font: 500 0.8rem/1.35 var(--font-body);
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
}

.hero__cta {
  display: inline-flex;
  min-height: 3.1rem;
  margin-top: 0.15rem;
  padding: 1rem 2.15rem !important;
  border-radius: 0 !important;
  font-size: 0.76rem !important;
  letter-spacing: 0.16em !important;
}

.hero__dots {
  position: absolute;
  left: 50%;
  bottom: calc(var(--mobile-book-bar-height, 4.25rem) + 1.35rem);
  z-index: 4;
  display: flex;
  gap: 0.4rem;
  transform: translateX(-50%);
}

.hero__dot {
  width: 0.5rem;
  height: 0.5rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
  cursor: pointer;
  transition: background-color 0.25s ease, transform 0.25s ease;
}

.hero__dot--active {
  background: #fff;
  transform: scale(1.15);
}

.hero__dot:focus-visible {
  outline: 2px solid #fff;
  outline-offset: 3px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Welcome — calm seam under spa hero */
.welcome {
  padding: var(--home-section-y) 1rem;
  position: relative;
  z-index: 1;
  margin-top: 0;
  background: var(--color-paper);
  border-bottom: var(--home-seam);
}

@media (max-width: 767px) {
  .welcome {
    padding-top: clamp(2.5rem, 6vh, 3.25rem);
  }

  /* Hero + sticky bar already book — keep welcome focused on paths */
  .welcome__cta {
    display: none;
  }
}

.welcome__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.35rem;
  align-items: center;
}

.welcome__media-wrap,
.welcome__copy {
  height: 100%;
}

.welcome__media {
  position: relative;
  display: flex;
  justify-content: center;
}

.welcome__mirror {
  position: relative;
  width: min(260px, 68vw);
  aspect-ratio: 1;
  margin: 0 auto;
  padding: 6px;
  border-radius: 50%;
  background: linear-gradient(145deg, var(--color-rose-soft), #fff 45%, var(--color-rose-soft));
  box-shadow:
    0 0 0 1px rgba(222, 150, 141, 0.35),
    0 16px 48px rgba(39, 37, 42, 0.12);
}

.welcome__photo {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
}

.welcome__flower {
  position: absolute;
  right: max(-0.25rem, calc(50% - 150px));
  bottom: 0.5rem;
  z-index: 2;
  width: min(100px, 28%);
  pointer-events: none;
}

.welcome__copy h2 {
  margin: 0 0 1.25rem;
  font-family: var(--font-display);
  font-size: clamp(1.95rem, 3.8vw, 2.75rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
}

.welcome__text {
  margin: 0 0 1.5rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

/* Treatments — Mellis static-bg scroll chapter + colored Shee board */
.offer.home-section {
  content-visibility: visible;
  contain-intrinsic-size: none;
}

.offer {
  position: relative;
  /* Taller runway — more photo hold + less cramped sticky chapter */
  min-height: 175vh;
  padding: 0;
  overflow: clip;
  background: #1c1714;
  border-block: var(--home-seam);
}

.offer__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  clip-path: inset(0);
}

.offer__fixed {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
}

.offer__photo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 72% 42%;
  transform: scale(1.06);
  transform-origin: 70% 40%;
}

.offer__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(18, 12, 12, 0.52) 0%,
      rgba(18, 12, 12, 0.34) 38%,
      rgba(18, 12, 12, 0.62) 72%,
      rgba(18, 12, 12, 0.72) 100%
    ),
    linear-gradient(
      90deg,
      rgba(18, 12, 12, 0.36) 0%,
      rgba(18, 12, 12, 0.16) 48%,
      rgba(18, 12, 12, 0.32) 100%
    );
  pointer-events: none;
}

.offer__chapter {
  position: sticky;
  top: var(--site-header-height, 4.75rem);
  z-index: 1;
  display: flex;
  align-items: center;
  min-height: calc(100vh - var(--site-header-height, 4.75rem));
  padding: clamp(4rem, 9vh, 7.5rem) 1.25rem;
}

.offer__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.85rem, 4.5vh, 3rem);
}

.offer__head {
  display: flex;
  justify-content: center;
  text-align: center;
}

.offer__title-lockup {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.85rem, 2.4vw, 1.6rem);
  max-width: 100%;
  padding: 0.35rem 0 0.5rem;
}

.offer__title-lockup h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2.65rem, 7.5vw, 4.15rem);
  font-weight: 500;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: #fff;
  text-shadow: 0 3px 22px rgba(0, 0, 0, 0.5);
}

.offer__title-flower {
  width: clamp(2.75rem, 6.5vw, 4rem);
  height: auto;
  flex-shrink: 0;
  opacity: 0.88;
  filter: brightness(1.05) saturate(0.95);
  pointer-events: none;
}

.offer__title-flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.offer__title-flower--right {
  transform: rotate(8deg);
}

.offer__board {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.95rem;
}

.offer__board > li {
  min-width: 0;
  height: 100%;
}

.offer__board > li :deep(.reveal),
.offer__board > li :deep(.reveal > *) {
  height: 100%;
}

.offer__cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  height: 100%;
  min-height: 9.5rem;
  padding: 1.35rem 1.15rem 1.2rem;
  color: #fff;
  text-decoration: none;
  background: rgba(28, 16, 18, 0.52);
  border: 1px solid rgba(245, 216, 208, 0.22);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06) inset,
    0 14px 32px rgba(8, 4, 4, 0.28);
  backdrop-filter: blur(18px) saturate(1.15);
  -webkit-backdrop-filter: blur(18px) saturate(1.15);
  cursor: pointer;
  transition:
    background 0.25s ease,
    border-color 0.25s ease,
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease;
}

.offer__cell:hover,
.offer__cell:focus-visible {
  background: rgba(176, 122, 113, 0.42);
  border-color: rgba(245, 216, 208, 0.55);
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.1) inset,
    0 20px 40px rgba(8, 4, 4, 0.4);
  outline: none;
}

.offer__cell:hover .offer__name,
.offer__cell:focus-visible .offer__name {
  color: #f5d8d0;
}

.offer__cell:hover .offer__go,
.offer__cell:focus-visible .offer__go {
  opacity: 1;
  transform: translateX(0);
}

.offer__index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.7rem;
  height: 1.7rem;
  padding: 0 0.35rem;
  margin-bottom: 0.15rem;
  border: 1px solid rgba(240, 184, 172, 0.55);
  border-radius: 999px;
  background: rgba(222, 150, 141, 0.18);
  font: 600 0.62rem/1 var(--font-body);
  letter-spacing: 0.12em;
  color: #f5d8d0;
}

.offer__name {
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 4.6vw, 1.95rem);
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.4);
  transition: color 0.2s ease;
}

.offer__detail {
  margin: 0;
  font: 400 0.82rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.88);
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.35);
}

.offer__go {
  margin-top: auto;
  padding-top: 0.65rem;
  font: 600 0.68rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #f0b8ac;
  opacity: 0.72;
  transform: translateX(-0.15rem);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.offer__cta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem 1.5rem;
  width: 100%;
  margin-top: 0.25rem;
  padding: 1.45rem 1.5rem;
  background:
    linear-gradient(135deg, rgba(176, 122, 113, 0.92) 0%, rgba(140, 88, 82, 0.95) 100%);
  border: 1px solid rgba(245, 216, 208, 0.35);
  color: #fff;
  text-decoration: none;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08) inset,
    0 18px 40px rgba(80, 32, 36, 0.45);
  transition:
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease,
    filter 0.25s ease;
}

.offer__cta:hover,
.offer__cta:focus-visible {
  transform: translateY(-3px);
  filter: brightness(1.05);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.12) inset,
    0 22px 48px rgba(80, 32, 36, 0.55);
  outline: none;
}

.offer__cta-copy {
  display: grid;
  gap: 0.28rem;
  min-width: 0;
  text-align: left;
}

.offer__cta-label {
  font: 600 0.68rem/1.2 var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 245, 240, 0.88);
}

.offer__cta-title {
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.5vw, 1.95rem);
  font-weight: 400;
  line-height: 1.15;
  color: #fff;
}

.offer__cta-meta {
  font: 400 0.86rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.9);
}

.offer__cta-action {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  padding: 0.85rem 1.15rem;
  background: #fff;
  color: var(--color-ink);
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  box-shadow: 0 8px 20px rgba(40, 16, 18, 0.2);
  transition: transform 0.2s ease, background 0.2s ease;
}

.offer__cta:hover .offer__cta-action,
.offer__cta:focus-visible .offer__cta-action {
  background: #fff8f4;
}

.offer__cta-arrow {
  font-size: 1rem;
  line-height: 1;
  letter-spacing: 0;
  transition: transform 0.2s ease;
}

.offer__cta:hover .offer__cta-arrow,
.offer__cta:focus-visible .offer__cta-arrow {
  transform: translateX(0.2rem);
}

@media (max-width: 767px) {
  .offer {
    min-height: auto;
  }

  .offer__chapter {
    position: relative;
    top: auto;
    min-height: min(92svh, 48rem);
    padding: clamp(3.75rem, 9vh, 6rem) 1.15rem;
  }

  .offer__fixed {
    position: absolute;
    inset: 0;
  }

  .offer__inner {
    gap: 1.75rem;
  }

  .offer__head {
    margin-bottom: 0.35rem;
  }

  .offer__cta {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 1.1rem;
    padding: 1.35rem 1.2rem 1.25rem;
  }

  .offer__cta-action {
    justify-content: center;
    width: 100%;
  }

  .offer__board {
    gap: 0.85rem;
  }

  .offer__cell {
    min-height: 9.25rem;
    padding: 1.2rem 1rem 1.1rem;
  }

  .offer__go {
    opacity: 0.85;
    transform: none;
  }

  .hero__eyebrow {
    letter-spacing: 0.16em;
  }

  .hero__cta {
    min-height: 2.85rem;
    padding: 0.9rem 1.75rem !important;
  }
}

@media (min-width: 768px) {
  .offer {
    min-height: 185vh;
  }

  .offer__chapter {
    padding: clamp(4.5rem, 10vh, 8rem) 1.5rem;
  }

  .offer__inner {
    gap: clamp(2.15rem, 5vh, 3.25rem);
  }

  .offer__photo {
    object-position: 68% 40%;
  }

  .offer__board {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1.15rem;
  }

  .offer__cell {
    min-height: 12.5rem;
    padding: clamp(1.45rem, 2.8vh, 1.9rem) clamp(1.1rem, 1.5vw, 1.4rem);
    gap: 0.45rem;
  }

  .offer__name {
    font-size: clamp(1.55rem, 2vw, 1.95rem);
  }

  .offer__detail {
    font-size: 0.88rem;
    max-width: 14ch;
  }
}

@media (min-width: 1024px) {
  .offer {
    min-height: 190vh;
  }

  .offer__photo {
    object-position: 65% 38%;
  }

  .offer__title-lockup h2 {
    font-size: clamp(3.1rem, 3.8vw, 4.25rem);
  }

  .offer__cta {
    padding: 1.55rem 1.85rem;
  }

  .offer__name {
    font-size: clamp(1.7rem, 1.9vw, 2.1rem);
  }

  .offer__detail {
    font-size: 0.92rem;
  }

  .offer__cell {
    min-height: 13.25rem;
  }
}

@media (min-width: 1440px) {
  .offer__photo {
    object-position: 62% 36%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .offer {
    min-height: auto;
  }

  .offer__chapter {
    position: relative;
    min-height: auto;
    padding: clamp(4rem, 9vh, 8rem) 1.25rem;
  }

  .offer__fixed {
    position: absolute;
    inset: 0;
  }

  .offer__photo {
    transform: none;
  }

  .offer__cell:hover,
  .offer__cell:focus-visible,
  .offer__cta:hover,
  .offer__cta:focus-visible {
    transform: none;
    filter: none;
  }
}

/* Steps — numbered book → pay → visit cards (no images, one system) */
.steps {
  padding: var(--home-section-y-lg) 1.25rem;
  background: var(--color-parchment);
  border-block: var(--home-seam);
}

.steps__compact {
  list-style: none;
  width: var(--container);
  margin: 0 auto;
  padding: 0;
  display: grid;
  gap: 0.85rem;
}

.steps__compact li {
  display: grid;
  grid-template-columns: 2.5rem 1fr;
  gap: 0.85rem;
  align-items: start;
  height: 100%;
  padding: 1rem 1rem 1.05rem;
  background: #fff;
  border: 1px solid rgba(176, 122, 113, 0.14);
  box-shadow: 0 10px 28px rgba(44, 44, 48, 0.04);
}

.steps__compact-num {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.04em;
}

.steps__compact strong {
  display: block;
  margin: 0.1rem 0 0.3rem;
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-ink);
}

.steps__compact p {
  margin: 0;
  font: 400 0.88rem/1.5 var(--font-body);
  color: var(--color-muted);
}

@media (min-width: 768px) {
  .steps__compact {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.15rem;
  }

  .steps__compact li {
    grid-template-columns: 1fr;
    justify-items: start;
    gap: 0.75rem;
    padding: 1.35rem 1.25rem 1.4rem;
  }

  .steps__compact strong {
    font-size: 1.2rem;
  }

  .steps__compact p {
    font-size: 0.92rem;
  }
}

@media (min-width: 1024px) {
  .steps__compact {
    gap: 1.35rem;
  }

  .steps__compact li {
    padding: 1.5rem 1.4rem 1.55rem;
  }

  .steps__compact strong {
    font-size: 1.28rem;
  }
}

/* Cut brochure filler on phones — keep booking path short */
@media (max-width: 767px) {
  .home-section--desktop-only {
    display: none !important;
  }
}

/* Book a visit — distinctive atmospheric path through doors */
.book-visit {
  padding: 0;
  background: var(--color-paper);
  overflow: hidden;
  border-bottom: var(--home-seam);
}

.book-visit__path {
  position: relative;
  padding: clamp(2.5rem, 6vh, 4rem) 1rem;
  overflow: hidden;
}

.book-visit__atmosphere {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.book-visit__bg {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 40%;
  transform: scale(1.1);
  filter: saturate(0.55) blur(6px) brightness(1.06);
  opacity: 0.7;
}

.book-visit__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(252, 248, 244, 0.92) 0%,
      rgba(252, 248, 244, 0.82) 42%,
      rgba(252, 248, 244, 0.94) 100%
    ),
    radial-gradient(ellipse 70% 55% at 12% 0%, rgba(176, 122, 113, 0.14), transparent 55%),
    radial-gradient(ellipse 55% 45% at 92% 100%, rgba(176, 122, 113, 0.1), transparent 50%);
}

.book-visit__path-inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.5rem, 3.5vw, 2.25rem);
}

.book-visit__head {
  text-align: center;
  max-width: 28rem;
  margin: 0 auto;
}

.book-visit__head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2rem, 4.4vw, 2.85rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}

.book-visit__doors {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
}

.book-visit__doors > * {
  min-width: 0;
  height: 100%;
}

.visit-card {
  position: relative;
  display: block;
  min-height: 16.5rem;
  overflow: hidden;
  text-decoration: none;
  color: var(--color-ink);
  background: var(--color-cream);
  box-shadow: 0 14px 34px rgba(44, 44, 48, 0.08);
  transition:
    transform 0.35s var(--ease-story, ease),
    box-shadow 0.35s var(--ease-story, ease);
}

.visit-card__media {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
  transform: scale(1.02);
  transition: transform 0.7s var(--ease-story, ease);
}

.visit-card__media--mono {
  object-position: center 28%;
  filter: grayscale(1) contrast(1.08);
}

/* Mellis mist: soft left wash so script + CTA stay readable */
.visit-card__mist {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      95deg,
      rgba(255, 252, 250, 0.94) 0%,
      rgba(255, 252, 250, 0.82) 28%,
      rgba(255, 252, 250, 0.35) 52%,
      rgba(255, 252, 250, 0.06) 72%,
      transparent 100%
    ),
    linear-gradient(180deg, transparent 55%, rgba(255, 252, 250, 0.28) 100%);
}

.visit-card__badge {
  position: absolute;
  top: 1.15rem;
  right: 1.15rem;
  z-index: 3;
  display: grid;
  place-content: center;
  width: 4.5rem;
  height: 4.5rem;
  padding: 0.35rem;
  border-radius: 50%;
  text-align: center;
  color: #fff;
  background: var(--color-rose);
  box-shadow: 0 10px 22px rgba(176, 122, 113, 0.32);
}

.visit-card__badge--today {
  background: var(--color-rose-dark);
}

.visit-card__badge-line {
  display: block;
  font: 700 0.58rem/1.15 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.visit-card__body {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.4rem;
  min-height: 16.5rem;
  max-width: 17.5rem;
  padding: 1.5rem 1.25rem 1.55rem 1.4rem;
}

.visit-card__title {
  margin: 0;
  font-family: var(--font-script);
  font-size: clamp(2.15rem, 4.6vw, 2.75rem);
  font-weight: 400;
  line-height: 1;
  color: var(--color-ink);
}

.visit-card__text {
  max-width: 20ch;
  font: 500 0.9rem/1.45 var(--font-body);
  color: var(--color-deep);
}

.visit-card__meta {
  font: 700 0.72rem/1.3 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.visit-card__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.55rem;
  min-height: 2.65rem;
  padding: 0.7rem 1.55rem;
  font: 700 0.7rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-ink);
  background: #fff;
  border: 0;
  box-shadow: 0 8px 20px rgba(44, 44, 48, 0.12);
}

.visit-card__flower {
  position: absolute;
  z-index: 3;
  left: 38%;
  bottom: -0.85rem;
  width: min(7.25rem, 32%);
  height: auto;
  pointer-events: none;
  filter: drop-shadow(0 6px 12px rgba(44, 44, 48, 0.12));
}

.visit-card__flower--right {
  left: auto;
  right: 0.5rem;
  bottom: -0.95rem;
}

.visit-card--focus {
  box-shadow: 0 18px 40px rgba(176, 122, 113, 0.2);
}

.visit-card:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

@media (hover: hover) {
  .visit-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 42px rgba(44, 44, 48, 0.12);
  }

  .visit-card:hover .visit-card__media {
    transform: scale(1.06);
  }

  .visit-card:hover .visit-card__cta {
    background: var(--color-rose);
    color: #fff;
  }
}

/* Classic Full Package — B&W model atmosphere; card stays primary */
.book-visit__stage {
  position: relative;
  isolation: isolate;
  margin-top: 0;
  padding: clamp(2.5rem, 6vw, 3.75rem) 1rem clamp(2.25rem, 5vw, 3.25rem);
  overflow: hidden;
  border-block: 1px solid rgba(176, 122, 113, 0.16);
}

.mellis-cta__atmosphere {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.mellis-cta__bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 18%;
  transform: scale(1.04);
  /* Already a B&W portrait — keep light grayscale pass for consistency */
  filter: grayscale(0.35) contrast(1.06) brightness(1.03);
  opacity: 0.48;
}

.mellis-cta__veil {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      ellipse 48% 62% at 50% 46%,
      rgba(243, 242, 241, 0.96) 0%,
      rgba(243, 242, 241, 0.86) 36%,
      rgba(243, 242, 241, 0.48) 68%,
      rgba(243, 242, 241, 0.18) 100%
    ),
    linear-gradient(
      180deg,
      rgba(243, 242, 241, 0.68) 0%,
      rgba(243, 242, 241, 0.28) 36%,
      rgba(243, 242, 241, 0.28) 64%,
      rgba(243, 242, 241, 0.72) 100%
    );
}

.mellis-cta__content {
  position: relative;
  z-index: 1;
}

.mellis-cta__head {
  text-align: center;
  max-width: 28rem;
  margin: 0 auto 1.75rem;
}

.mellis-cta__head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.mellis-cta__card-wrap {
  position: relative;
  width: min(100%, 26rem);
  margin: 0 auto;
  padding-top: 0.65rem;
}

.mellis-cta__flower {
  position: absolute;
  z-index: 0;
  right: -1.15rem;
  bottom: -1.15rem;
  width: min(7.5rem, 36%);
  height: auto;
  pointer-events: none;
  opacity: 0.92;
}

.mellis-cta__flower--left {
  right: auto;
  left: -1.35rem;
  bottom: auto;
  top: -0.85rem;
  width: min(6.25rem, 30%);
  opacity: 0.78;
  transform: scaleX(-1) rotate(-8deg);
}

.mellis-cta__card-wrap > *:not(.mellis-cta__flower) {
  position: relative;
  z-index: 1;
}

.mellis-cta__card {
  box-shadow:
    0 22px 48px rgba(44, 44, 48, 0.14),
    0 0 0 1px rgba(255, 255, 255, 0.7);
}

@media (max-width: 479px) {
  .book-visit__stage {
    padding-inline: 0.85rem;
  }

  .mellis-cta__flower {
    width: min(5.5rem, 28%);
    right: -0.55rem;
    bottom: -0.75rem;
  }

  .mellis-cta__flower--left {
    left: -0.65rem;
    top: -0.55rem;
    width: min(4.75rem, 24%);
  }

  .mellis-cta__head h2 {
    font-size: clamp(1.75rem, 8vw, 2.1rem);
  }
}

.mellis-cta__note {
  margin: 1.1rem auto 0;
  max-width: 28rem;
  text-align: center;
  font: 500 0.8rem/1.45 var(--font-body);
  color: var(--color-rose-dark);
}

@media (min-width: 768px) {
  .book-visit__doors {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.15rem;
  }

  .visit-card,
  .visit-card__body {
    min-height: 18.5rem;
  }

  .visit-card__body {
    max-width: 18.5rem;
    padding: 1.65rem 1.4rem 1.7rem 1.65rem;
  }

  .mellis-cta__card-wrap {
    width: min(100%, 28rem);
  }
}

@media (min-width: 1024px) {
  .visit-card,
  .visit-card__body {
    min-height: 19.5rem;
  }

  .visit-card__title {
    font-size: 2.85rem;
  }
}

.reviews__grid > * {
  height: 100%;
  min-width: 0;
}

/* Reviews — Mellis-style proof cards, Shee-branded */
.reviews {
  position: relative;
  padding: clamp(2.5rem, 5.5vh, 3.5rem) 1rem;
  overflow: hidden;
  border-block: var(--home-seam);
  background:
    radial-gradient(ellipse 60% 50% at 8% 20%, rgba(176, 122, 113, 0.1), transparent 55%),
    radial-gradient(ellipse 50% 45% at 92% 80%, rgba(176, 122, 113, 0.08), transparent 50%),
    linear-gradient(180deg, var(--color-parchment) 0%, var(--color-paper) 48%, var(--color-cream) 100%);
}

.reviews__inner {
  width: var(--container);
  margin: 0 auto;
}

.reviews__head {
  margin-bottom: 1.75rem;
  text-align: center;
}

.reviews__head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4vw, 2.65rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.reviews__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
}

.reviews__grid > * {
  height: 100%;
  min-width: 0;
}

.review-card {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  margin: 0;
  padding: 1.45rem 1.3rem 1.35rem;
  background: #fff;
  border: 1px solid rgba(176, 122, 113, 0.12);
  box-shadow: 0 14px 34px rgba(44, 44, 48, 0.06);
  transition:
    transform 0.35s var(--ease-story, ease),
    box-shadow 0.35s var(--ease-story, ease);
}

.review-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(44, 44, 48, 0.09);
}

.review-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.review-card__stars {
  color: var(--color-rose);
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  line-height: 1;
}

.review-card__quote {
  font-family: var(--font-display);
  font-size: 3.25rem;
  line-height: 0.55;
  color: rgba(176, 122, 113, 0.28);
  user-select: none;
}

.review-card__text {
  flex: 1;
  margin: 0 0 1.15rem;
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--color-muted);
}

.review-card__footer {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.review-card__name {
  font: 700 1.05rem/1.25 var(--font-display);
  font-style: normal;
  color: var(--color-ink);
}

.review-card__service {
  font: 600 0.72rem/1.35 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-rose);
}

@media (min-width: 768px) {
  .reviews__head {
    margin-bottom: 2rem;
  }

  .reviews__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;
  }
}

/* Our work — Pinterest-style masonry */
.work {
  padding: var(--home-section-y-lg) 1rem;
  background: var(--color-cream);
  border-bottom: var(--home-seam);
}

.work__masonry {
  width: var(--container);
  margin: 0 auto;
  column-count: 2;
  column-gap: 0.65rem;
}

.work__tile {
  display: block;
  width: 100%;
  padding: 0;
  border: 0;
  break-inside: avoid;
  margin: 0 0 0.65rem;
  overflow: hidden;
  background: var(--color-cream);
  text-decoration: none;
  text-align: left;
  cursor: pointer;
  font: inherit;
  color: inherit;
  -webkit-tap-highlight-color: transparent;
}

.work__tile--tall .work__photo {
  aspect-ratio: 3 / 4;
}

.work__tile--wide .work__photo {
  aspect-ratio: 4 / 3;
}

.work__tile--square .work__photo {
  aspect-ratio: 1;
}

.work__photo {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: transform 0.7s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1));
}

@media (hover: hover) {
  .work__tile:hover .work__photo {
    transform: scale(1.04);
  }
}

.work__tile:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

.work__footer {
  width: var(--container);
  margin: 1.35rem auto 0;
  text-align: center;
}

@media (min-width: 768px) {
  .work__masonry {
    column-count: 3;
    column-gap: 0.85rem;
  }

  .work__tile {
    margin-bottom: 0.85rem;
  }
}

@media (min-width: 1024px) {
  .work__masonry {
    column-count: 4;
    column-gap: 1rem;
  }
}

.work-lightbox {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  padding: 1.25rem;
  background: rgba(20, 16, 18, 0.88);
}

.work-lightbox__photo {
  max-width: min(92vw, 28rem);
  max-height: 62vh;
  width: auto;
  height: auto;
  object-fit: contain;
}

.work-lightbox__caption {
  margin: 0;
  max-width: 28rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  font: 500 0.92rem/1.4 var(--font-body);
}

.work-lightbox__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: center;
}

.work-lightbox__ig {
  color: #fff;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: underline;
  text-underline-offset: 0.2em;
}

.work-lightbox__close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  min-height: 2.5rem;
  padding: 0.4rem 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 999px;
  background: transparent;
  color: #fff;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
}

/* Visit — split hours + clipped map */
.visit-map {
  padding: var(--home-section-y-lg) 1rem;
  background: var(--color-paper);
  border-top: var(--home-seam);
}

.visit-map__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-items: stretch;
}

.visit-map__hours-panel {
  padding: 0.25rem 0 0.5rem;
}

.visit-map__card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.35rem;
}

.visit-map__card-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3vw, 1.85rem);
  font-weight: 400;
  color: var(--color-ink);
}

.visit-map__hours {
  margin: 0 0 1.25rem;
}

.visit-map__hours > div {
  margin-bottom: 0.9rem;
}

.visit-map__hours > div:last-child {
  margin-bottom: 0;
}

.visit-map__hours dt {
  margin: 0 0 0.2rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.visit-map__hours dd {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 400;
  color: var(--color-rose);
  line-height: 1.35;
}

.visit-map__place {
  margin: 0 0 1.25rem;
  font: 500 0.88rem/1.4 var(--font-body);
  color: var(--color-muted);
}

.visit-map__actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.85rem;
}

.visit-map__maps {
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
  text-decoration: none;
}

.visit-map__maps:hover {
  color: var(--color-rose-dark);
}

.visit-map__map-panel {
  min-width: 0;
}

.visit-map__frame-wrap {
  position: relative;
  height: 15rem;
  overflow: hidden;
  background: var(--color-paper);
}

.visit-map__frame {
  position: absolute;
  /* Crop Google search chrome / UI edges */
  top: -3.5rem;
  left: -1rem;
  width: calc(100% + 2rem);
  height: calc(100% + 5.5rem);
  border: 0;
  filter: grayscale(0.35) contrast(0.92) saturate(0.75);
  pointer-events: auto;
}

@media (min-width: 768px) {
  .visit-map__inner {
    grid-template-columns: minmax(16rem, 22rem) 1fr;
    gap: clamp(1.5rem, 3vw, 2.5rem);
    align-items: center;
  }

  .visit-map__hours-panel {
    padding: 0.5rem 0;
  }

  .visit-map__frame-wrap {
    height: min(26rem, 52vh);
    min-height: 22rem;
  }
}

@media (min-width: 1024px) {
  .visit-map__inner {
    grid-template-columns: minmax(18rem, 24rem) 1fr;
    gap: clamp(2rem, 4vw, 3.25rem);
  }

  .visit-map__frame-wrap {
    height: min(28rem, 50vh);
    min-height: 24rem;
  }
}

/* Tablet and up — progressive enhancement */
@media (min-width: 768px) {
  .home {
    --home-section-y: 2rem;
    --home-section-y-lg: 2.25rem;
    --home-head-gap: 0.95rem;
  }

  .hero {
    /* Locked: tablet/iPad 92vh — Mellis-tall */
    height: 92vh;
    min-height: 38rem;
  }

  .hero__content {
    padding:
      max(var(--site-header-height, 8.5rem), env(safe-area-inset-top, 0px))
      1.5rem
      2.5rem;
  }

  .hero__copy {
    transform: none;
  }

  @keyframes hero-copy-in {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .hero__dots {
    bottom: 2.5rem;
  }

  .hero__eyebrow {
    font-size: clamp(0.9rem, 1.15vw, 1.1rem);
    letter-spacing: 0.3em;
  }

  .welcome {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .welcome__inner {
    gap: clamp(1.25rem, 3vw, 2rem);
  }

  .welcome__mirror {
    width: min(320px, 42vw);
  }

  .welcome__flower {
    right: -1rem;
    width: min(130px, 30%);
  }

  .work,
  .reviews,
  .visit-map {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .book-visit__path {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .visit-card__body {
    padding: 1.55rem 1.35rem 1.6rem 1.5rem;
  }

  .review-card {
    padding: 1.5rem 1.35rem 1.4rem;
  }
}

@media (min-width: 1024px) {
  .home {
    --home-section-y: 2.25rem;
    --home-section-y-lg: 2.5rem;
    --home-head-gap: 1rem;
  }

  .hero {
    /* Locked: desktop 100vh — Mellis full viewport */
    height: 100vh;
    min-height: 44rem;
  }

  .welcome__inner {
    grid-template-columns: 1fr 1fr;
    gap: clamp(1.5rem, 3vw, 2.75rem);
  }

  .reviews__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.15rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__slide,
  .hero__bg,
  .hero__content,
  .hero__copy,
  .package-card,
  .review-card,
  .book-visit__door,
  .book-visit__door-media,
  .visit-card,
  .visit-card__media {
    animation: none !important;
    transition: none !important;
  }

  .hero__bg {
    transform: none !important;
  }
}
</style>
