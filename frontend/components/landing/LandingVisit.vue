<template>
  <!-- Visit — hours + Google Maps (client path: book / get directions) -->
  <section id="visit" class="visit-map home-section home-floral" aria-labelledby="visit-heading">
    <img
      src="/images/flower-edge.png"
      alt=""
      class="home-floral__edge home-floral__edge--tl"
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

    <div class="visit-map__shell">
      <header class="visit-map__intro">
        <div class="title-lockup">
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
          <h2 id="visit-heading">Visit us</h2>
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

      <div class="visit-map__inner">
        <ScrollReveal variant="up" :delay="40">
          <div class="visit-map__card">
            <div class="visit-map__card-head">
              <h3 class="visit-map__card-title">Opening Hours</h3>
              <img
                src="/images/icon-clock.png"
                alt=""
                width="40"
                height="40"
                class="visit-map__clock"
                loading="lazy"
                decoding="async"
              />
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
                <dd class="visit-map__closed">Closed</dd>
              </div>
            </dl>
            <p class="visit-map__place">
              <svg class="visit-map__pin" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
                <path
                  fill="currentColor"
                  d="M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"
                />
              </svg>
              <span>{{ LANDING_LOCATION_LABEL }}</span>
            </p>
            <div class="visit-map__actions">
              <SiteButton
                v-if="primaryCtaIsExternal"
                :href="primaryCtaHref"
                variant="primary"
                class="visit-map__book"
              >
                {{ LANDING_PRIMARY_CTA }}
              </SiteButton>
              <SiteButton
                v-else
                :to="primaryCtaHref"
                variant="primary"
                class="visit-map__book"
              >
                {{ LANDING_PRIMARY_CTA }}
              </SiteButton>
              <a
                :href="LANDING_MAPS_DIRECTIONS_URL"
                class="visit-map__maps visit-map__maps--primary"
                target="_blank"
                rel="noopener noreferrer"
                @click="trackFunnelEvent('cta_book_click', { surface: 'visit_directions', href: LANDING_MAPS_DIRECTIONS_URL })"
              >
                Get directions
              </a>
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
            </div>
          </div>
        </ScrollReveal>

        <ScrollReveal variant="up" :delay="100">
          <div class="visit-map__map-panel">
            <div class="visit-map__frame-wrap">
              <iframe
                class="visit-map__frame"
                title="Shee Aesthetics on Google Maps — Meru Town"
                :src="LANDING_MAPS_EMBED_URL"
                loading="lazy"
                referrerpolicy="no-referrer-when-downgrade"
                allowfullscreen
              />
            </div>
            <a
              :href="LANDING_MAPS_URL"
              class="visit-map__map-caption"
              target="_blank"
              rel="noopener noreferrer"
              @click="trackFunnelEvent('cta_book_click', { surface: 'visit_open_maps', href: LANDING_MAPS_URL })"
            >
              <span>Open in Google Maps</span>
              <span class="visit-map__map-caption-arrow" aria-hidden="true">→</span>
            </a>
          </div>
        </ScrollReveal>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  LANDING_LOCATION_LABEL,
  LANDING_MAPS_DIRECTIONS_URL,
  LANDING_MAPS_EMBED_URL,
  LANDING_MAPS_URL,
  LANDING_PRIMARY_CTA,
} from '@/landing/landingContent'
import { useLandingContact } from '@/landing/useLandingContact'
import { primaryBookHref, primaryBookIsExternal } from '@/landing/primaryBookHref'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const contact = useLandingContact()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel

const primaryCtaHref = computed(() =>
  primaryBookHref(new Date(), {
    contactIsLive: contactIsLive.value,
    whatsappUrl: whatsappUrl.value,
  }),
)
const primaryCtaIsExternal = computed(() => primaryBookIsExternal(primaryCtaHref.value))
</script>

<style scoped>
/* Shared floral/title utilities (scoped copy — required inside this SFC). */
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

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

.home-floral__edge--br {
  right: 0.75rem;
  bottom: 0.35rem;
  transform: rotate(8deg);
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

/* Visit — floral atmosphere + hours card + Google Maps panel */
.visit-map {
  position: relative;
  padding: var(--home-section-y-lg) 1rem;
  background:
    radial-gradient(
      ellipse 70% 55% at 12% 18%,
      rgba(240, 184, 172, 0.14) 0%,
      transparent 58%
    ),
    radial-gradient(
      ellipse 55% 50% at 88% 82%,
      rgba(176, 122, 113, 0.1) 0%,
      transparent 55%
    ),
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-paper) 88%, var(--color-rose-soft)) 0%,
      var(--color-paper) 42%,
      color-mix(in srgb, var(--color-paper) 92%, var(--color-cream)) 100%
    );
  border-block: var(--home-seam);
  overflow: hidden;
}

.visit-map__shell {
  width: var(--container);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(1.15rem, 2.8vw, 1.65rem);
}

.visit-map__intro {
  text-align: center;
  margin: 0 auto;
}

.visit-map__intro .title-lockup {
  justify-content: center;
  margin-bottom: 0;
}

.visit-map__intro .title-lockup h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5.5vw, 2.85rem);
  font-weight: 500;
  letter-spacing: -0.03em;
  color: var(--color-ink);
}

.visit-map__inner {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
  align-items: stretch;
}

