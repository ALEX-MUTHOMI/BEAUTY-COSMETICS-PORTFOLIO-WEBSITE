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
          <SiteButton :to="HERO_CTA.to" variant="primary" class="hero__cta">
            {{ HERO_CTA.label }}
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
            <SiteButton to="/services" variant="primary" class="welcome__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
          </div>
        </ScrollReveal>
      </div>
    </section>

    <!-- Our work — Pinterest masonry; primary proof for new clients -->
    <section id="our-work" class="work home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">Our work</p>
          <h2>Clients by Shee</h2>
          <p class="section-head__sub">Studio mood — makeup, facials, massage &amp; waxing.</p>
        </header>
      </ScrollReveal>
      <div class="work__masonry" aria-label="Shee client and studio work">
        <a
          v-for="(img, index) in workImages"
          :key="img.id"
          :href="LANDING_INSTAGRAM_URL"
          class="work__tile"
          :class="`work__tile--${img.shape}`"
          target="_blank"
          rel="noopener noreferrer"
          :aria-label="img.alt"
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
        </a>
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
            <div>
              <p class="offer__label">What we offer</p>
              <h2 class="sr-only">Facials, massage, waxing and makeup</h2>
            </div>
            <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="offer__cta">
              View packages
              <span class="offer__cta-arrow" aria-hidden="true">→</span>
            </NuxtLink>
          </header>
          <ul class="offer__board" aria-label="Core treatments">
            <li v-for="(item, index) in offerShowcase" :key="item.label">
              <ScrollReveal variant="up" :delay="60 + index * 70">
                <NuxtLink :to="item.to" class="offer__cell">
                  <span class="offer__index" aria-hidden="true">{{ item.index }}</span>
                  <span class="offer__name">{{ item.label }}</span>
                  <span class="offer__detail">{{ item.perk }}</span>
                </NuxtLink>
              </ScrollReveal>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- How it works — before packages so booking flow is clear first -->
    <section class="steps home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">How booking works</p>
          <h2>Three simple steps</h2>
        </header>
      </ScrollReveal>
      <ScrollReveal variant="up" :delay="120">
        <ol class="steps__compact" aria-label="Booking steps">
          <li v-for="step in flowSteps" :key="`compact-${step.title}`">
            <span class="steps__compact-num" aria-hidden="true">{{ step.num }}</span>
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.text }}</p>
            </div>
          </li>
        </ol>
      </ScrollReveal>
      <div class="steps__flow">
        <ScrollReveal
          v-for="(step, index) in flowSteps"
          :key="step.title"
          variant="up"
          :delay="100 + index * 120"
        >
          <MellisFlowStep
            :num="step.num"
            :title="step.title"
            :text="step.text"
            :image="step.image"
          />
        </ScrollReveal>
      </div>
    </section>

    <!-- Visit path — two doors only; catalogs live on /services -->
    <section id="visit-path" class="visit-path home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">Book a visit</p>
          <h2>How would you like to visit?</h2>
        </header>
      </ScrollReveal>
      <div class="visit-path__grid">
        <ScrollReveal variant="up" :delay="80">
          <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="visit-path__door">
            <p class="visit-path__days">Tue &amp; Wed</p>
            <h3 class="visit-path__title">Full glow days</h3>
            <p class="visit-path__text">One booking for facial, waxing, massage and makeup.</p>
            <span class="visit-path__action">See packages</span>
          </NuxtLink>
        </ScrollReveal>
        <ScrollReveal variant="up" :delay="160">
          <NuxtLink :to="SERVICES_ROUTES.singleSessions" class="visit-path__door">
            <p class="visit-path__days">{{ SINGLE_DAYS_LABEL }}</p>
            <h3 class="visit-path__title">Single sessions</h3>
            <p class="visit-path__text">Book one treatment when that is all you need today.</p>
            <span class="visit-path__action">See singles</span>
          </NuxtLink>
        </ScrollReveal>
      </div>
    </section>

    <!-- Featured package — copy + card band -->
    <section id="packages" class="packages home-section">
      <div class="packages__band">
        <ScrollReveal variant="up" :delay="40">
          <div class="packages__copy">
            <p class="label">Package days</p>
            <h2>Full visits, Tuesday &amp; Wednesday</h2>
            <p class="packages__sub">{{ packageDaySubhead }}</p>
            <p class="packages__note">{{ packageDayUrgency }}</p>
            <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="home-services-link packages__all">
              See all packages
            </NuxtLink>
          </div>
        </ScrollReveal>
        <div class="packages__card-wrap">
          <ScrollReveal
            v-for="(pkg, index) in featuredPackages"
            :key="pkg.name"
            variant="up"
            :delay="100 + index * 80"
          >
            <MellisPackageCard
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
          </ScrollReveal>
        </div>
      </div>
    </section>

    <!-- Testimonials — short proof for new clients (mobile + desktop) -->
    <section class="reviews home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">Client stories</p>
          <h2>What our clients say</h2>
          <p class="section-head__sub">Visits from Meru Town and across the county.</p>
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
            <div class="review-card__stars" aria-label="5 out of 5 stars">★★★★★</div>
            <p>{{ review.text }}</p>
            <footer>
              <img
                :src="review.photo"
                alt=""
                class="review-card__photo"
                width="56"
                height="56"
                loading="lazy"
                decoding="async"
              />
              <div>
                <cite>{{ review.name }}</cite>
                <span>Customer</span>
              </div>
            </footer>
          </blockquote>
        </ScrollReveal>
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
                <dd>7:00 am – 7:00 pm · singles</dd>
              </div>
              <div>
                <dt>Tue &amp; Wed</dt>
                <dd>7:00 am – 7:00 pm · packages</dd>
              </div>
              <div>
                <dt>Thu – Sat</dt>
                <dd>7:00 am – 7:00 pm · singles</dd>
              </div>
              <div>
                <dt>Sunday</dt>
                <dd>Closed</dd>
              </div>
            </dl>
            <p class="visit-map__place">{{ LANDING_LOCATION_LABEL }}</p>
            <div class="visit-map__actions">
              <SiteButton to="/services" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
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
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  flowSteps,
  getFeaturedPackages,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_MAPS_EMBED_URL,
  LANDING_MAPS_URL,
  LANDING_PRIMARY_CTA,
  packageDaySubhead,
  packageDayUrgency,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import { fetchHomeWorkGallery, STATIC_HOME_WORK } from '@/landing/homeWorkGallery'
