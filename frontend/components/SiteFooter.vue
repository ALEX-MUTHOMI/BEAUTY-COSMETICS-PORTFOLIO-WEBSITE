<template>
  <footer id="contact" class="site-footer">
    <div class="site-footer__glow" aria-hidden="true" />

    <div class="site-footer__inner">
      <!-- Brand -->
      <div class="site-footer__brand">
        <SheeLogo variant="light" to="/" size="md" />
        <p class="site-footer__tagline">
          Facials, waxing, massage &amp; makeup in Meru Town — clean rooms, soft light, and therapists who take their time.
        </p>

        <div class="site-footer__call">
          <span class="site-footer__call-label">
            <svg class="site-footer__icon" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
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

      <!-- Quick Link -->
      <nav class="site-footer__col" aria-label="Quick links">
        <p class="site-footer__heading">Quick Link</p>
        <NuxtLink to="/">Home</NuxtLink>
        <NuxtLink to="/services">Services</NuxtLink>
        <NuxtLink :to="SERVICES_ROUTES.fullPackages">Packages</NuxtLink>
        <NuxtLink :to="SERVICES_ROUTES.singleSessions">Treatments</NuxtLink>
      </nav>

      <!-- Working Hour — tabloid plate so hours lead the footer -->
      <div class="site-footer__col site-footer__col--hours">
        <p class="site-footer__heading">Working Hour</p>
        <ul class="site-footer__hours">
          <li>
            <span class="site-footer__day">Monday</span>
            <span class="site-footer__time">7:00 to 19:00</span>
          </li>
          <li>
            <span class="site-footer__day">Tuesday – Wednesday</span>
            <span class="site-footer__time">7:00 to 19:00 · packages</span>
          </li>
          <li>
            <span class="site-footer__day">Thursday – Saturday</span>
            <span class="site-footer__time">7:00 to 19:00</span>
          </li>
          <li class="site-footer__hours-closed">
            <svg class="site-footer__icon" viewBox="0 0 24 24" aria-hidden="true" width="15" height="15">
              <path
                fill="currentColor"
                d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2zm6-6V11c0-3.1-1.6-5.6-4.5-6.3V4a1.5 1.5 0 0 0-3 0v.7C7.6 5.4 6 7.9 6 11v5l-2 2v1h16v-1l-2-2z"
              />
            </svg>
            Sunday Closed
          </li>
        </ul>
      </div>

      <!-- Visit us -->
      <div class="site-footer__col site-footer__col--support">
        <p class="site-footer__heading">Visit us</p>

        <a
          class="site-footer__support-row"
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
            {{ LANDING_ADDRESS_LINES[0] }}<br />
            {{ LANDING_ADDRESS_LINES[1] }}
          </span>
        </a>

        <a class="site-footer__support-row" href="mailto:bookings@sheeaesthetics.co.ke">
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
import { useLandingBookCta } from '@/landing/useLandingBookCta'

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
  padding: clamp(3.5rem, 7vw, 5.25rem) 1.25rem 0;
  overflow: clip;
}

.site-footer__glow {
  position: absolute;
  inset: auto auto -18% -8%;
  width: min(42vw, 18rem);
  height: min(42vw, 18rem);
  background-image: url('/images/flower.png');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.07;
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
  gap: clamp(2rem, 4.5vw, 2.75rem);
  padding-bottom: clamp(2.25rem, 5vw, 3.25rem);
}

.site-footer__brand {
  position: relative;
  max-width: 28rem;
}

.site-footer__tagline {
  margin: 1.25rem 0 0;
  max-width: 34ch;
  font: 400 0.95rem/1.65 var(--font-body);
  color: rgba(244, 235, 230, 0.7);
}

.site-footer__call {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
}

.site-footer__call-label {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font: 600 0.72rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(244, 235, 230, 0.78);
}

.site-footer__phone {
  margin: 0;
  font: 500 1.15rem/1.3 var(--font-body);
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
  font-size: 1rem;
}

.site-footer__heading {
  margin: 0 0 1.1rem;
  font: 600 1.05rem/1.2 var(--font-display);
  letter-spacing: -0.02em;
  text-transform: none;
  color: #fff;
}

.site-footer__col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
}

/* Tabloid plate — hours are the footer’s lead signal */
.site-footer__col--hours {
  position: relative;
  padding: 1.25rem 1.2rem 1.35rem;
  background:
    linear-gradient(
      160deg,
      rgba(48, 36, 38, 0.95) 0%,
      rgba(32, 24, 26, 0.98) 55%,
      rgba(26, 20, 22, 1) 100%
    );
  border: 1px solid rgba(240, 184, 172, 0.38);
  box-shadow:
    0 0 0 1px rgba(176, 122, 113, 0.12) inset,
    0 18px 40px rgba(0, 0, 0, 0.38);
  overflow: hidden;
}

