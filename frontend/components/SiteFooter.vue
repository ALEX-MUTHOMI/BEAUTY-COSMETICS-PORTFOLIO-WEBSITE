<template>
  <footer id="contact" class="site-footer">
    <div class="site-footer__glow" aria-hidden="true" />

    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <SheeLogo variant="light" to="/" size="md" />
        <p class="site-footer__tagline">
          Facials, waxing, massage &amp; makeup in Meru Town.
        </p>
        <div class="site-footer__call">
          <span class="site-footer__call-label">
            <svg class="site-footer__icon" viewBox="0 0 24 24" aria-hidden="true" width="14" height="14">
              <path
                fill="currentColor"
                d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1.1-.2 1.2.4 2.5.6 3.8.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.7 21 3 13.3 3 3.7c0-.6.4-1 1-1H7c.6 0 1 .4 1 1 0 1.3.2 2.6.6 3.8.1.4 0 .8-.3 1.1L6.6 10.8z"
              />
            </svg>
            Make a call
          </span>
          <a
            v-if="contactIsLive && phoneTel"
            class="site-footer__phone"
            :href="phoneTel"
            @click="trackFunnelEvent('cta_book_click', { surface: 'footer_call', href: phoneTel })"
          >
            {{ phoneDisplay }}
          </a>
          <a
            v-else-if="contactIsLive && whatsappUrl"
            class="site-footer__phone"
            :href="whatsappUrl"
            target="_blank"
            rel="noopener noreferrer"
            @click="trackFunnelEvent('wa_click', { surface: 'footer_call' })"
          >
            {{ whatsappLabel }}
          </a>
          <p v-else class="site-footer__phone site-footer__phone--pending">
            {{ phoneDisplay }}
          </p>
        </div>
      </div>

      <nav class="site-footer__links" aria-label="Quick links">
        <p class="site-footer__heading">Quick links</p>
        <div class="site-footer__link-grid">
          <NuxtLink to="/">Home</NuxtLink>
          <NuxtLink to="/services">Services</NuxtLink>
          <NuxtLink to="/faq">FAQ</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.fullPackages">Packages</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.singleSessions">Treatments</NuxtLink>
        </div>
      </nav>

      <div class="site-footer__visit">
        <img
          src="/images/flower.png"
          alt=""
          class="site-footer__visit-bloom site-footer__visit-bloom--tr"
          width="72"
          height="72"
          loading="lazy"
          decoding="async"
          aria-hidden="true"
        />
        <img
          src="/images/flower.png"
          alt=""
          class="site-footer__visit-bloom site-footer__visit-bloom--bl"
          width="56"
          height="56"
          loading="lazy"
          decoding="async"
          aria-hidden="true"
        />
        <p class="site-footer__heading">Visit us</p>

        <a
          class="site-footer__visit-row"
          :href="LANDING_MAPS_URL"
          target="_blank"
          rel="noopener noreferrer"
        >
          <svg class="site-footer__icon site-footer__icon--accent" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
            <path
              fill="currentColor"
              d="M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z"
            />
          </svg>
          <span>
            {{ LANDING_ADDRESS_LINES[0] }} · {{ LANDING_ADDRESS_LINES[1] }}
          </span>
        </a>

        <a class="site-footer__visit-row" href="mailto:bookings@sheeaesthetics.co.ke">
          <svg class="site-footer__icon site-footer__icon--accent" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
            <path
              fill="currentColor"
              d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"
            />
          </svg>
          <span>bookings@sheeaesthetics.co.ke</span>
        </a>

        <div class="site-footer__social" aria-label="Social">
          <a
            class="site-footer__social-btn"
            :href="LANDING_INSTAGRAM_URL"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Shee Aesthetics on Instagram"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
              <path
                fill="currentColor"
                d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"
              />
            </svg>
          </a>
          <a
            v-if="contactIsLive && whatsappUrl"
            class="site-footer__social-btn"
            :href="whatsappUrl"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="WhatsApp Shee Aesthetics"
            @click="trackFunnelEvent('wa_click', { surface: 'footer_social' })"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
              <path
                fill="currentColor"
                d="M12.04 2C6.58 2 2.15 6.4 2.15 11.84c0 2.08.61 4.02 1.67 5.66L2 22l4.67-1.76a9.86 9.86 0 0 0 5.37 1.56h.01c5.46 0 9.89-4.4 9.89-9.84C21.94 6.4 17.5 2 12.04 2zm5.78 14.15c-.24.68-1.4 1.25-1.94 1.33-.5.07-1.13.1-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.26-4.79-4.2-4.93-4.4-.14-.2-1.16-1.55-1.16-2.95 0-1.4.73-2.09.99-2.38.26-.29.57-.36.76-.36h.54c.17 0 .4-.06.62.47.24.57.81 1.98.88 2.12.07.14.12.31.02.5-.1.2-.15.31-.3.48-.14.17-.3.38-.43.51-.14.14-.29.29-.12.56.17.28.75 1.24 1.61 2.01 1.11.99 2.04 1.3 2.33 1.44.29.14.46.12.63-.07.17-.2.73-.85.93-1.14.2-.29.4-.24.67-.14.27.1 1.72.81 2.01.96.29.14.49.22.56.34.07.12.07.7-.17 1.38z"
              />
            </svg>
          </a>
        </div>
      </div>
    </div>

    <div class="site-footer__bottom">
      <p class="site-footer__copy">&copy; {{ year }} Shee Aesthetics</p>
      <div class="site-footer__legal">
        <NuxtLink to="/terms">Terms of Use</NuxtLink>
        <span aria-hidden="true">/</span>
        <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
      </div>
    </div>

    <button
      type="button"
      class="site-footer__top"
      :class="{ 'site-footer__top--visible': showTop }"
      aria-label="Back to top"
      @click="scrollToTop"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
        <path fill="currentColor" d="M7.4 15.4 12 10.8l4.6 4.6L18 14l-6-6-6 6z" />
      </svg>
    </button>
  </footer>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import {
  LANDING_ADDRESS_LINES,
  LANDING_INSTAGRAM_URL,
  LANDING_MAPS_URL,
} from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'
import { trackFunnelEvent } from '@/landing/funnelEvents'
import { useLandingBookCta } from '~/composables/useLandingBookCta'