import { HERO_COPY_FADE_MS, HERO_CROSSFADE_MS, HERO_CTA, HERO_FADE_MS, heroSlides, shouldMountHeroImage } from '@/landing/heroMedia'
import { useLandingSeo } from '@/landing/useLandingSeo'
import { bookHrefForPackageName } from '@/landing/bookingHandoff'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const config = useRuntimeConfig()

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

const offerShowcase = [
  { index: '01', label: 'Facials', perk: 'Deep cleansing facials', to: `${SERVICES_ROUTES.page}#facials` },
  { index: '02', label: 'Massage', perk: 'Hot stone massage', to: `${SERVICES_ROUTES.page}#massage` },
  { index: '03', label: 'Waxing', perk: 'Brow shaping', to: `${SERVICES_ROUTES.page}#waxing` },
  { index: '04', label: 'Makeup', perk: 'Bridal & event glam', to: `${SERVICES_ROUTES.page}#makeup` },
]

const reviews = [
  {
    name: 'Wanjiku M.',
    photo: '/images/testimonial-1.jpg',
    text: 'I come every month for a facial. My skin has improved and the room is always clean and quiet.',
  },
  {
    name: 'Sharon O.',
    photo: '/images/testimonial-2.jpg',
    text: 'Had my makeup done for a wedding. It stayed on all day and looked good in every photo.',
  },
  {
    name: 'Diana K.',
    photo: '/images/testimonial-3.jpg',
    text: 'The Saturday massage is something I look forward to each week. Easy to book and always on time.',
  },
]
</script>

<style scoped>
.home {
  background: var(--color-paper);
  margin: 0;
  padding: 0;
  /* Tight section rhythm — no dead white */
  --home-section-y: clamp(1.5rem, 3.5vh, 2.25rem);
  --home-section-y-lg: clamp(1.75rem, 4vh, 2.5rem);
  --home-head-gap: 1rem;
}

