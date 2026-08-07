<template>
  <SiteLoader />
  <main class="home">
    <LandingHero />

    <!-- Get to know us — content first on mobile; Mellis oval left on desktop -->
    <section id="behind-the-glow" class="glow home-section" aria-labelledby="glow-heading">
      <div class="glow__inner">
        <div class="glow__copy">
          <p class="glow__eyebrow">{{ GLOW_SECTION_EYEBROW }}</p>
          <h2 id="glow-heading" class="glow__heading">{{ GLOW_SECTION_HEADING }}</h2>
          <p class="glow__text">{{ GLOW_SECTION_TEXT }}</p>
          <p class="glow__artist">
            <span class="glow__name">{{ GLOW_ARTIST_NAME }}</span>
            <span class="glow__line">{{ GLOW_ARTIST_LINE }}</span>
          </p>
          <a
            class="glow__continue"
            :href="GLOW_CONTINUE_HASH"
            @click="scrollToGlowWork"
          >
            {{ GLOW_CONTINUE_LABEL }}
          </a>
        </div>
        <div class="glow__media">
          <div class="glow__flower-sketch" aria-hidden="true">
            <svg viewBox="0 0 240 280" fill="none" xmlns="http://www.w3.org/2000/svg" class="glow__flower-svg">
              <path d="M120 270 C110 210 95 160 75 110 C65 85 45 60 20 40 C38 65 50 95 55 130 C60 165 65 210 70 270" stroke="#c88478" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.65"/>
              <path d="M115 200 C140 180 175 170 210 165 C180 185 150 210 125 240" stroke="#c88478" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
              <path d="M80 120 C65 90 85 60 115 40 C105 70 95 98 80 120 Z" stroke="#c88478" stroke-width="1.5" fill="rgba(230, 165, 152, 0.15)" stroke-linecap="round" opacity="0.7"/>
              <path d="M115 40 C140 22 180 28 200 58 C170 65 140 82 115 105 C110 82 112 58 115 40 Z" stroke="#c88478" stroke-width="1.5" fill="rgba(230, 165, 152, 0.18)" stroke-linecap="round" opacity="0.7"/>
              <path d="M80 120 C50 128 25 150 10 180 C32 168 60 156 90 148" stroke="#c88478" stroke-width="1.5" stroke-linecap="round" opacity="0.55"/>
              <circle cx="110" cy="72" r="3.5" fill="#c88478" opacity="0.75"/>
              <circle cx="128" cy="60" r="3" fill="#c88478" opacity="0.75"/>
              <circle cx="142" cy="78" r="3" fill="#c88478" opacity="0.75"/>
            </svg>
          </div>
          <div class="glow__accent-circle" aria-hidden="true" />
          <figure class="glow__mirror">
            <img
              src="/images/therapist.png"
              alt="Shee, beauty artist and founder at Shee Aesthetics"
              class="glow__photo"
              loading="lazy"
              decoding="async"
              width="480"
              height="600"
            />
          </figure>
        </div>
      </div>
    </section>

    <!-- Our work — Pinterest masonry; primary proof for new clients -->
    <section id="our-work" class="work home-section">
      <ScrollReveal variant="up">
        <header class="section-head">
          <div class="title-lockup">
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--left"
              width="64"
              height="64"
              loading="lazy"
              decoding="async"
              aria-hidden="true"
            />
            <h2>Clients by Shee</h2>
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--right"
              width="64"
              height="64"
              loading="lazy"
              decoding="async"
              aria-hidden="true"
            />
          </div>
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
          <InstagramLink class="work__ig" />
        </p>
      </ScrollReveal>
    </section>

    <!-- Treatments — dark chapter with soft massage photo atmosphere -->
    <section id="services" class="offer home-section">
      <div class="offer__bg" aria-hidden="true">
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
      <div class="offer__chapter">
        <div class="offer__inner">
          <header class="offer__head">
            <div class="title-lockup title-lockup--on-dark">
              <img
                src="/images/flower.png"
                alt=""
                class="title-lockup__flower title-lockup__flower--left"
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
                class="title-lockup__flower title-lockup__flower--right"
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
                <span class="offer__cta-meta">Facial, wax, massage &amp; makeup · from {{ LANDING_PACKAGE_FLOOR_SHORT }}</span>
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
    <section class="steps home-section home-floral">
      <!-- Soft edge orchids — transparent line art, visible but quiet -->
      <img
        src="/images/flower-edge.png"
        alt=""
        class="home-floral__edge home-floral__edge--bl"
        width="200"
        height="160"
        loading="lazy"
        decoding="async"
        aria-hidden="true"
      />
      <img
        src="/images/flower-edge.png"
        alt=""
        class="home-floral__edge home-floral__edge--br"
        width="200"
        height="160"
        loading="lazy"
        decoding="async"
        aria-hidden="true"
      />
      <ScrollReveal variant="up">
        <header class="section-head">
          <div class="title-lockup">
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--left"
              width="64"
              height="64"
              loading="lazy"
              decoding="async"
              aria-hidden="true"
            />
            <h2>How booking works</h2>
            <img
              src="/images/flower.png"
              alt=""
              class="title-lockup__flower title-lockup__flower--right"
              width="64"
              height="64"
              loading="lazy"
              decoding="async"
              aria-hidden="true"
            />
          </div>
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

    <!-- Book a visit — flat paper; photos only on visit doors -->
    <section id="visit-path" class="book-visit home-section">
      <div class="book-visit__path">
        <img
          src="/images/flower-edge.png"
          alt=""
          class="home-floral__edge home-floral__edge--bl"
          width="180"
          height="145"
          loading="lazy"
          decoding="async"
          aria-hidden="true"
        />
        <img
          src="/images/flower-edge.png"
          alt=""
          class="home-floral__edge home-floral__edge--br"
          width="180"
          height="145"
          loading="lazy"
          decoding="async"
          aria-hidden="true"
        />

        <div class="book-visit__path-inner">
          <ScrollReveal variant="up">
            <header class="book-visit__head">
              <div class="title-lockup">
                <img
                  src="/images/flower.png"
                  alt=""
                  class="title-lockup__flower title-lockup__flower--left"
                  width="64"
                  height="64"
                  loading="lazy"
                  decoding="async"
                  aria-hidden="true"
                />
                <h2>How would you like to visit?</h2>
                <img
                  src="/images/flower.png"
                  alt=""
                  class="title-lockup__flower title-lockup__flower--right"
                  width="64"
                  height="64"
                  loading="lazy"
                  decoding="async"
                  aria-hidden="true"
                />
              </div>
            </header>
          </ScrollReveal>

          <div class="book-visit__doors">
          <ScrollReveal variant="up" :delay="80">
            <NuxtLink
              :to="packagesVisitHref"
              class="visit-card visit-card--dark"
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
              <span class="visit-card__wash" aria-hidden="true" />
              <span class="visit-card__pattern" aria-hidden="true" />
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
                <span class="visit-card__meta">{{ LANDING_PACKAGE_FLOOR }}</span>
                <span class="visit-card__cta">Book now</span>
              </span>
            </NuxtLink>
          </ScrollReveal>

          <ScrollReveal variant="up" :delay="160">
            <NuxtLink
              :to="treatmentsVisitHref"
              class="visit-card visit-card--photo"
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
              <span class="visit-card__wash visit-card__wash--photo" aria-hidden="true" />
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
                <span class="visit-card__meta">{{ LANDING_TREATMENT_FLOOR }}</span>
                <span class="visit-card__cta">Book now</span>
              </span>
            </NuxtLink>
          </ScrollReveal>
          </div>
        </div>
      </div>

      <div id="packages" class="book-visit__stage">
          <div class="mellis-cta__atmosphere" aria-hidden="true">
            <img
              src="/images/hero-makeup.jpg"
              alt=""
              class="mellis-cta__bg"
              width="1280"
              height="1600"
              loading="lazy"
              decoding="async"
            />
            <span class="mellis-cta__veil" />
          </div>

          <div class="mellis-cta__content">
            <ScrollReveal variant="up" :delay="40">
              <header class="mellis-cta__head">
                <div class="title-lockup title-lockup--on-dark">
                  <img
                    src="/images/flower.png"
                    alt=""
                    class="title-lockup__flower title-lockup__flower--left"
                    width="64"
                    height="64"
                    loading="lazy"
                    decoding="async"
                    aria-hidden="true"
                  />
                  <h2>Full packages</h2>
                  <img
                    src="/images/flower.png"
                    alt=""
                    class="title-lockup__flower title-lockup__flower--right"
                    width="64"
                    height="64"
                    loading="lazy"
                    decoding="async"
                    aria-hidden="true"
                  />
                </div>
              </header>
            </ScrollReveal>

            <div class="mellis-cta__card-wrap packages__band">
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
            <p class="mellis-cta__note">{{ LANDING_FEATURED_PACKAGE_CLARIFIER }}</p>
            <p class="mellis-cta__note mellis-cta__note--soft">{{ packageDayUrgency }}</p>
          </div>
      </div>
    </section>

    <!-- Client reviews — Mellis-style proof cards (no reviewer photos) -->
    <section class="reviews home-section home-floral" aria-labelledby="reviews-heading">
      <img
        src="/images/flower-edge.png"
        alt=""
        class="home-floral__edge home-floral__edge--tl"
        width="160"
        height="130"
        loading="lazy"
        decoding="async"
        aria-hidden="true"
      />
      <img
        src="/images/flower-edge.png"
        alt=""
        class="home-floral__edge home-floral__edge--br"
        width="180"
        height="145"
        loading="lazy"
        decoding="async"
        aria-hidden="true"
      />
      <div class="reviews__inner">
        <ScrollReveal variant="up">
          <header class="reviews__head">
            <div class="title-lockup">
              <img
                src="/images/flower.png"
                alt=""
                class="title-lockup__flower title-lockup__flower--left"
                width="64"
                height="64"
                loading="lazy"
                decoding="async"
                aria-hidden="true"
              />
              <h2 id="reviews-heading">What clients say</h2>
              <img
                src="/images/flower.png"
                alt=""
                class="title-lockup__flower title-lockup__flower--right"
                width="64"
                height="64"
                loading="lazy"
                decoding="async"
                aria-hidden="true"
              />
            </div>
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

    <LandingVisit />

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
          <SiteButton
            v-if="primaryCtaIsExternal"
            :href="primaryCtaHref"
            variant="primary"
            @click="closeWorkLightbox"
          >
            Book this vibe
          </SiteButton>
          <SiteButton
            v-else
            :to="primaryCtaHref"
            variant="primary"
            @click="closeWorkLightbox"
          >
            Book this vibe
          </SiteButton>
          <InstagramLink variant="light" />
        </div>
      </div>
    </Teleport>
  </main>