const year = new Date().getFullYear()

const { contact } = useLandingBookCta()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel
const phoneDisplay = contact.phoneDisplay
const phoneTel = contact.phoneTel

const showTop = ref(false)

function onScroll() {
  showTop.value = window.scrollY > 480
}

function scrollToTop() {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' })
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
.site-footer {
  position: relative;
  isolation: isolate;
  background: var(--color-footer);
  color: rgba(244, 235, 230, 0.72);
  /* Mobile-first: tight padding — not a second page */
  padding: 1.75rem 1rem 0;
  overflow: clip;
}

.site-footer__glow {
  position: absolute;
  inset: auto auto -12% -6%;
  width: min(36vw, 12rem);
  height: min(36vw, 12rem);
  background-image: url('/images/flower.png');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.08;
  filter: saturate(1.2) brightness(1.1);
  pointer-events: none;
  z-index: 0;
}

.site-footer__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.35rem;
  align-items: start;
  padding-bottom: 1.25rem;
}

.site-footer__brand {
  max-width: 28rem;
}

.site-footer__tagline {
  margin: 0.75rem 0 0;
  max-width: 36ch;
  font: 400 0.88rem/1.5 var(--font-body);
  color: rgba(244, 235, 230, 0.68);
}

.site-footer__call {
  margin-top: 0.85rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
}

.site-footer__call-label {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font: 600 0.65rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(244, 235, 230, 0.7);
}

.site-footer__phone {
  margin: 0;
  font: 600 1.05rem/1.3 var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-rose);
  text-decoration: none;
  -webkit-tap-highlight-color: transparent;
  transition: color 0.18s ease;
}

a.site-footer__phone:hover,
a.site-footer__phone:focus-visible {
  color: #f0b8ac;
}

.site-footer__phone--pending {
  color: rgba(240, 184, 172, 0.75);
  font-size: 0.95rem;
}

