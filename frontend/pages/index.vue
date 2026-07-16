<template>
  <SiteLoader />
  <main class="home">
    <!-- Hero slider -->
    <section class="hero" @touchstart.passive="onHeroTouchStart" @touchend.passive="onHeroTouchEnd">
      <div class="hero__track">
        <article
          v-for="(slide, index) in heroSlides"
          :key="slide.image"
          class="hero__slide"
          :class="{ 'hero__slide--active': activeSlide === index }"
        >
          <img
            v-if="heroLoadedSlides.has(index)"
            :src="slide.image"
            :alt="slide.alt"
            class="hero__bg"
            :loading="index === 0 ? 'eager' : 'lazy'"
            :fetchpriority="index === 0 ? 'high' : 'auto'"
            decoding="async"
            width="1400"
            height="788"
          />
          <div class="hero__overlay" />
        </article>
      </div>
      <div class="hero__content">
        <p class="hero__eyebrow">{{ currentHero.eyebrow }}</p>
        <h1 class="hero__title">{{ currentHero.title }}</h1>
        <p v-if="currentHero.subtitle" class="hero__subtitle">{{ currentHero.subtitle }}</p>
        <SiteButton :to="currentHero.ctaTo" variant="primary">{{ currentHero.cta }}</SiteButton>
      </div>
      <ol class="hero__pager" aria-label="Hero slides">
        <li v-for="(_, index) in heroSlides" :key="index">
          <button
            type="button"
            class="hero__pager-dot"
            :class="{ 'hero__pager-dot--active': activeSlide === index }"
            :aria-label="`Go to slide ${index + 1}`"
            :aria-current="activeSlide === index ? 'true' : undefined"
            @click="goToSlide(index)"
          />
        </li>
      </ol>
    </section>

    <!-- Welcome -->
    <section id="welcome" class="welcome home-section">
      <div class="welcome__inner">
        <div class="welcome__media-wrap">
          <div class="welcome__media">
            <div class="welcome__mirror" aria-hidden="true">
              <img src="/images/welcome.jpg" alt="Spa treatment room with candles and warm lighting" class="welcome__photo" loading="lazy" decoding="async" width="800" height="800" />
            </div>
            <img src="/images/flower.png" alt="" class="welcome__flower" aria-hidden="true" loading="lazy" decoding="async" width="100" height="100" />
          </div>
        </div>
        <div class="welcome__copy">
            <p class="label">{{ LANDING_LOCATION_LABEL }}</p>
            <h2>Your hour to unwind</h2>
            <p class="welcome__text">
              A private studio for facials, waxing, massage and makeup. Soft light, clean rooms,
              and therapists who take their time with every client.
            </p>
            <div class="welcome__offers">
              <NuxtLink :to="SERVICES_ROUTES.fullPackages" class="welcome__offer-btn">
                <img src="/images/icon-offer.png" alt="" width="46" height="46" />
                <div>
                  <h3>Full glow days</h3>
                  <p>Tuesday and Wednesday. Facial, waxing, massage and makeup in one relaxed visit.</p>
                  <span class="welcome__offer-action">See packages</span>
                </div>
              </NuxtLink>
              <NuxtLink :to="SERVICES_ROUTES.singleSessions" class="welcome__offer-btn">
                <img src="/images/icon-gift.png" alt="" width="48" height="48" />
                <div>
                  <h3>Single sessions</h3>
                  <p>Monday and Thursday through Saturday when you only need one treatment today.</p>
                  <span class="welcome__offer-action">See singles</span>
                </div>
              </NuxtLink>
            </div>
            <SiteButton to="/services" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
          </div>
      </div>
    </section>

    <!-- Services -->
    <section id="services" class="services home-section">
      <header class="section-head">
        <p class="label">Our treatments</p>
        <h2>Facials, waxing, massage &amp; makeup</h2>
        <p class="section-head__sub">
          <NuxtLink to="/services" class="home-services-link">View packages and full pricing</NuxtLink>
        </p>
      </header>
      <div class="services__grid">
        <MellisServiceCard
          v-for="service in services"
          :key="service.name"
          :name="service.name"
          :text="service.text"
          :image="service.image"
          :icon="service.icon"
          :cta-to="service.ctaTo"
        />
      </div>
    </section>

    <!-- Full packages — after services for mobile booking flow -->
    <section id="packages" class="packages home-section">
      <header class="section-head">
        <p class="label">Package days</p>
        <h2>Full visits, Tuesday &amp; Wednesday</h2>
        <p class="section-head__sub">One private room. Every treatment done while you unwind.</p>
      </header>
      <div class="packages__grid">
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

    <!-- Single treatments -->
    <section id="singles" class="packages packages--singles home-section">
      <header class="section-head">
        <p class="label">Single treatments</p>
        <h2>Book one specific treatment</h2>
        <p class="section-head__sub">
          {{ SINGLE_DAYS_LABEL }}. Pick the exact treatment you want — or
          <NuxtLink :to="SERVICES_ROUTES.singleSessions" class="home-services-link">
            browse every single treatment and price
          </NuxtLink>.
        </p>
      </header>
      <div class="packages__grid packages__grid--singles">
        <MellisPackageCard
          v-for="treatment in singleHighlights"
          :key="treatment.name"
          :name="treatment.name"
          :text="treatment.description"
          :price="treatment.price"
          :includes="treatment.highlights"
          :days-label="SINGLE_DAYS_LABEL"
          :cta-label="`Book ${treatment.name}`"
          :cta-to="bookHrefForTreatment(treatment.category, treatment.name)"
          :details-to="`${SERVICES_ROUTES.page}#${treatment.category}`"
          details-label="See all options"
        />
      </div>
    </section>

    <!-- How it works — Mellis flow -->
    <section class="steps home-section">
      <header class="section-head">
        <p class="label">How booking works</p>
        <h2>Three simple steps</h2>
      </header>
      <div class="steps__flow">
        <MellisFlowStep
          v-for="step in flowSteps"
          :key="step.title"
          :num="step.num"
          :title="step.title"
          :text="step.text"
          :image="step.image"
        />
      </div>
    </section>

    <!-- More we do -->
    <section class="more home-section">
      <div class="more__bg" aria-hidden="true">
        <img src="/images/more-bg.jpg" alt="" loading="lazy" decoding="async" width="1280" height="720" />
        <div class="more__bg-overlay" />
      </div>
      <div class="more__inner">
        <div class="more__panel">
            <p class="label">The studio</p>
            <h2>Everything you need in one calm visit</h2>
            <ul class="more__list">
              <li v-for="item in serviceList" :key="item">{{ item }}</li>
            </ul>
            <SiteButton to="/services" variant="primary" class="more__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
            <p class="more__hint">Prices are listed above. Pay at checkout to confirm your slot.</p>
          </div>
        <div class="more__stats">
          <article v-for="stat in stats" :key="stat.label" class="stat-card">
            <img :src="stat.icon" alt="" width="48" height="48" loading="lazy" decoding="async" />
            <span class="stat-card__num">{{ stat.value }}</span>
            <span class="stat-card__label">{{ stat.label }}</span>
          </article>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="reviews home-section">
      <header class="section-head">
        <p class="label">Client stories</p>
        <h2>What our clients say</h2>
        <p class="section-head__sub">Visits from Meru Town and across the county. Facials, waxing, massage and makeup.</p>
      </header>
      <div class="reviews__grid">
        <blockquote v-for="review in reviews" :key="review.name" class="review-card">
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
      </div>
    </section>

    <!-- Gallery -->
    <section id="gallery" class="gallery home-section">
      <header class="section-head section-head--light">
        <p class="label">On Instagram</p>
        <h2>@shee_aesthetics</h2>
      </header>
      <div class="gallery__grid" aria-label="Studio photos">
        <a
          v-for="(img, index) in galleryImages"
          :key="img"
          :href="LANDING_INSTAGRAM_URL"
          class="gallery__item"
          target="_blank"
          rel="noopener noreferrer"
          :aria-label="`View studio photo ${index + 1} on Instagram`"
        >
          <img :src="img" alt="" loading="lazy" decoding="async" width="400" height="400" />
        </a>
      </div>
    </section>

    <!-- Hours CTA -->
    <section id="visit" class="cta home-section">
      <div class="cta__photo">
        <img src="/images/cta-bg.jpg" alt="" loading="lazy" decoding="async" width="1280" height="720" />
        <div class="cta__overlay" />
      </div>
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
                <p>9:00 am – 6:00 pm</p>
              </div>
              <div>
                <h3>Tue &amp; Wed</h3>
                <p>Full packages only</p>
              </div>
              <div>
                <h3>Thu – Sat</h3>
                <p>8:00 am – 7:00 pm</p>
              </div>
              <div>
                <h3>Sunday</h3>
                <p>Closed</p>
              </div>
            </div>
          </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  flowSteps,
  heroSlides,
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
  packages,
  SINGLE_DAYS_LABEL,
} from '@/landing/landingContent'
import { useLandingSeo } from '@/landing/useLandingSeo'
import { getServiceSummaries, getSingleTreatmentHighlights } from '@/landing/servicesContent'
import { bookHrefForPackageName, bookHrefForTreatment } from '@/landing/bookingHandoff'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const activeSlide = ref(0)
const heroLoadedSlides = ref(new Set<number>([0]))
let heroTouchStartX = 0

