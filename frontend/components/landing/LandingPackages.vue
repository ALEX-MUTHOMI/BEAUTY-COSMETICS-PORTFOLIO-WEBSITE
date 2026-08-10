<template>
  <!-- Book a visit — flat paper; photos only on visit doors + packages stage -->
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
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  getFeaturedPackages,
  LANDING_FEATURED_PACKAGE_CLARIFIER,
  LANDING_PACKAGE_FLOOR,
  LANDING_TREATMENT_FLOOR,
  packageDayUrgency,
} from '@/landing/landingContent'
import {
  defaultTreatmentBookHref,
  featuredPackageBookHref,
} from '@/landing/bookCtaTargets'
import { bookHrefForPackageName } from '@/landing/bookingHandoff'
import { primaryBookHrefKind } from '@/landing/primaryBookHref'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const packagesVisitHref = featuredPackageBookHref()
const treatmentsVisitHref = defaultTreatmentBookHref()
const featuredPackages = getFeaturedPackages()

/** Day bias for visit doors — matches sticky/header Book href logic. */
const visitFocus = computed(() => primaryBookHrefKind())
</script>

<style scoped>
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
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
  filter: grayscale(1) contrast(1.15) brightness(0.65);
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
  opacity: 0.48;
  filter: grayscale(1) contrast(1.18) brightness(0.62);
}

.mellis-cta__veil {
  position: absolute;
  inset: 0;
  z-index: 1;
  background:
    radial-gradient(
      ellipse 50% 55% at 50% 45%,
      rgba(18, 14, 15, 0.42) 0%,
      rgba(18, 14, 15, 0.82) 60%,
      rgba(18, 14, 15, 0.96) 100%
    ),
    linear-gradient(
      180deg,
      rgba(34, 28, 29, 0.7) 0%,
      rgba(18, 14, 15, 0.45) 40%,
      rgba(18, 14, 15, 0.9) 100%
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
  .book-visit__path {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

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

  .visit-card__body {
    padding: 1.55rem 1.35rem 1.6rem 1.5rem;
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

@media (prefers-reduced-motion: reduce) {
  .package-card,
  .book-visit__door,
  .book-visit__door-media,
  .visit-card,
  .visit-card__media {
    animation: none !important;
    transition: none !important;
  }
}
</style>