.site-footer__heading {
  margin: 0 0 0.55rem;
  font: 600 0.95rem/1.2 var(--font-display);
  letter-spacing: -0.02em;
  color: #fff;
}

.site-footer__links {
  min-width: 0;
}

.site-footer__link-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.site-footer__link-grid a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.65rem;
  padding: 0.55rem 0.7rem;
  text-align: center;
  color: rgba(255, 248, 244, 0.9);
  text-decoration: none;
  font: 600 0.82rem/1.2 var(--font-body);
  letter-spacing: 0.02em;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(222, 150, 141, 0.22);
  transition:
    color 0.15s ease,
    background 0.15s ease,
    border-color 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__link-grid a:hover,
.site-footer__link-grid a:focus-visible {
  color: #fff;
  background: rgba(222, 150, 141, 0.22);
  border-color: rgba(222, 150, 141, 0.45);
}

.site-footer__link-grid a.router-link-active {
  color: #fff;
  background: rgba(222, 150, 141, 0.28);
  border-color: rgba(222, 150, 141, 0.5);
}

/* Dark Visit card — calm palette, readable type */
.site-footer__visit {
  position: relative;
  overflow: hidden;
  padding: 0.95rem 0.95rem 1rem;
  background:
    radial-gradient(ellipse 80% 60% at 100% 0%, rgba(222, 150, 141, 0.16), transparent 58%),
    linear-gradient(165deg, #322a2b 0%, #262122 50%, #1e1a1b 100%);
  border: 1px solid rgba(222, 150, 141, 0.24);
  border-top: 3px solid var(--color-rose);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.18);
}

.site-footer__visit::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.08;
  background-image: url('/images/flower.png');
  background-size: 4.75rem;
  background-repeat: repeat;
  filter: saturate(1.15) brightness(1.05);
  mix-blend-mode: soft-light;
}

.site-footer__visit-bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.24;
  filter: saturate(1.15);
}

.site-footer__visit-bloom--tr {
  top: -0.65rem;
  right: -0.45rem;
  width: 4.25rem;
  transform: rotate(16deg);
}

.site-footer__visit-bloom--bl {
  left: -0.55rem;
  bottom: -0.4rem;
  width: 3.25rem;
  opacity: 0.28;
  transform: rotate(-24deg);
}

.site-footer__visit > *:not(.site-footer__visit-bloom) {
  position: relative;
  z-index: 1;
}