const currentHero = computed(() => heroSlides[activeSlide.value] ?? heroSlides[0]!)

function markHeroSlideLoaded(index: number) {
  heroLoadedSlides.value = new Set([...heroLoadedSlides.value, index])
}

function onHeroTouchStart(e: TouchEvent) {
  heroTouchStartX = e.changedTouches[0]?.clientX ?? 0
}

function onHeroTouchEnd(e: TouchEvent) {
  const endX = e.changedTouches[0]?.clientX ?? 0
  const delta = heroTouchStartX - endX
  if (Math.abs(delta) < 48) return
  if (delta > 0) {
    goToSlide((activeSlide.value + 1) % heroSlides.length)
  } else {
    goToSlide((activeSlide.value - 1 + heroSlides.length) % heroSlides.length)
  }
}

function goToSlide(index: number) {
  activeSlide.value = index
  markHeroSlideLoaded(index)
}

onMounted(() => {
  const preloadRest = () => {
    heroSlides.forEach((_, index) => markHeroSlideLoaded(index))
  }
  if ('requestIdleCallback' in window) {
    requestIdleCallback(preloadRest, { timeout: 5000 })
  } else {
    setTimeout(preloadRest, 2500)
  }
})

const services = getServiceSummaries()
const singleHighlights = getSingleTreatmentHighlights()

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
  font-size: clamp(1.65rem, 3.5vw, 2.35rem);
  font-weight: 400;
  line-height: 1.25;
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