</template>

<script setup lang="ts">
/**
 * Homepage composition (marketing only).
 * Section order: hero → Get to know us → Clients by Shee → offer → packages → reviews → visit.
 * Data helpers live under `src/landing/` — keep Django as the API, not Nuxt server routes.
 */
import { computed, ref } from 'vue'
import {
  flowSteps,
  getFeaturedPackages,
  LANDING_FEATURED_PACKAGE_CLARIFIER,
  LANDING_PACKAGE_FLOOR,
  LANDING_PACKAGE_FLOOR_SHORT,
  LANDING_TREATMENT_FLOOR,
  landingClientReviews,
  packageDayUrgency,
  GLOW_SECTION_EYEBROW,
  GLOW_SECTION_HEADING,
  GLOW_SECTION_TEXT,
  GLOW_ARTIST_NAME,
  GLOW_ARTIST_LINE,
  GLOW_CONTINUE_LABEL,
  GLOW_CONTINUE_HASH,
} from '@/landing/landingContent'
import { fetchHomeWorkGallery, STATIC_HOME_WORK, type HomeWorkImage } from '@/landing/homeWorkGallery'
import {
  defaultTreatmentBookHref,
  featuredPackageBookHref,
} from '@/landing/bookCtaTargets'
import { useLandingSeo } from '@/landing/useLandingSeo'
import { useLandingContact } from '@/landing/useLandingContact'
import { bookHrefForPackageName } from '@/landing/bookingHandoff'
import {
  primaryBookHref,
  primaryBookHrefKind,
  primaryBookIsExternal,
} from '@/landing/primaryBookHref'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const config = useRuntimeConfig()
const contact = useLandingContact()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl

definePageMeta({ layout: 'landing' })
useLandingSeo()

const { data: workGallery } = await useAsyncData(
  'home-work-gallery',
  () => fetchHomeWorkGallery(String(config.public.apiBaseUrl || '')),
  { default: () => STATIC_HOME_WORK },
)
const workImages = computed(() => (workGallery.value ?? STATIC_HOME_WORK).slice(0, 8))

const packagesVisitHref = featuredPackageBookHref()
const treatmentsVisitHref = defaultTreatmentBookHref()

const primaryCtaHref = computed(() =>
  primaryBookHref(new Date(), {
    contactIsLive: contactIsLive.value,
    whatsappUrl: whatsappUrl.value,
  }),
)
const primaryCtaIsExternal = computed(() => primaryBookIsExternal(primaryCtaHref.value))

const lightboxImage = ref<HomeWorkImage | null>(null)

function openWorkLightbox(img: HomeWorkImage) {
  lightboxImage.value = img
  trackFunnelEvent('gallery_open', { id: img.id })
}

function closeWorkLightbox() {
  lightboxImage.value = null
}

function scrollToGlowWork(event: Event) {
  event.preventDefault()
  const el = document.getElementById('our-work')
  if (!el) return
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' })
  if (import.meta.client) {
    window.history.replaceState(null, '', '#our-work')
  }
}

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
  --home-seam: 1px solid rgba(44, 44, 48, 0.05);
}