.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
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
  font-size: clamp(1.85rem, 4vw, 2.65rem);
  font-weight: 400;
  line-height: 1.2;
  letter-spacing: -0.01em;
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
  font-size: clamp(1.85rem, 3.5vw, 2.5rem);
  font-weight: 400;
  line-height: 1.25;
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
  /* Runway: ~50vh sticky hold while fixed photo stays put */
  min-height: 150vh;
  padding: 0;
  overflow: clip;
  background: #1c1714;
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
  transform: scale(1.03);
  transform-origin: 70% 40%;
}

.offer__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(18, 12, 12, 0.42) 0%,
      rgba(18, 12, 12, 0.28) 40%,
      rgba(18, 12, 12, 0.58) 100%
    ),
    linear-gradient(
      90deg,
      rgba(18, 12, 12, 0.28) 0%,
      rgba(18, 12, 12, 0.12) 50%,
      rgba(18, 12, 12, 0.24) 100%
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
  padding: clamp(3rem, 6vh, 5.5rem) 1.25rem;
}

.offer__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.35rem, 3vh, 2rem);
}

.offer__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem 1.5rem;
}

.offer__label {
  margin: 0;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #f5d8d0;
  text-shadow: 0 1px 14px rgba(0, 0, 0, 0.55);
}

.offer__board {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  /* Restored unified bar — stronger veil so copy stays readable */
  background: rgba(28, 16, 18, 0.78);
  border: 1px solid rgba(245, 216, 208, 0.32);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04) inset,
    0 18px 48px rgba(8, 4, 4, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.offer__board > li {
  min-width: 0;
}

.offer__board > li:nth-child(odd) .offer__cell {
  border-right: 1px solid rgba(255, 255, 255, 0.2);
}

.offer__board > li:nth-child(-n + 2) .offer__cell {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.offer__cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  min-height: 100%;
  padding: clamp(1.15rem, 2.8vw, 1.55rem) clamp(0.9rem, 2vw, 1.3rem);
  color: #fff;
  text-decoration: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.22s ease;
}

.offer__cell:hover,
.offer__cell:focus-visible {
  background: rgba(222, 150, 141, 0.16);
  outline: none;
}

.offer__cell:hover .offer__name,
.offer__cell:focus-visible .offer__name {
  color: #f0b8ac;
}

.offer__index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.75rem;
  height: 1.75rem;
  padding: 0 0.35rem;
  border: 1px solid rgba(240, 184, 172, 0.55);
  border-radius: 999px;
  background: rgba(222, 150, 141, 0.2);
  font: 600 0.64rem/1 var(--font-body);
  letter-spacing: 0.14em;
  color: #f5d8d0;
}

.offer__name {
  font-family: var(--font-display);
  font-size: clamp(1.7rem, 5.2vw, 2.3rem);
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: #fff;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.4);
  transition: color 0.2s ease;
}

.offer__detail {
  margin-top: 0.1rem;
  font: 400 0.88rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.9);
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.35);
}