/* Hero — mobile-first, edge-to-edge */
.hero {
  position: relative;
  width: 100%;
  height: min(72svh, 560px);
  min-height: 380px;
  overflow: hidden;
  touch-action: pan-y;
  background: var(--color-ink);
}

.hero::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: clamp(3rem, 12vw, 5rem);
  background: linear-gradient(to bottom, transparent, var(--color-paper));
  z-index: 2;
  pointer-events: none;
}

.hero__track {
  height: 100%;
  position: relative;
}

.hero__slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.35s ease, visibility 0.35s;
}

.hero__slide--active {
  opacity: 1;
  visibility: visible;
  z-index: 1;
}

.hero__bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(39, 37, 42, 0.42) 0%, rgba(39, 37, 42, 0.28) 45%, rgba(39, 37, 42, 0.62) 100%);
}

.hero__content {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  text-align: center;
  padding: 1.5rem 1.25rem clamp(3.5rem, 10vw, 4.5rem);
  color: #fff;
  pointer-events: none;
}

.hero__content :deep(.site-btn) {
  pointer-events: auto;
}

.hero__eyebrow {
  margin: 0 0 0.5rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.hero__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-script);
  font-size: clamp(2.65rem, 13vw, 8rem);
  font-weight: 400;
  line-height: 1;
  color: #fff;
}