.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

/**
 * Edge orchid accents — transparent line art at section corners.
 * Quiet enough not to compete with copy; visible enough to read as design.
 */
.home-floral {
  overflow: hidden;
}

.home-floral__edge {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  width: min(11rem, 34vw);
  height: auto;
  opacity: 0.28;
  filter: saturate(0.95) contrast(1.02);
}

.home-floral__edge--on-photo {
  opacity: 0.5;
  filter: saturate(1.05) contrast(1.02) drop-shadow(0 2px 10px rgba(255, 255, 255, 0.35));
}

.home-floral__edge--br {
  right: 0.75rem;
  bottom: 0.35rem;
  transform: rotate(8deg);
}

.home-floral__edge--bl {
  left: 0.75rem;
  bottom: 0.35rem;
  width: min(13rem, 40vw);
  transform: rotate(-12deg) scaleX(-1);
}

.home-floral__edge--tr {
  top: 0.45rem;
  right: 0.85rem;
  width: min(11rem, 34vw);
  transform: rotate(16deg) scaleX(-1);
}

.home-floral__edge--tl {
  top: 0.45rem;
  left: 0.85rem;
  width: min(11rem, 34vw);
  transform: rotate(-14deg);
}

.home-floral > :not(.home-floral__edge) {
  position: relative;
  z-index: 1;
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

/* Spa orchid flanks — complimentary to every quiet header */
.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.65rem, 2.2vw, 1.15rem);
  max-width: 100%;
}

.title-lockup h2 {
  margin: 0;
  flex: 0 1 auto;
  min-width: 0;
}

.title-lockup__flower {
  width: clamp(2.85rem, 6.5vw, 3.85rem);
  height: auto;
  flex-shrink: 0;
  opacity: 0.78;
  pointer-events: none;
  user-select: none;
}

.title-lockup__flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.title-lockup__flower--right {
  transform: rotate(8deg);
}

.title-lockup--on-dark .title-lockup__flower {
  opacity: 1;
  filter: brightness(1.22) saturate(1.35) drop-shadow(0 0 10px rgba(240, 184, 172, 0.35));
}

.title-lockup--start {
  justify-content: flex-start;
}

