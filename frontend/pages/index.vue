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
        <Transition name="hero-copy">
          <div :key="currentHero.service" class="hero__copy">
            <img
              src="/images/logo-mark.png"
              alt=""
              class="hero__mark"
              width="48"
              height="48"
              aria-hidden="true"
            />
            <p class="hero__eyebrow">{{ currentHero.eyebrow }}</p>
            <h1 class="hero__title">{{ currentHero.headline }}</h1>
            <SiteButton :to="HERO_CTA.to" variant="primary" class="hero__cta">
              {{ HERO_CTA.label }}
            </SiteButton>
          </div>
        </Transition>
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

    <!-- Treatments — photo showcase; headline stays brand-simple -->
    <section id="services" class="services home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">The studio</p>
          <h2>Our treatments</h2>
        </header>
      </ScrollReveal>
      <div class="services__grid">
        <ScrollReveal
          v-for="(service, index) in services"
          :key="service.name"
          variant="up"
          :delay="100 + index * 90"
        >
          <MellisServiceCard
            :name="service.name"
            :image="service.image"
            :cta-to="service.ctaTo"
            cta-label="Explore"
          />
        </ScrollReveal>
      </div>
      <ScrollReveal variant="fade" :delay="160">
        <p class="services__footer">
          <NuxtLink to="/services" class="home-services-link">View packages and full pricing</NuxtLink>
        </p>
      </ScrollReveal>
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

    <!-- Featured packages only -->
    <section id="packages" class="packages home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <p class="label">Package days</p>
          <h2>Full visits, Tuesday &amp; Wednesday</h2>
        </header>
      </ScrollReveal>
      <div class="packages__grid packages__grid--featured">
        <ScrollReveal
          v-for="(pkg, index) in featuredPackages"
          :key="pkg.name"
          variant="up"
          :delay="80 + index * 100"
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
      <ScrollReveal variant="fade" :delay="120">
        <p class="packages__footer">
          <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="home-services-link">
            See all packages
          </NuxtLink>
        </p>
      </ScrollReveal>
    </section>

    <!-- More we do — desktop atmosphere band (hidden on phones to cut scroll) -->
    <section class="more home-section home-section--desktop-only">
      <div class="more__bg" aria-hidden="true">
        <img src="/images/more-bg.jpg" alt="" loading="lazy" decoding="async" width="1280" height="720" />
        <div class="more__bg-overlay" />
      </div>
      <div class="more__inner">
        <ScrollReveal variant="left" :delay="60">
          <div class="more__panel">
            <p class="label">The studio</p>
            <h2>A calm place to glow</h2>
            <ul class="more__list">
              <li v-for="item in serviceList" :key="item">{{ item }}</li>
            </ul>
            <SiteButton to="/services" variant="primary" class="more__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
            <p class="more__hint">Pay at checkout to confirm your slot.</p>
          </div>
        </ScrollReveal>
        <div class="more__stats">
          <ScrollReveal
            v-for="(stat, index) in stats"
            :key="stat.label"
            variant="scale"
            :delay="80 + index * 70"
          >
            <article class="stat-card">
              <img :src="stat.icon" alt="" width="48" height="48" loading="lazy" decoding="async" />
              <span class="stat-card__num">{{ stat.value }}</span>
              <span class="stat-card__label">{{ stat.label }}</span>
            </article>
          </ScrollReveal>
        </div>
      </div>
    </section>

    <!-- Testimonials — desktop only on phones (filler scroll) -->
    <section class="reviews home-section home-section--desktop-only">
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

    <!-- Gallery — desktop only on phones -->
    <section id="gallery" class="gallery home-section home-section--desktop-only">
      <ScrollReveal variant="fade">
        <header class="section-head section-head--light">
          <p class="label">On Instagram</p>
          <h2>@shee_aesthetics</h2>
        </header>
      </ScrollReveal>
      <div class="gallery__grid" aria-label="Studio photos">
        <ScrollReveal
          v-for="(img, index) in galleryImages"
          :key="img"
          variant="scale"
          :delay="40 + index * 50"
        >
          <a
            :href="LANDING_INSTAGRAM_URL"
            class="gallery__item"
            target="_blank"
            rel="noopener noreferrer"
            :aria-label="`View studio photo ${index + 1} on Instagram`"
          >
            <img :src="img" alt="" loading="lazy" decoding="async" width="400" height="400" />
          </a>
        </ScrollReveal>
      </div>
    </section>

    <!-- Hours CTA -->
    <section id="visit" class="cta home-section">
      <div class="cta__photo">
        <img src="/images/cta-bg.jpg" alt="" loading="lazy" decoding="async" width="1280" height="720" />
        <div class="cta__overlay" />
      </div>
      <ScrollReveal variant="up" :delay="60">
        <div class="cta__inner">
          <div class="cta__book">
            <h2>Ready when you are</h2>
            <SiteButton to="/services" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
          </div>
          <div class="cta__hours">
            <img src="/images/icon-clock.png" alt="" width="40" height="40" />
            <p class="label">Opening Hours</p>
            <div class="cta__hours-grid">
              <div>
                <h3>Monday</h3>
                <p>7:00 am – 7:00 pm · singles</p>
              </div>
              <div>
                <h3>Tue &amp; Wed</h3>
                <p>7:00 am – 7:00 pm · packages</p>
              </div>
              <div>
                <h3>Thu – Sat</h3>
                <p>7:00 am – 7:00 pm · singles</p>
              </div>
              <div>
                <h3>Sunday</h3>
                <p>Closed</p>
              </div>
            </div>
          </div>
        </div>
      </ScrollReveal>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  flowSteps,
  getFeaturedPackages,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import { HERO_COPY_FADE_MS, HERO_CROSSFADE_MS, HERO_CTA, HERO_FADE_MS, heroSlides, shouldMountHeroImage } from '@/landing/heroMedia'