.visit-map__card {
  position: relative;
  height: 100%;
  padding: clamp(1.55rem, 4vw, 2.05rem) clamp(1.25rem, 3.5vw, 1.75rem) clamp(1.45rem, 3.5vw, 1.75rem);
  background:
    linear-gradient(
      165deg,
      color-mix(in srgb, var(--color-surface-raised) 92%, #fff) 0%,
      var(--color-surface-raised) 100%
    );
  border: 1px solid rgba(176, 122, 113, 0.14);
  box-shadow: 0 14px 34px rgba(44, 44, 48, 0.07);
  overflow: hidden;
}

.visit-map__card::before {
  content: '';
  position: absolute;
  right: -1.25rem;
  bottom: -1.5rem;
  width: 7.5rem;
  height: 7.5rem;
  background-image: url('/images/flower.png');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.12;
  filter: saturate(1.15);
  pointer-events: none;
}

.visit-map__card-head {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.35rem;
}

.visit-map__card-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.45rem, 3.2vw, 1.85rem);
  font-weight: 500;
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.visit-map__clock {
  width: 2.25rem;
  height: 2.25rem;
  object-fit: contain;
  flex-shrink: 0;
  opacity: 0.88;
}

.visit-map__hours {
  position: relative;
  z-index: 1;
  margin: 0 0 1.25rem;
}

.visit-map__hours > div {
  margin-bottom: 0.95rem;
}

.visit-map__hours > div:last-child {
  margin-bottom: 0;
}

.visit-map__hours dt {
  margin: 0 0 0.22rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.visit-map__hours dd {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.02rem, 2.4vw, 1.18rem);
  font-weight: 400;
  color: var(--color-rose);
  line-height: 1.35;
}

.visit-map__closed {
  color: var(--color-rose-dark);
  font-weight: 500;
}

.visit-map__place {
  position: relative;
  z-index: 1;
  display: inline-flex;
  align-items: flex-start;
  gap: 0.45rem;
  margin: 0 0 1.2rem;
  font: 500 0.9rem/1.4 var(--font-body);
  color: var(--color-deep);
}

.visit-map__pin {
  flex-shrink: 0;
  margin-top: 0.12rem;
  color: var(--color-rose);
}

.visit-map__actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.45rem;
}

.visit-map__book {
  width: 100%;
}

.visit-map__maps {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  padding: 0.45rem 0.85rem;
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
  text-decoration: none;
  border: 1px solid rgba(176, 122, 113, 0.28);
  background: rgba(176, 122, 113, 0.06);
  -webkit-tap-highlight-color: transparent;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease;
}

.visit-map__maps--primary {
  color: #fff;
  background: var(--color-rose);
  border-color: var(--color-rose);
}

.visit-map__maps--primary:hover,
.visit-map__maps--primary:focus-visible {
  background: var(--color-rose-dark);
  border-color: var(--color-rose-dark);
  color: #fff;
}

.visit-map__maps:hover,
.visit-map__maps:focus-visible {
  color: var(--color-rose-dark);
  background: rgba(176, 122, 113, 0.12);
  border-color: rgba(176, 122, 113, 0.4);
}

.visit-map__map-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-width: 0;
  background: var(--color-surface-raised);
  border: 1px solid rgba(176, 122, 113, 0.14);
  box-shadow: 0 14px 34px rgba(44, 44, 48, 0.07);
  overflow: hidden;
}

.visit-map__frame-wrap {
  position: relative;
  flex: 1 1 auto;
  min-height: 15.5rem;
  overflow: hidden;
  background:
    linear-gradient(
      180deg,
      color-mix(in srgb, var(--color-stone) 70%, var(--color-rose-soft)) 0%,
      var(--color-stone) 100%
    );
}

.visit-map__frame {
  position: absolute;
  /* Crop Google Maps chrome / “No reviews” strip */
  top: -4.75rem;
  left: -1.35rem;
  width: calc(100% + 2.7rem);
  height: calc(100% + 7.25rem);
  border: 0;
  filter: grayscale(0.1) contrast(0.98) saturate(0.9) brightness(1.02);
  pointer-events: auto;
}

.visit-map__map-caption {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0;
  padding: 0.95rem 1.15rem;
  border-top: 1px solid rgba(176, 122, 113, 0.12);
  font: 700 0.7rem/1.3 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-ink);
  text-decoration: none;
  background: color-mix(in srgb, var(--color-surface-raised) 88%, var(--color-rose-soft));
  transition: background 0.18s ease, color 0.18s ease;
  -webkit-tap-highlight-color: transparent;
  min-height: 2.85rem;
}

.visit-map__map-caption:hover,
.visit-map__map-caption:focus-visible {
  background: rgba(176, 122, 113, 0.14);
  color: var(--color-rose-dark);
}

.visit-map__map-caption-arrow {
  color: var(--color-rose);
  font-size: 1.05rem;
}

@media (min-width: 768px) {
  .visit-map {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .visit-map__inner {
    grid-template-columns: minmax(17rem, 22.5rem) minmax(0, 1fr);
    gap: 1.35rem;
    align-items: stretch;
  }

  .visit-map__card {
    padding: 2rem 1.85rem 1.85rem;
  }

  .visit-map__actions {
    align-items: flex-start;
  }

  .visit-map__book {
    width: auto;
    min-width: 11rem;
  }

  .visit-map__maps {
    justify-content: flex-start;
    padding-inline: 0.15rem;
    border: 0;
    background: transparent;
  }

  .visit-map__maps--primary {
    justify-content: center;
    padding-inline: 1.15rem;
    border: 1px solid var(--color-rose);
    background: var(--color-rose);
  }

  .visit-map__frame-wrap {
    min-height: 100%;
  }

  .visit-map__map-panel {
    min-height: 100%;
  }
}

@media (min-width: 1024px) {
  .visit-map__inner {
    grid-template-columns: minmax(18rem, 24rem) minmax(0, 1fr);
    gap: 1.65rem;
  }

  .visit-map__frame-wrap {
    min-height: 28rem;
  }
}
</style>