@media (max-width: 479px) {
  .title-lockup__flower {
    width: clamp(1.55rem, 7.5vw, 2rem);
    opacity: 0.68;
  }

  .title-lockup {
    gap: 0.4rem;
  }

  .title-lockup h2 {
    font-size: clamp(1.55rem, 7.2vw, 1.95rem);
  }
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

/* Get to know us — content-first mobile; Mellis oval frame; desktop image-left */
.glow {
  position: relative;
  z-index: 1;
  margin-top: -1px;
  padding: clamp(1.75rem, 5vw, 3.25rem) 1rem clamp(1.5rem, 4vw, 2.5rem);
  overflow: hidden;
  background: var(--color-paper);
}

.glow__inner {
  width: var(--container);
  max-width: 64rem;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.65rem;
  align-items: center;
  justify-items: center;
  text-align: center;
}

.glow__copy {
  min-width: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  order: 1;
}

.glow__media {
  position: relative;
  width: min(100%, 22rem);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  order: 2;
}

.glow__flower-sketch {
  position: absolute;
  left: -18%;
  bottom: -6%;
  width: clamp(7.5rem, 42%, 10.5rem);
  pointer-events: none;
  z-index: 0;
  opacity: 0.9;
}

.glow__flower-svg {
  width: 100%;
  height: auto;
  display: block;
}

.glow__accent-circle {
  position: absolute;
  right: -8%;
  bottom: -4%;
  width: clamp(5.5rem, 32%, 7.5rem);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, #f7d8d0 0%, #e8a99d 68%, #d89689 100%);
  box-shadow: 0 10px 28px rgba(216, 150, 137, 0.28);
  z-index: 1;
  pointer-events: none;
}

/* Mellis Theme vertical oval — soft frame, white rim, botanical accents */
.glow__mirror {
  position: relative;
  z-index: 2;
  margin: 0;
  width: min(100%, 22rem);
  aspect-ratio: 4 / 5;
  padding: 0;
  border-radius: 50% / 46%;
  overflow: hidden;
  background: #ebe4de;
  border: 4px solid #fff;
  box-shadow:
    0 18px 42px rgba(39, 37, 42, 0.16),
    0 0 0 1px rgba(222, 150, 141, 0.22);
}

.glow__photo {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center 16%;
  border-radius: 50% / 46%;
  background: #ebe4de;
}

.glow__eyebrow {
  margin: 0 0 0.45rem;
  font: 700 0.68rem/1.3 var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.glow__heading {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 5.5vw, 2.35rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.glow__text {
  margin: 0.7rem auto 0;
  max-width: 36ch;
  font: 400 0.95rem/1.6 var(--font-body);
  color: var(--color-muted);
}

.glow__artist {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  margin: 0.95rem 0 0;
}

.glow__name {
  font-family: var(--font-script);
  font-size: clamp(1.55rem, 4vw, 1.95rem);
  font-weight: 400;
  line-height: 1.05;
  color: var(--color-rose-dark, #b56b62);
}

.glow__line {
  font: 600 0.7rem/1.35 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.glow__continue {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 1.1rem;
  min-height: 2.75rem;
  min-width: 11rem;
  padding: 0.65rem 1.4rem;
  font: 700 0.7rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  text-decoration: none;
  color: #fff;
  background: var(--color-rose);
  transition: background 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.glow__continue:hover,
.glow__continue:focus-visible {
  background: var(--color-rose-dark, #b56b62);
  outline: none;
}

.glow__continue:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

@media (min-width: 900px) {
  .glow {
    padding: clamp(2.25rem, 4.5vw, 3.5rem) 1.5rem clamp(1.75rem, 3.5vw, 2.75rem);
  }

  .glow__inner {
    grid-template-columns: 24rem minmax(0, 1fr);
    gap: clamp(2rem, 4vw, 3.5rem);
    justify-items: start;
    text-align: left;
    align-items: center;
  }

  /* Desktop: Mellis oval left, story right */
  .glow__media {
    order: 1;
    width: 24rem;
    margin: 0;
  }

  .glow__copy {
    order: 2;
    align-items: flex-start;
    text-align: left;
  }

  .glow__mirror {
    width: 24rem;
  }

  .glow__flower-sketch {
    left: -22%;
    bottom: -8%;
    width: 11.5rem;
  }

  .glow__accent-circle {
    width: 8rem;
    right: -12%;
    bottom: -6%;
  }

  .glow__text {
    margin-left: 0;
    margin-right: 0;
    max-width: 38ch;
  }

  .glow__artist {
    align-items: flex-start;
  }

  .glow__heading {
    font-size: clamp(2rem, 2.6vw, 2.55rem);
  }
}

/* Treatments — Mellis static-bg scroll chapter + colored Shee board */
.offer.home-section {
  content-visibility: visible;
  contain-intrinsic-size: none;
}

.offer {
  position: relative;
  padding: 0;
  overflow: hidden;
  background: var(--color-card-dark);
  border-block: var(--home-seam);
}

.offer__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.offer__photo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 70% 40%;
  transform: scale(1.04);
  /* Keep enough tone so the massage scene holds attention under the veil */
  filter: grayscale(0.18) contrast(1.08) brightness(0.88) saturate(0.92);
}

.offer__veil {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      180deg,
      rgba(28, 18, 22, 0.58) 0%,
      rgba(22, 16, 18, 0.42) 38%,
      rgba(18, 14, 15, 0.62) 100%
    ),
    linear-gradient(
      90deg,
      rgba(28, 18, 22, 0.32) 0%,
      rgba(18, 14, 15, 0.12) 48%,
      rgba(28, 18, 22, 0.28) 100%
    );
}

.offer__chapter {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  padding: clamp(3.5rem, 8vh, 6rem) 1.25rem;
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

.offer__head .title-lockup {
  padding: 0.35rem 0 0.5rem;
  gap: clamp(0.85rem, 2.4vw, 1.6rem);
}

.offer__head .title-lockup h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2.65rem, 7.5vw, 4.15rem);
  font-weight: 500;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: #fff;
  text-shadow: none;
}

.offer__head .title-lockup__flower {
  width: clamp(2.9rem, 7vw, 4.25rem);
  opacity: 1;
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
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(245, 216, 208, 0.18);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  cursor: pointer;
  transition:
    background 0.25s ease,
    border-color 0.25s ease,
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease;
}

.offer__cell:hover,
.offer__cell:focus-visible {
  background: rgba(176, 122, 113, 0.28);
  border-color: rgba(245, 216, 208, 0.45);
  transform: translateY(-4px);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
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
  text-shadow: none;
  transition: color 0.2s ease;
}

.offer__detail {
  margin: 0;
  font: 400 0.82rem/1.4 var(--font-body);
  color: rgba(255, 245, 240, 0.88);
  text-shadow: none;
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
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  transition:
    transform 0.25s var(--ease-story, ease),
    box-shadow 0.25s ease,
    filter 0.25s ease;
}

.offer__cta:hover,
.offer__cta:focus-visible {
  transform: translateY(-3px);
  filter: brightness(1.05);
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
  background: var(--color-surface-raised);
  color: var(--color-ink);
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  box-shadow: none;
  transition: transform 0.2s ease, background 0.2s ease;
}

.offer__cta:hover .offer__cta-action,
.offer__cta:focus-visible .offer__cta-action {
  background: var(--color-paper);
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
  .offer__chapter {
    padding: clamp(3.25rem, 8vh, 5rem) 1.15rem;
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

}

/* Narrow phones — stack offer board for readable copy */
@media (max-width: 419px) {
  .offer__board {
    grid-template-columns: 1fr;
    gap: 0.7rem;
  }

  .offer__cell {
    min-height: 7.5rem;
    padding: 1.15rem 1.05rem 1.05rem;
  }
}

@media (min-width: 768px) {
  .offer__chapter {
    padding: clamp(4rem, 9vh, 6.5rem) 1.5rem;
  }

  .offer__inner {
    gap: clamp(2.15rem, 5vh, 3.25rem);
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
  .offer__head .title-lockup h2 {
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

@media (prefers-reduced-motion: reduce) {
  .offer__cell:hover,
  .offer__cell:focus-visible,
  .offer__cta:hover,
  .offer__cta:focus-visible {
    transform: none;
    filter: none;
  }
}

/* Steps — quiet parchment + one soft edge orchid */
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
  background: var(--color-surface-raised);
  border: 1px solid rgba(176, 122, 113, 0.12);
  box-shadow: none;
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

/* Book a visit — soft photo atmosphere; visit cards carry the visual weight */
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
  background: var(--color-paper);
}

.book-visit__path > .home-floral__edge {
  z-index: 0;
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
  max-width: 42rem;
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
  text-shadow: none;
}

.book-visit__doors {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

.book-visit__doors > * {
  min-width: 0;
  height: 100%;
}

.visit-card {
  position: relative;
  display: block;
  min-height: 18rem;
  overflow: hidden;
  text-decoration: none;
  color: #f4ebe6;
  background: var(--color-card-dark);
  box-shadow: 0 14px 32px rgba(23, 21, 22, 0.18);
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
  object-position: center 28%;
  transform: scale(1.02);
  transition: transform 0.7s var(--ease-story, ease);
}

.visit-card__media--mono {
  filter: grayscale(0.92) contrast(1.1) brightness(0.68);
  object-position: center 22%;
}

.visit-card__wash {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      105deg,
      rgba(22, 16, 18, 0.9) 0%,
      rgba(22, 16, 18, 0.72) 40%,
      rgba(22, 16, 18, 0.42) 70%,
      rgba(22, 16, 18, 0.28) 100%
    );
  pointer-events: none;
}

.visit-card__wash--photo {
  background:
    linear-gradient(
      105deg,
      rgba(24, 16, 20, 0.88) 0%,
      rgba(28, 18, 22, 0.62) 36%,
      rgba(28, 18, 22, 0.28) 64%,
      rgba(18, 14, 15, 0.12) 100%
    );
}

.visit-card__pattern {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.42;
  background-image: url('/images/flower.png');
  background-size: 6.25rem;
  background-repeat: repeat;
  filter: saturate(1.55) brightness(1.2) contrast(1.05);
  mix-blend-mode: soft-light;
}

.visit-card__badge {
  position: absolute;
  top: 1.1rem;
  right: 1.1rem;
  z-index: 3;
  display: grid;
  place-content: center;
  width: 4.25rem;
  height: 4.25rem;
  padding: 0.3rem;
  border-radius: 50%;
  text-align: center;
  color: #fff;
  background: var(--color-rose);
  box-shadow: 0 8px 18px rgba(176, 122, 113, 0.28);
}

.visit-card__badge--today {
  background: var(--color-rose-dark);
}

.visit-card__badge-line {
  display: block;
  font: 700 0.64rem/1.2 var(--font-body);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.visit-card__body {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.45rem;
  min-height: 18rem;
  max-width: 17rem;
  padding: 1.6rem 1.35rem 1.6rem 1.5rem;
}

.visit-card__title {
  margin: 0;
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 4.5vw, 2.7rem);
  font-weight: 400;
  line-height: 1;
  color: #f8f2ee;
}

.visit-card__text {
  max-width: 20ch;
  font: 500 0.9rem/1.45 var(--font-body);
  color: rgba(244, 235, 230, 0.8);
}

.visit-card__meta {
  font: 700 0.7rem/1.3 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #f0b8ac;
}

.visit-card__cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.55rem;
  min-height: 2.6rem;
  min-width: 8.5rem;
  padding: 0.65rem 1.4rem;
  font: 700 0.7rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #fff;
  background: var(--color-rose);
  border: 0;
  box-shadow: none;
}

.visit-card--focus {
  box-shadow: 0 18px 40px rgba(23, 21, 22, 0.28);
}

.visit-card:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

@media (hover: hover) {
  .visit-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 20px 42px rgba(23, 21, 22, 0.3);
  }

  .visit-card:hover .visit-card__media {
    transform: scale(1.05);
  }

  .visit-card:hover .visit-card__cta {
    background: var(--color-rose-dark);
  }
}

/* Full packages — services warm charcoal stage; white featured card pops */
.book-visit__stage {
  position: relative;
  isolation: isolate;
  margin-top: 0;
  padding: clamp(2.5rem, 6vw, 3.75rem) 1rem clamp(2.25rem, 5vw, 3.25rem);
  overflow: hidden;
  border-block: var(--home-seam);
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(222, 150, 141, 0.2), transparent 60%),
    linear-gradient(180deg, #2a2324 0%, #221c1e 48%, #1a1718 100%);
}

.mellis-cta__atmosphere {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.28;
  overflow: hidden;
}

.mellis-cta__bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 22%;
  transform: scale(1.04);
  opacity: 0.55;
  filter: grayscale(0.35) contrast(1.05) brightness(0.72) saturate(0.85);
}

.mellis-cta__veil {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    radial-gradient(
      ellipse 48% 52% at 50% 45%,
      rgba(34, 28, 30, 0.35) 0%,
      rgba(26, 23, 24, 0.72) 55%,
      rgba(26, 23, 24, 0.92) 100%
    ),
    linear-gradient(
      180deg,
      rgba(42, 35, 36, 0.55) 0%,
      rgba(26, 23, 24, 0.35) 40%,
      rgba(26, 23, 24, 0.85) 100%
    );
}

.mellis-cta__content {
  position: relative;
  z-index: 2;
}

.mellis-cta__head {
  text-align: center;
  max-width: 36rem;
  margin: 0 auto 1.75rem;
}

.mellis-cta__head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: #fff8f4;
  text-shadow: none;
}

.mellis-cta__card-wrap {
  position: relative;
  width: min(100%, 26rem);
  margin: 0 auto;
  padding-top: 0.65rem;
}

.mellis-cta__card {
  position: relative;
  z-index: 3;
  /* Let featured white / services charcoal styles win — do not force dark */
  box-shadow:
    0 22px 48px rgba(0, 0, 0, 0.35),
    0 0 0 1px rgba(222, 150, 141, 0.2);
}

@media (max-width: 479px) {
  .book-visit__stage {
    padding-inline: 0.85rem;
  }

  .mellis-cta__head h2 {
    font-size: clamp(1.75rem, 8vw, 2.1rem);
  }

  .visit-card__badge {
    width: 4rem;
    height: 4rem;
    top: 0.95rem;
    right: 0.95rem;
  }

  .visit-card__badge-line {
    font-size: 0.64rem;
  }

}

.mellis-cta__note {
  margin: 1.1rem auto 0;
  max-width: 28rem;
  text-align: center;
  font: 500 0.8rem/1.45 var(--font-body);
  color: #f0b8ac;
  text-shadow: none;
}

.mellis-cta__note--soft {
  margin-top: 0.35rem;
  color: rgba(255, 248, 244, 0.58);
}

@media (min-width: 768px) {
  .book-visit__doors {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
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

/* Reviews — quiet parchment + one soft corner orchid */
.reviews {
  position: relative;
  padding: clamp(2.5rem, 5.5vh, 3.5rem) 1rem;
  overflow: hidden;
  border-block: var(--home-seam);
  background: var(--color-parchment);
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
  background: var(--color-surface-raised);
  border: 1px solid rgba(176, 122, 113, 0.12);
  box-shadow: none;
  transition: transform 0.35s var(--ease-story, ease);
}

.review-card:hover {
  transform: translateY(-3px);
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

/* Our work — quiet paper; tight seam after Meet your therapist */
.work {
  padding: clamp(1.35rem, 3.5vw, 2.25rem) 1rem var(--home-section-y-lg);
  background: var(--color-paper);
  border-bottom: var(--home-seam);
  scroll-margin-top: calc(var(--site-header-height, 4rem) + 0.5rem);
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

.work__ig {
  margin-inline: auto;
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

/* Tablet and up — progressive enhancement */
@media (min-width: 768px) {
  .home {
    --home-section-y: 2rem;
    --home-section-y-lg: 2.25rem;
    --home-head-gap: 0.95rem;
  }

  .work,
  .reviews {
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

  .reviews__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.15rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .package-card,
  .review-card,
  .book-visit__door,
  .book-visit__door-media,
  .visit-card,
  .visit-card__media {
    animation: none !important;
    transition: none !important;
  }
}
</style>