import { useLandingSeo } from '@/landing/useLandingSeo'
import { getServiceSummaries } from '@/landing/servicesContent'
import { bookHrefForPackageName } from '@/landing/bookingHandoff'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const activeSlide = ref(0)
const mountedHeroSlides = computed(() => {
  const set = new Set<number>()
  heroSlides.forEach((_, index) => {
    if (shouldMountHeroImage(activeSlide.value, index, heroSlides.length)) {
      set.add(index)
    }
  })
  return set
})

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

const services = getServiceSummaries()
const featuredPackages = getFeaturedPackages()

const serviceList = [
  'Deep Cleansing Facials',
  'Hot Stone Massage',
  'Full Body Waxing',
  'Bridal Makeup',
  'Back & Shoulder Massage',
  'Brow Shaping',
  'Skin Brightening',
  'Event Glam',
]

const stats = [
  { value: '4', label: 'Treatments in one studio', icon: '/images/icon-counter-2.png' },
  { value: '2', label: 'Days for full packages', icon: '/images/icon-counter-4.png' },
  { value: '6', label: 'Days open weekly', icon: '/images/icon-counter-1.png' },
  { value: 'M-Pesa', label: 'Pay at checkout', icon: '/images/icon-counter-3.png' },
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

const galleryImages = [
  '/images/gallery-1.jpg',
  '/images/gallery-2.jpg',
  '/images/gallery-3.jpg',
  '/images/gallery-4.jpg',
  '/images/gallery-5.jpg',
  '/images/gallery-6.jpg',
]

definePageMeta({ layout: 'landing' })

useLandingSeo()
</script>

<style scoped>
.home {
  background: var(--color-paper);
  margin: 0;
  padding: 0;
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
  margin: 0 auto 1.35rem;
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
  height: min(78svh, 40rem);
  height: min(78dvh, 40rem);
  min-height: 28rem;
  overflow: hidden;
  background: var(--color-ink);
  --hero-crossfade-ms: 1800ms;
  --hero-copy-fade-ms: 1100ms;
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
  transform: scale(1.05);
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
  background: rgba(39, 37, 42, 0.3);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding:
    1.5rem
    1.25rem
    calc(var(--mobile-book-bar-height, 4.25rem) + 3rem);
  color: #fff;
  pointer-events: none;
}

.hero__copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  max-width: 100%;
  position: relative;
}

.hero__content :deep(.site-btn) {
  pointer-events: auto;
}

.hero-copy-enter-active,
.hero-copy-leave-active {
  transition:
    opacity var(--hero-copy-fade-ms) cubic-bezier(0.22, 1, 0.36, 1),
    transform var(--hero-copy-fade-ms) cubic-bezier(0.22, 1, 0.36, 1);
}

.hero-copy-leave-active {
  position: absolute;
  inset-inline: 0;
  margin-inline: auto;
}