.site-footer__col--hours::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-rose-dark), var(--color-rose), #f0b8ac);
  pointer-events: none;
}

.site-footer__col--hours::after {
  content: '';
  position: absolute;
  right: -1.1rem;
  bottom: -1.25rem;
  width: 6.5rem;
  height: 6.5rem;
  background-image: url('/images/flower.png');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.2;
  filter: saturate(1.4) brightness(1.2);
  pointer-events: none;
}

.site-footer__col--hours .site-footer__heading {
  position: relative;
  z-index: 1;
  margin-bottom: 0.95rem;
  font-size: 1.2rem;
  color: #fff;
}

.site-footer__col--hours .site-footer__hours {
  position: relative;
  z-index: 1;
  width: 100%;
  gap: 0.85rem;
}

.site-footer__col--hours .site-footer__day {
  color: #fff;
  font-weight: 600;
}

.site-footer__col--hours .site-footer__time {
  color: rgba(244, 235, 230, 0.72);
}

.site-footer__col--hours .site-footer__hours-closed {
  margin-top: 0.15rem;
  padding-top: 0.75rem;
  border-top: 1px solid rgba(240, 184, 172, 0.22);
  width: 100%;
}

.site-footer__col a {
  display: inline-flex;
  align-items: center;
  min-height: 2.5rem;
  padding: 0.15rem 0;
  color: rgba(244, 235, 230, 0.68);
  text-decoration: none;
  font: 400 0.92rem/1.45 var(--font-body);
  transition: color 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__col a:hover,
.site-footer__col a:focus-visible {
  color: var(--color-rose);
}

.site-footer__hours {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  font: 400 0.9rem/1.45 var(--font-body);
  color: rgba(244, 235, 230, 0.68);
}

.site-footer__day {
  display: block;
  color: rgba(244, 235, 230, 0.88);
  font-weight: 500;
}

.site-footer__time {
  display: block;
  margin-top: 0.1rem;
  color: rgba(244, 235, 230, 0.55);
  font-size: 0.86rem;
}

.site-footer__hours-closed {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.25rem;
  color: var(--color-rose);
  font: 600 0.92rem/1.3 var(--font-body);
}

.site-footer__support-row {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  margin: 0 0 0.85rem;
  max-width: 22rem;
  color: rgba(244, 235, 230, 0.68);
  font: 400 0.92rem/1.55 var(--font-body);
  text-decoration: none;
  transition: color 0.15s ease;
}

a.site-footer__support-row:hover,
a.site-footer__support-row:focus-visible {
  color: var(--color-rose);
}

.site-footer__icon {
  flex-shrink: 0;
  margin-top: 0.15rem;
}

.site-footer__icon--accent {
  color: var(--color-rose);
}

.site-footer__social {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 0.35rem;
}

.site-footer__social-btn {
  display: grid;
  place-content: center;
  width: 2.75rem;
  height: 2.75rem;
  min-height: 2.75rem;
  padding: 0;
  border-radius: 50%;
  color: rgba(244, 235, 230, 0.85);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(245, 216, 208, 0.16);
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
  padding: 1.15rem 0 calc(1.25rem + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.65rem 1.25rem;
  font: 400 0.8rem/1.4 var(--font-body);
  color: rgba(244, 235, 230, 0.42);
}

.site-footer__copy {
  margin: 0;
}

.site-footer__legal {
  display: flex;
  gap: 0.55rem;
  align-items: center;
}

.site-footer__legal a {
  display: inline-flex;
  align-items: center;
  min-height: 2.75rem;
  padding: 0.2rem 0.1rem;
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
  right: 1.1rem;
  bottom: calc(1.1rem + env(safe-area-inset-bottom, 0px));
  z-index: 60;
  display: grid;
  place-content: center;
  width: 3rem;
  height: 3rem;
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
    padding-bottom: calc(var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px));
  }

  .site-footer__top {
    bottom: calc(
      var(--mobile-book-bar-height, 4.15rem) + env(safe-area-inset-bottom, 0px) + 0.85rem
    );
  }
}

@media (min-width: 768px) {
  .site-footer__inner {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(2rem, 4vw, 2.75rem) clamp(1.75rem, 4vw, 3rem);
  }
}

@media (min-width: 1024px) {
  .site-footer__inner {
    grid-template-columns: 1.25fr 0.85fr 1.2fr 1fr;
    align-items: start;
    gap: clamp(1.75rem, 3vw, 3.25rem);
  }

  .site-footer__heading {
    font-size: 1.15rem;
  }

  .site-footer__col--hours {
    padding: 1.4rem 1.35rem 1.5rem;
  }

  .site-footer__col--hours .site-footer__heading {
    font-size: 1.28rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-footer__top,
  .site-footer__social-btn {
    transition: none;
  }
}
</style>