.site-footer__visit-row {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  margin: 0 0 0.45rem;
  color: rgba(255, 250, 246, 0.92);
  font: 500 0.84rem/1.45 var(--font-body);
  text-decoration: none;
  transition: color 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

a.site-footer__visit-row:hover,
a.site-footer__visit-row:focus-visible {
  color: #f0b8ac;
}

.site-footer__icon {
  flex-shrink: 0;
  margin-top: 0.12rem;
}

.site-footer__icon--accent {
  color: #f0b8ac;
}

.site-footer__social {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.35rem;
}

.site-footer__social-btn {
  display: grid;
  place-content: center;
  width: 2.5rem;
  height: 2.5rem;
  min-height: 2.5rem;
  padding: 0;
  border-radius: 50%;
  color: rgba(244, 235, 230, 0.9);
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(245, 216, 208, 0.22);
  text-decoration: none;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__social-btn:hover,
.site-footer__social-btn:focus-visible {
  color: #fff;
  background: var(--color-rose);
  border-color: var(--color-rose);
  transform: translateY(-2px);
}

.site-footer__bottom {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  padding: 0.85rem 0 calc(0.95rem + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem 1rem;
  font: 400 0.75rem/1.4 var(--font-body);
  color: rgba(244, 235, 230, 0.42);
}

.site-footer__copy {
  margin: 0;
}

.site-footer__legal {
  display: flex;
  gap: 0.45rem;
  align-items: center;
}

.site-footer__legal a {
  display: inline-flex;
  align-items: center;
  min-height: 2.35rem;
  padding: 0.15rem 0.05rem;
  color: rgba(244, 235, 230, 0.5);
  text-decoration: none;
  -webkit-tap-highlight-color: transparent;
  transition: color 0.15s ease;
}

.site-footer__legal a:hover,
.site-footer__legal a:focus-visible {
  color: var(--color-rose);
}

.site-footer__top {
  position: fixed;
  right: 1rem;
  bottom: calc(1rem + env(safe-area-inset-bottom, 0px));
  z-index: 60;
  display: grid;
  place-content: center;
  width: 2.75rem;
  height: 2.75rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: #fff;
  background: var(--color-rose);
  box-shadow: 0 10px 24px rgba(176, 122, 113, 0.35);
  cursor: pointer;
  opacity: 0;
  visibility: hidden;
  transform: translateY(0.5rem);
  pointer-events: none;
  transition:
    opacity 0.25s ease,
    visibility 0.25s ease,
    transform 0.25s ease,
    background 0.18s ease;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__top--visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
  pointer-events: auto;
}

.site-footer__top:hover,
.site-footer__top:focus-visible {
  background: var(--color-rose-dark);
  outline: none;
}

@media (max-width: 767px) {
  .site-footer {
    padding: 1.15rem 1rem 0;
    padding-bottom: calc(var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px));
  }

  .site-footer__inner {
    gap: 0.85rem;
    padding-bottom: 0.85rem;
  }

  .site-footer__tagline {
    display: none;
  }

  .site-footer__call {
    margin-top: 0.55rem;
  }

  .site-footer__phone {
    font-size: 0.95rem;
  }

  .site-footer__heading {
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
  }

  .site-footer__link-grid a {
    min-height: 2.75rem;
    font-size: 0.84rem;
  }

  .site-footer__visit {
    padding: 0.85rem 0.85rem 0.9rem;
  }

  .site-footer__social-btn {
    width: 2.25rem;
    height: 2.25rem;
    min-height: 2.25rem;
  }

  .site-footer__top {
    bottom: calc(
      var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px) + 0.75rem
    );
  }

  .site-footer__bottom {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    padding-top: 0.55rem;
    padding-bottom: calc(0.65rem + env(safe-area-inset-bottom, 0px));
    font-size: 0.7rem;
  }

  .site-footer__legal a {
    min-height: 2.1rem;
  }
}

@media (min-width: 768px) {
  .site-footer {
    padding: 2.5rem 1.25rem 0;
  }

  .site-footer__inner {
    grid-template-columns: 1.35fr 1fr 1.15fr;
    gap: 1.75rem 2.5rem;
    padding-bottom: 1.75rem;
    align-items: start;
  }

  .site-footer__tagline {
    font-size: 0.92rem;
  }

  /* Desktop: quiet text links — not mobile tap tiles */
  .site-footer__link-grid {
    display: flex;
    flex-direction: column;
    gap: 0;
  }

  .site-footer__link-grid a {
    justify-content: flex-start;
    min-height: 2.35rem;
    padding: 0.35rem 0;
    font: 500 0.95rem/1.3 var(--font-body);
    letter-spacing: 0.04em;
    color: rgba(244, 235, 230, 0.72);
    background: transparent;
    border: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 0;
  }

  .site-footer__link-grid a:last-child {
    border-bottom: 0;
  }

  .site-footer__link-grid a:hover,
  .site-footer__link-grid a:focus-visible {
    color: #f0b8ac;
    background: transparent;
    border-color: rgba(222, 150, 141, 0.35);
  }

  .site-footer__link-grid a.router-link-active {
    color: #f0b8ac;
    background: transparent;
    border-color: rgba(222, 150, 141, 0.45);
    font-weight: 600;
  }

  .site-footer__visit {
    padding: 1.15rem 1.1rem 1.2rem;
  }

  .site-footer__heading {
    font-size: 1.05rem;
    margin-bottom: 0.75rem;
  }
}

@media (min-width: 1024px) {
  .site-footer {
    padding: 2.75rem 1.25rem 0;
  }

  .site-footer__inner {
    gap: 2rem 3rem;
  }

  .site-footer__link-grid a {
    font-size: 1rem;
    min-height: 2.5rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-footer__top,
  .site-footer__social-btn {
    transition: none;
  }
}
</style>