.hero-copy-enter-from {
  opacity: 0;
  transform: translateY(16px);
}

.hero-copy-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}

.hero__mark {
  display: block;
  width: 2.75rem;
  height: 2.75rem;
  margin: 0 0 0.85rem;
  object-fit: contain;
  filter: brightness(0) invert(1);
  opacity: 0.95;
}

.hero__eyebrow {
  margin: 0 0 0.55rem;
  font-family: var(--font-body);
  font-size: 0.72rem;
  font-weight: 700;
  line-height: 1.3;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.95);
}

.hero__title {
  margin: 0 0 1.35rem;
  max-width: 14ch;
  font-family: var(--font-script);
  font-size: clamp(2.75rem, 11vw, 4.75rem);
  font-weight: 400;
  line-height: 1.05;
  letter-spacing: 0.01em;
  color: #fff;
  text-align: center;
  text-shadow: 0 2px 28px rgba(20, 16, 18, 0.35);
}

.hero__cta {
  display: inline-flex;
  min-height: 2.85rem;
  padding: 0.9rem 1.85rem !important;
  border-radius: 0 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.16em !important;
}

.hero__dots {
  position: absolute;
  left: 50%;
  bottom: calc(var(--mobile-book-bar-height, 4.25rem) + 2.75rem);
  z-index: 4;
  display: flex;
  gap: 0.45rem;
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
  padding: clamp(2rem, 5vh, 3.5rem) 1rem clamp(2rem, 5vh, 3.5rem);
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
  gap: 2rem;
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

/* Treatments — photo showcase (not a list of names in the headline) */
.services {
  padding: clamp(2.5rem, 6vh, 4rem) 1rem;
  background: var(--color-cream);
}

.services__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem 0.85rem;
}

.services__footer {
  width: var(--container);
  margin: 1.75rem auto 0;
  text-align: center;
}

/* More — standout band with visible spa photo */
.more {
  position: relative;
  padding: clamp(2.25rem, 5vh, 3.75rem) 1rem;
  overflow: hidden;
  border-top: 4px solid var(--color-rose);
  border-bottom: 4px solid var(--color-rose);
}

.more__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.more__bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
}

.more__bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    rgba(252, 245, 245, 0.97) 0%,
    rgba(255, 255, 255, 0.9) 42%,
    rgba(39, 37, 42, 0.45) 100%
  );
}

.more__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}

.more__panel {
  background: #fff;
  border-left: 4px solid var(--color-rose);
  padding: clamp(1.75rem, 4vw, 2.5rem);
  box-shadow: 0 24px 64px rgba(39, 37, 42, 0.14);
  max-width: 34rem;
}

.more__panel h2 {
  margin: 0 0 1.5rem;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4.5vw, 2.55rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
}

.more__cta {
  width: 100%;
  max-width: 16rem;
}

.more__hint {
  margin: 1rem 0 0;
  font: 500 0.8rem/1.5 var(--font-body);
  color: var(--color-muted);
  letter-spacing: 0.02em;
}

.more__list {
  columns: 1;
  column-gap: 2rem;
  list-style: none;
  margin: 0 0 1.5rem;
  padding: 0;
}

.more__list li {
  position: relative;
  padding-left: 1.1rem;
  margin-bottom: 0.85rem;
  font: 500 0.92rem var(--font-body);
  break-inside: avoid;
}

.more__list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-rose);
}

.more__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.stat-card {
  background: #fff;
  padding: 1.1rem 1rem;
  text-align: center;
  border: 1px solid rgba(222, 150, 141, 0.25);
  box-shadow: 0 8px 24px rgba(39, 37, 42, 0.08);
  height: 100%;
  transition: transform 0.35s var(--ease-story), box-shadow 0.35s;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(39, 37, 42, 0.1);
}

.stat-card img {
  margin: 0 auto 1rem;
  display: block;
}

.stat-card__num {
  display: block;
  font: 700 clamp(1.35rem, 4vw, 2.25rem)/1.1 var(--font-display);
  color: var(--color-ink);
}

.stat-card__label {
  display: block;
  margin-top: 0.5rem;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-muted);
}

/* Steps — compact numbered list on phones; circle flow from tablet up */
.steps {
  padding: clamp(2rem, 5vh, 3.5rem) 1.25rem;
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

/* Packages */
.packages {
  padding: clamp(2rem, 5vh, 3.5rem) 1rem;
  background: var(--color-paper);
}

.packages__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  align-items: stretch;
  padding-top: 0.85rem;
}