.offer__cta {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.85rem 1.25rem;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  text-decoration: none;
  box-shadow: 0 10px 28px rgba(120, 48, 52, 0.35);
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.offer__cta:hover {
  background: var(--color-rose-dark);
  transform: translateY(-1px);
  box-shadow: 0 14px 32px rgba(120, 48, 52, 0.42);
}

.offer__cta-arrow {
  font-size: 1rem;
  line-height: 1;
  letter-spacing: 0;
  transition: transform 0.2s ease;
}

.offer__cta:hover .offer__cta-arrow {
  transform: translateX(0.2rem);
}

/* Phones: static chapter (no fixed sticky runway) — calmer scroll, less jank */
@media (max-width: 767px) {
  .offer {
    min-height: auto;
  }

  .offer__chapter {
    position: relative;
    top: auto;
    min-height: auto;
    padding: clamp(2.75rem, 7vh, 4.5rem) 1.15rem;
  }

  .offer__fixed {
    position: absolute;
    inset: 0;
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
    min-height: 155vh;
  }

  .offer__chapter {
    padding: clamp(3.5rem, 7vh, 6rem) 1.5rem;
  }

  .offer__photo {
    object-position: 68% 40%;
  }

  .offer__board {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .offer__board > li:nth-child(odd) .offer__cell,
  .offer__board > li:nth-child(-n + 2) .offer__cell {
    border-right: 0;
    border-bottom: 0;
  }

  .offer__board > li:not(:last-child) .offer__cell {
    border-right: 1px solid rgba(255, 255, 255, 0.22);
  }

  .offer__cell {
    padding: clamp(1.3rem, 2.6vh, 1.85rem) clamp(1rem, 1.5vw, 1.4rem);
    gap: 0.5rem;
  }

  .offer__name {
    font-size: clamp(1.8rem, 2.4vw, 2.35rem);
  }

  .offer__detail {
    font-size: 0.9rem;
    max-width: 14ch;
  }
}

@media (min-width: 1024px) {
  .offer {
    min-height: 158vh;
  }

  .offer__photo {
    object-position: 65% 38%;
  }

  .offer__name {
    font-size: clamp(1.95rem, 2.15vw, 2.5rem);
  }

  .offer__detail {
    font-size: 0.94rem;
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
    padding: clamp(3.25rem, 7vh, 7.5rem) 1.25rem;
  }

  .offer__fixed {
    position: absolute;
    inset: 0;
  }

  .offer__photo {
    transform: none;
  }

  .offer__cta:hover {
    transform: none;
  }
}

/* Steps — compact numbered list on phones; circle flow from tablet up */
.steps {
  padding: var(--home-section-y) 1.25rem;
  background: var(--color-paper);
}

.steps__compact {
  list-style: none;
  width: var(--container);
  margin: 0 auto;
  padding: 0;
  display: grid;
  gap: 0.75rem;
}

.steps__compact li {
  display: grid;
  grid-template-columns: 2.5rem 1fr;
  gap: 0.75rem;
  align-items: start;
  padding: 0.85rem 0.9rem;
  background: #fff;
  border: 1px solid var(--color-line);
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
  margin: 0.1rem 0 0.25rem;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-ink);
}

.steps__compact p {
  margin: 0;
  font: 400 0.84rem/1.45 var(--font-body);
  color: var(--color-muted);
}

.steps__flow {
  position: relative;
  width: var(--container);
  margin: 0 auto;
  display: none;
  grid-template-columns: 1fr;
  gap: 1.35rem;
  padding-top: 0.35rem;
}

.steps__flow::before {
  display: none;
}

@media (min-width: 768px) {
  .steps__compact {
    display: none;
  }

  .steps__flow {
    display: grid;
  }
}

/* Cut brochure filler on phones — keep booking path short */
@media (max-width: 767px) {
  .home-section--desktop-only {
    display: none !important;
  }
}

/* Packages — copy + featured card band */
.packages {
  position: relative;
  padding: var(--home-section-y) 1rem;
  background:
    linear-gradient(135deg, rgba(196, 140, 140, 0.08) 0%, transparent 42%),
    linear-gradient(180deg, var(--color-cream) 0%, var(--color-paper) 100%);
  overflow: hidden;
}

.packages::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 55% 70% at 92% 20%, rgba(196, 140, 140, 0.12), transparent 60%),
    radial-gradient(ellipse 40% 50% at 8% 85%, rgba(196, 140, 140, 0.06), transparent 55%);
  pointer-events: none;
}

.packages__band {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
  align-items: center;
}

.packages__copy h2 {
  margin: 0 0 0.85rem;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.5vw, 2.35rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
  max-width: 18ch;
}

.packages__sub {
  margin: 0 0 0.65rem;
  font: 400 0.98rem/1.55 var(--font-body);
  color: var(--color-muted);
  max-width: 36ch;
}

.packages__note {
  margin: 0 0 1.25rem;
  font: 500 0.82rem/1.45 var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-rose);
  max-width: 32ch;
}

.packages__all {
  display: inline-block;
}

.packages__card-wrap {
  min-width: 0;
  width: 100%;
  max-width: 26rem;
}

.packages__card-wrap > * {
  height: 100%;
}