.hero__subtitle {
  max-width: 36ch;
  margin: 0 0 1.75rem;
  font: 400 1rem/1.65 var(--font-body);
  color: rgba(255, 255, 255, 0.88);
}

.hero__pager {
  position: absolute;
  bottom: clamp(1.25rem, 4vw, 2rem);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.45rem;
  list-style: none;
  margin: 0;
  padding: 0.35rem 0.65rem;
  z-index: 4;
  border-radius: 999px;
  background: rgba(39, 37, 42, 0.22);
  backdrop-filter: blur(6px);
}

.hero__pager-dot {
  display: block;
  width: 7px;
  height: 7px;
  padding: 0;
  border: none;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.45);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: width 0.2s ease, background-color 0.2s ease;
}

.hero__pager-dot:hover {
  background: rgba(255, 255, 255, 0.75);
}

.hero__pager-dot--active {
  width: 1.35rem;
  background: var(--color-rose) !important;
}

/* Welcome — mobile-first single column */
.welcome {
  padding: clamp(2rem, 5vh, 3.5rem) 1rem;
  position: relative;
  z-index: 1;
}

@media (max-width: 767px) {
  .welcome {
    padding-top: clamp(1.75rem, 5vh, 2.5rem);
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

.welcome__offers {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
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

.welcome__offer-btn {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  width: 100%;
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-rose);
  background: #fff;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

@media (hover: hover) {
  .welcome__offer-btn {
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .welcome__offer-btn:hover {
    border-color: var(--color-rose);
    box-shadow: 0 10px 28px rgba(39, 37, 42, 0.08);
  }
}

.welcome__offer-btn:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.welcome__offer-btn h3 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-ink);
}

.welcome__offer-btn p {
  margin: 0;
  font: 400 0.88rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.welcome__offer-action {
  display: inline-block;
  margin-top: 0.65rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
}

/* Services — Mellis open grid, no boxed cards */
.services {
  padding: clamp(2rem, 5vh, 3.5rem) 1rem;
  background: var(--color-paper);
}

.services__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.35rem;
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

/* Steps — Mellis circle flow */
.steps {
  padding: clamp(2.25rem, 5vh, 3.75rem) 1.25rem;
  background: var(--color-paper);
}

.steps__flow {
  position: relative;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.35rem;
  padding-top: 0.35rem;
}

.steps__flow::before {
  display: none;
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
  gap: 1.1rem;
  align-items: stretch;
  padding-top: 0.85rem;
}

.packages__grid > * {
  min-width: 0;
}

.packages--singles {
  background: var(--color-cream);
}

.packages__grid--singles {
  grid-template-columns: 1fr;
  padding-top: 0.85rem;
}

.packages__grid--singles > * {
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
  .welcome__offers {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .cta__hours-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (min-width: 768px) {
  .hero {
    height: min(68svh, 560px);
    min-height: 420px;
  }

  .hero__content {
    justify-content: center;
    padding: 2rem 1.5rem 3rem;
  }

  .hero__eyebrow {
    font-size: 0.85rem;
    letter-spacing: 0.32em;
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
  .packages {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .services__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.35rem;
  }

  .packages__grid,
  .packages__grid--singles {
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
    height: min(620px, 72vh);
    min-height: 440px;
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

  .packages__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
  }

  .packages__grid--singles {
    grid-template-columns: repeat(4, 1fr);
    gap: 1.1rem;
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
  .stat-card,
  .package-card,
  .review-card {
    animation: none !important;
    transition: none !important;
  }
}
</style>