.packages__grid--featured {
  max-width: 26rem;
  margin-left: auto;
  margin-right: auto;
}

.packages__grid > * {
  min-width: 0;
  height: 100%;
}

.packages__footer {
  width: var(--container);
  margin: 1.5rem auto 0;
  text-align: center;
}

/* Visit path — two clear booking doors */
.visit-path {
  padding: clamp(2.25rem, 5vh, 3.75rem) 1rem;
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

.services__grid > *,
.reviews__grid > *,
.more__stats > *,
.steps__flow > *,
.gallery__grid > * {
  height: 100%;
  min-width: 0;
}

/* Reviews */
.reviews {
  padding: clamp(2rem, 5vh, 3.5rem) 1rem;
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

/* Gallery — static grid (no infinite scroll animation) */
.gallery {
  padding: clamp(2.25rem, 5vh, 3.75rem) 0;
  background: var(--color-footer);
}

.gallery .section-head {
  padding: 0 1.5rem;
}

.gallery__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  width: var(--container);
  max-width: 100%;
  margin: 2rem auto 0;
  padding: 0 1rem;
}

.gallery__item {
  display: block;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 2px;
}

.gallery__item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

@media (min-width: 768px) {
  .gallery__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .gallery__grid {
    grid-template-columns: repeat(6, 1fr);
    gap: 1rem;
  }
}

/* CTA */
.cta {
  position: relative;
  padding: clamp(2.5rem, 6vh, 4rem) 1.5rem;
  overflow: hidden;
}

.cta__photo {
  position: absolute;
  inset: 0;
}

.cta__photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cta__overlay {
  position: absolute;
  inset: 0;
  background: rgba(39, 37, 42, 0.82);
}

.cta__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
  color: #fff;
}

.cta__book h2 {
  margin: 0 0 2rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.5vw, 2.65rem);
  font-weight: 400;
  line-height: 1.25;
  color: #fff;
  max-width: 16ch;
}

.cta__hours .label {
  color: var(--color-rose);
}

.cta__hours-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.cta__hours-grid h3 {
  margin: 0 0 0.25rem;
  font: 700 0.95rem var(--font-body);
  color: #fff;
}

.cta__hours-grid p {
  margin: 0;
  font: 400 0.88rem var(--font-body);
  color: rgba(255, 255, 255, 0.75);
}

/* Tablet and up — progressive enhancement */
@media (min-width: 640px) {
  .cta__hours-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (min-width: 768px) {
  .hero {
    height: min(72vh, 42rem);
    min-height: 30rem;
  }

  .hero__content {
    padding: 2rem 1.5rem 3.25rem;
  }

  .hero__dots {
    bottom: 2.75rem;
  }

  .hero__title {
    font-size: clamp(3.5rem, 6vw, 5.5rem);
  }

  .hero__eyebrow {
    font-size: 0.78rem;
  }

  .section-head {
    margin-bottom: 1.75rem;
  }

  .welcome {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .welcome__inner {
    gap: clamp(2rem, 5vw, 4.5rem);
  }

  .welcome__mirror {
    width: min(320px, 42vw);
  }

  .welcome__flower {
    right: -1rem;
    width: min(130px, 30%);
  }

  .services,
  .reviews,
  .packages,
  .visit-path {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .services__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.35rem;
  }

  .packages__grid {
    grid-template-columns: 1fr;
    gap: 1.15rem;
  }

  .reviews__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .review-card {
    padding: 1.35rem 1.25rem;
  }

  .more__inner {
    grid-template-columns: 1.15fr 1fr;
    gap: 3rem;
  }

  .more__cta {
    width: auto;
  }

  .more__list {
    columns: 2;
    margin-bottom: 2rem;
  }

  .cta__inner {
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
  }
}

@media (min-width: 1024px) {
  .hero {
    height: min(78vh, 46rem);
    min-height: 34rem;
  }

  .welcome__inner {
    grid-template-columns: 1fr 1fr;
  }

  .services__grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
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

  .packages__grid:not(.packages__grid--featured) {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
  }

  .packages__grid--featured {
    grid-template-columns: 1fr;
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
  .hero-copy-enter-active,
  .hero-copy-leave-active,
  .stat-card,
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