@media (min-width: 768px) {
  .packages__band {
    grid-template-columns: 1fr minmax(16rem, 24rem);
    gap: clamp(1.75rem, 4vw, 3rem);
    align-items: center;
  }

  .packages__card-wrap {
    max-width: none;
    justify-self: stretch;
  }
}

@media (min-width: 1024px) {
  .packages__band {
    grid-template-columns: 1.05fr minmax(18rem, 26rem);
    gap: clamp(2.25rem, 5vw, 4rem);
  }
}

/* Visit path — two clear booking doors */
.visit-path {
  padding: var(--home-section-y) 1rem;
  background: var(--color-cream);
}

.visit-path__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.visit-path__grid > * {
  height: 100%;
  min-width: 0;
}

.visit-path__door {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  height: 100%;
  padding: 1.5rem 1.35rem;
  background: #fff;
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-rose);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

@media (hover: hover) {
  .visit-path__door:hover {
    border-color: var(--color-rose);
    box-shadow: 0 12px 32px rgba(39, 37, 42, 0.08);
  }

  .visit-path__door:hover .visit-path__action {
    color: var(--color-rose-dark);
  }
}

.visit-path__door:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

.visit-path__days {
  margin: 0 0 0.55rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.visit-path__title {
  margin: 0 0 0.55rem;
  font-family: var(--font-display);
  font-size: clamp(1.35rem, 3vw, 1.65rem);
  font-weight: 700;
  line-height: 1.2;
  color: var(--color-ink);
}

.visit-path__text {
  margin: 0 0 1.15rem;
  flex: 1;
  font: 400 0.95rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.visit-path__action {
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose);
}

@media (min-width: 768px) {
  .visit-path__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1.25rem;
  }
}

.reviews__grid > *,
.steps__flow > * {
  height: 100%;
  min-width: 0;
}

/* Reviews */
.reviews {
  padding: var(--home-section-y) 1rem;
}

.reviews__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.review-card {
  margin: 0;
  padding: 1.25rem 1.15rem;
  background: var(--color-cream);
  position: relative;
  height: 100%;
  transition: transform 0.35s var(--ease-story), box-shadow 0.35s;
}

.review-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(39, 37, 42, 0.08);
}

.review-card__stars {
  color: var(--color-rose);
  font-size: 0.8rem;
  letter-spacing: 0.15em;
  margin-bottom: 0.65rem;
}

.review-card p {
  margin: 0 0 1.1rem;
  font: 400 0.88rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.review-card footer {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.review-card__photo {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #fff;
  box-shadow: 0 4px 12px rgba(39, 37, 42, 0.1);
  flex-shrink: 0;
}

.review-card cite {
  display: block;
  font: 700 0.95rem var(--font-display);
  font-style: normal;
  color: var(--color-ink);
}

.review-card footer span {
  font: 400 0.82rem var(--font-body);
  color: var(--color-muted);
}

/* Our work — Pinterest-style masonry */
.work {
  padding: var(--home-section-y-lg) 1rem;
  background: var(--color-paper);
}

.work__masonry {
  width: var(--container);
  margin: 0 auto;
  column-count: 2;
  column-gap: 0.65rem;
}

.work__tile {
  display: block;
  break-inside: avoid;
  margin: 0 0 0.65rem;
  overflow: hidden;
  background: var(--color-cream);
  text-decoration: none;
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

/* Visit — split hours + clipped map */
.visit-map {
  padding: var(--home-section-y) 1rem;
  background: var(--color-cream);
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
  .packages,
  .visit-path,
  .visit-map {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .visit-path__door {
    padding: 1.35rem 1.25rem;
  }

  .reviews__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .review-card {
    padding: 1.35rem 1.25rem;
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

  .steps__flow {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.35rem;
  }

  .steps__flow::before {
    content: '';
    display: block;
    position: absolute;
    top: 80px;
    left: 18%;
    right: 18%;
    height: 2px;
    background: var(--color-rose-soft);
    z-index: 0;
  }

  .visit-path__door {
    padding: 1.25rem 1.2rem;
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
  .review-card {
    animation: none !important;
    transition: none !important;
  }

  .hero__bg {
    transform: none !important;
  }
}
</style>
