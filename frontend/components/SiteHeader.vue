<template>
  <header
    ref="headerEl"
    class="site-header"
    :class="{
      'site-header--menu-open': menuOpen,
      'site-header--home': isHome,
      'site-header--over-hero': overHero,
      'site-header--solid': !overHero,
    }"
  >
    <!--
      Mellis Home 3:
      Centered stacked brand → hairline → IG | centered nav | Book
      Transparent over homepage hero; solid sticky after scroll / off-home
    -->
    <div class="site-header__brand">
      <SheeLogo
        class="site-header__logo site-header__logo--stacked"
        layout="stacked"
        size="sm"
        variant="default"
      />
      <SheeLogo
        class="site-header__logo site-header__logo--compact"
        size="sm"
        variant="default"
      />
    </div>

    <div class="site-header__nav-row">
      <a
        class="site-header__ig"
        :href="LANDING_INSTAGRAM_URL"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Instagram"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z" />
        </svg>
      </a>
      <a
        v-if="contactIsLive"
        class="site-header__wa"
        :href="whatsappUrl"
        target="_blank"
        rel="noopener noreferrer"
        :aria-label="whatsappLabel"
        @click="onWaClick"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
          <path
            fill="currentColor"
            d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 1.67c2.2 0 4.26.86 5.82 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.23 8.24-1.44 0-2.84-.37-4.08-1.07l-.29-.17-3.12.82.83-3.04-.19-.31a8.2 8.2 0 0 1-1.26-4.47c0-4.54 3.7-8.24 8.11-8.24z"
          />
        </svg>
      </a>

      <nav class="site-header__nav" aria-label="Primary">
        <NuxtLink
          to="/services"
          :class="{ 'is-active': route.path === '/services' && !isPackagesHash && !isSinglesHash }"
        >
          Services
        </NuxtLink>
        <NuxtLink
          :to="SERVICES_ROUTES.fullPackages"
          :class="{ 'is-active': isPackagesHash }"
        >
          Packages
        </NuxtLink>
        <NuxtLink
          :to="SERVICES_ROUTES.singleSessions"
          :class="{ 'is-active': isSinglesHash }"
        >
          Treatments
        </NuxtLink>
        <a href="/#contact" :class="{ 'is-active': route.hash === '#contact' }">Visit</a>
      </nav>

      <a
        v-if="bookIsExternal"
        :href="bookHref"
        class="site-header__cta"
        target="_blank"
        rel="noopener noreferrer"
        @click="onBookClick"
      >
        Book now
      </a>
      <NuxtLink
        v-else
        :to="bookHref"
        class="site-header__cta"
        @click="onBookClick"
      >
        Book now
      </NuxtLink>

      <button
        class="site-header__menu-toggle"
        type="button"
        :class="{ 'site-header__menu-toggle--open': menuOpen }"
        :aria-expanded="menuOpen"
        aria-controls="site-header-mobile-nav"
        :aria-label="menuOpen ? 'Close menu' : 'Open menu'"
        @click="menuOpen = !menuOpen"
      >
        <span class="site-header__menu-line" />
        <span class="site-header__menu-line" />
        <span class="site-header__menu-line" />
      </button>
    </div>

    <Teleport to="body">
      <Transition name="menu-fade">
        <div
          v-if="menuOpen"
          class="site-header__backdrop"
          aria-hidden="true"
          @click="closeMenu"
        />
      </Transition>
      <Transition name="menu-slide">
        <nav
          v-if="menuOpen"
          id="site-header-mobile-nav"
          class="site-header__drawer"
          aria-label="Mobile"
        >
          <button type="button" class="site-header__drawer-close" aria-label="Close menu" @click="closeMenu">
            <span aria-hidden="true" />
          </button>
          <div class="site-header__drawer-brand">
            <SheeLogo layout="stacked" size="md" @click="closeMenu" />
            <p class="site-header__drawer-label">{{ LANDING_LOCATION_LABEL }}</p>
            <a href="mailto:bookings@sheeaesthetics.co.ke" class="site-header__drawer-mail">
              bookings@sheeaesthetics.co.ke
            </a>
          </div>
          <div class="site-header__drawer-links">
            <NuxtLink to="/services" @click="closeMenu">Services</NuxtLink>
            <NuxtLink :to="SERVICES_ROUTES.fullPackages" @click="closeMenu">Packages</NuxtLink>
            <NuxtLink :to="SERVICES_ROUTES.singleSessions" @click="closeMenu">Treatments</NuxtLink>
            <a href="/#contact" @click="closeMenu">Visit</a>
            <a
              v-if="contactIsLive"
              :href="whatsappUrl"
              target="_blank"
              rel="noopener noreferrer"
              @click="onDrawerWa"
            >
              {{ whatsappLabel }}
            </a>
            <a
              :href="LANDING_INSTAGRAM_URL"
              target="_blank"
              rel="noopener noreferrer"
              @click="closeMenu"
            >
              Instagram
            </a>
          </div>
          <SiteButton
            v-if="bookIsExternal"
            :href="bookHref"
            variant="primary"
            class="site-header__drawer-cta"
            @click="onDrawerBook"
          >
            {{ LANDING_PRIMARY_CTA }}
          </SiteButton>
          <SiteButton
            v-else
            :to="bookHref"
            variant="primary"
            class="site-header__drawer-cta"
            @click="onDrawerBook"
          >
            {{ LANDING_PRIMARY_CTA }}
          </SiteButton>
        </nav>
      </Transition>
    </Teleport>
  </header>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
} from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'
import { trackFunnelEvent } from '@/landing/funnelEvents'
import { useLandingBookCta } from '@/landing/useLandingBookCta'

const route = useRoute()
const menuOpen = ref(false)
const headerEl = ref<HTMLElement | null>(null)
const isHome = computed(() => route.path === '/')
/** Transparent Home 3 overlay while the homepage hero is in view */
const heroInView = ref(isHome.value)
const overHero = computed(() => isHome.value && heroInView.value && !menuOpen.value)

const isPackagesHash = computed(() => route.path === '/services' && route.hash === '#full-packages')
const isSinglesHash = computed(() => route.path === '/services' && route.hash === '#single-sessions')

const { bookHref, bookIsExternal, contact } = useLandingBookCta()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel

function onBookClick() {
  trackFunnelEvent('cta_book_click', { surface: 'header', href: bookHref.value })
}

function onWaClick() {
  trackFunnelEvent('wa_click', { surface: 'header' })
}

function onDrawerBook() {
  trackFunnelEvent('cta_book_click', { surface: 'header_drawer', href: bookHref.value })
  closeMenu()
}

function onDrawerWa() {
  trackFunnelEvent('wa_click', { surface: 'header_drawer' })
  closeMenu()
}

let headerResizeObserver: ResizeObserver | null = null
let heroObserver: IntersectionObserver | null = null

function closeMenu() {
  menuOpen.value = false
}

function syncHeaderHeight() {
  const height = headerEl.value?.offsetHeight ?? 0
  if (height > 0) {
    const value = `${height}px`
    document.documentElement.style.setProperty('--site-header-height', value)
    document.documentElement.style.setProperty('--header-height', value)
  }
}

function teardownHeroObserver() {
  heroObserver?.disconnect()
  heroObserver = null
}

function setupHeroObserver() {
  teardownHeroObserver()
  if (!import.meta.client || !isHome.value) {
    heroInView.value = false
    return
  }

  const hero = document.querySelector('[data-home-hero]')
  if (!(hero instanceof HTMLElement)) {
    heroInView.value = false
    return
  }

  heroInView.value = true
  heroObserver = new IntersectionObserver(
    ([entry]) => {
      if (!entry) return
      // Mellis: solid bar only after the carousel has left — not mid-hero
      heroInView.value = entry.isIntersecting && entry.intersectionRatio > 0.08
    },
    { root: null, threshold: [0, 0.08, 0.15, 0.35, 0.6, 1] },
  )
  heroObserver.observe(hero)
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

watch(
  () => route.fullPath,
  async () => {
    closeMenu()
    await nextTick()
    setupHeroObserver()
    syncHeaderHeight()
  },
)

watch(overHero, async () => {
  await nextTick()
  syncHeaderHeight()
})

onMounted(async () => {
  await nextTick()
  setupHeroObserver()
  syncHeaderHeight()
  if (headerEl.value && typeof ResizeObserver !== 'undefined') {
    headerResizeObserver = new ResizeObserver(() => syncHeaderHeight())
    headerResizeObserver.observe(headerEl.value)
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  teardownHeroObserver()
  headerResizeObserver?.disconnect()
  headerResizeObserver = null
})
</script>

<style scoped>
.site-header {
  --header-rose: #de968d;
  --header-rose-hover: #d1857c;
  --header-ink: #27252a;
  --header-muted: #89868d;
  --header-pad: clamp(1rem, 3.5vw, 3rem);

  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  transition:
    background-color 0.45s cubic-bezier(0.22, 1, 0.36, 1),
    box-shadow 0.45s cubic-bezier(0.22, 1, 0.36, 1),
    backdrop-filter 0.45s ease,
    border-color 0.45s ease,
    min-height 0.35s cubic-bezier(0.22, 1, 0.36, 1),
    padding 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

.site-header--menu-open {
  z-index: 60;
}

/*
  Mellis Home 3 scroll:
  Over carousel → absolute (scrolls away with hero).
  Past carousel → fixed compact solid bar.
*/
.site-header--home.site-header--over-hero {
  position: absolute;
  left: 0;
  right: 0;
  top: var(--welcome-bar-offset, 0px);
  width: 100%;
}

.site-header--home.site-header--solid {
  position: fixed;
  left: 0;
  right: 0;
  top: var(--welcome-bar-offset, 0px);
  width: 100%;
  animation: header-solid-in 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes header-solid-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Transparent Home 3 overlay — sits on the hero photo */
.site-header--over-hero {
  background: transparent;
  border-bottom: 0;
  box-shadow: none;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

/* Solid compact float after hero / off-home — soft Mellis glass bar */
.site-header--solid {
  background: rgba(255, 255, 255, 0.94);
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
  box-shadow:
    0 1px 0 rgba(255, 255, 255, 0.7) inset,
    0 8px 28px rgba(39, 37, 42, 0.07);
  backdrop-filter: blur(16px) saturate(1.15);
  -webkit-backdrop-filter: blur(16px) saturate(1.15);
}

.site-header--solid:not(.site-header--home) {
  position: sticky;
}

.site-header__brand {
  display: flex;
  justify-content: center;
  padding:
    calc(0.85rem + env(safe-area-inset-top, 0px))
    max(var(--header-pad), env(safe-area-inset-right, 0px))
    0.65rem
    max(var(--header-pad), env(safe-area-inset-left, 0px));
}

.site-header--over-hero .site-header__brand {
  padding-bottom: 0.65rem;
}

/* Keep brand light — no frosted pill covering the photo */
.site-header--over-hero .site-header__logo--stacked {
  padding: 0;
  border-radius: 0;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  box-shadow: none;
}

.site-header__logo--compact {
  display: none;
}

.site-header--solid .site-header__logo--stacked {
  display: none;
}

.site-header--solid .site-header__logo--compact {
  display: inline-flex;
}

.site-header--over-hero .site-header__logo--compact {
  display: none;
}

/* Brand colors — visible without blocking the hero */
.site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__mark-wrap) {
  width: 46px;
  height: 46px;
  background: var(--header-rose);
  border: 1.5px solid rgba(255, 255, 255, 0.85);
  box-shadow: 0 3px 12px rgba(20, 16, 18, 0.3);
}

.site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__mark) {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
}

.site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__name) {
  color: #f0b8ac;
  font-size: clamp(1.5rem, 3.2vw, 1.9rem);
  text-shadow:
    0 1px 2px rgba(20, 16, 18, 0.75),
    0 3px 14px rgba(20, 16, 18, 0.35);
}

.site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__tag) {
  color: #f0b8ac;
  font-size: 0.62rem;
  letter-spacing: 0.3em;
  font-weight: 700;
  text-shadow: 0 1px 8px rgba(20, 16, 18, 0.45);
}

.site-header__nav-row {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  min-height: 3.25rem;
  padding:
    0.35rem max(var(--header-pad), env(safe-area-inset-right, 0px))
    0.85rem max(var(--header-pad), env(safe-area-inset-left, 0px));
}

.site-header--over-hero .site-header__nav-row {
  border-top: 1px solid rgba(255, 255, 255, 0.28);
}

.site-header--solid .site-header__nav-row {
  border-top: 0;
}

/* Solid: single horizontal bar — compact logo | nav row */
.site-header--solid {
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  min-height: 4.25rem;
  padding-left: max(var(--header-pad), env(safe-area-inset-left, 0px));
  padding-right: max(var(--header-pad), env(safe-area-inset-right, 0px));
}

.site-header--solid .site-header__brand {
  display: flex;
  flex-shrink: 0;
  padding: 0;
}

.site-header--solid .site-header__nav-row {
  flex: 1 1 auto;
  min-height: 4.25rem;
  padding: 0;
}

.site-header__nav {
  display: none;
}

.site-header__ig,
.site-header__wa {
  display: none;
}

.site-header__cta {
  display: none;
}

.site-header__menu-toggle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  margin-left: auto;
  min-width: 48px;
  min-height: 48px;
  padding: 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.site-header--solid .site-header__menu-toggle {
  border-color: var(--color-line);
  background: #fff;
}

.site-header__menu-line {
  display: block;
  width: 18px;
  height: 2px;
  border-radius: 1px;
  background: #fff;
  transition: transform 0.3s ease, opacity 0.3s ease, width 0.3s ease;
}

.site-header--solid .site-header__menu-line {
  background: var(--header-ink);
}

.site-header__menu-toggle--open .site-header__menu-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.site-header__menu-toggle--open .site-header__menu-line:nth-child(2) {
  opacity: 0;
  width: 0;
}

.site-header__menu-toggle--open .site-header__menu-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.site-header--menu-open .site-header__menu-toggle {
  visibility: hidden;
  pointer-events: none;
}

/* Phone over-hero: single compact row — brand left, menu right */
@media (max-width: 767px) {
  .site-header--home.site-header--over-hero {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
    padding-left: max(0.85rem, env(safe-area-inset-left, 0px));
    padding-right: max(0.85rem, env(safe-area-inset-right, 0px));
    padding-top: env(safe-area-inset-top, 0px);
    min-height: 3.5rem;
  }

  .site-header--home.site-header--over-hero .site-header__brand {
    flex: 1 1 auto;
    justify-content: flex-start;
    padding: 0.35rem 0;
  }

  .site-header--home.site-header--over-hero .site-header__logo--stacked {
    display: none;
  }

  .site-header--home.site-header--over-hero .site-header__logo--compact {
    display: inline-flex;
  }

  .site-header--home.site-header--over-hero .site-header__logo--compact :deep(.shee-logo__mark-wrap) {
    width: 34px;
    height: 34px;
    background: var(--header-rose);
    border: 1.5px solid rgba(255, 255, 255, 0.85);
    box-shadow: 0 2px 10px rgba(20, 16, 18, 0.28);
  }

  .site-header--home.site-header--over-hero .site-header__logo--compact :deep(.shee-logo__mark) {
    width: 18px;
    height: 18px;
    filter: brightness(0) invert(1);
  }

  .site-header--home.site-header--over-hero .site-header__logo--compact :deep(.shee-logo__name) {
    color: #f0b8ac;
    font-size: 1.15rem;
    text-shadow:
      0 1px 2px rgba(20, 16, 18, 0.75),
      0 3px 12px rgba(20, 16, 18, 0.35);
  }

  .site-header--home.site-header--over-hero .site-header__logo--compact :deep(.shee-logo__tag) {
    color: #f0b8ac;
    font-size: 0.5rem;
    letter-spacing: 0.24em;
    font-weight: 700;
    text-shadow: 0 1px 8px rgba(20, 16, 18, 0.45);
  }

  .site-header--home.site-header--over-hero .site-header__nav-row {
    flex: 0 0 auto;
    justify-content: flex-end;
    min-height: 0;
    padding: 0;
    border-top: 0;
  }

  .site-header--home.site-header--over-hero .site-header__menu-toggle {
    min-width: 44px;
    min-height: 44px;
    padding: 0.55rem;
  }
}

/* Mobile over-hero (tablet band): brand centered, hamburger on the right of nav row */
@media (min-width: 768px) and (max-width: 959px) {
  .site-header--over-hero .site-header__brand {
    padding-top: calc(0.55rem + env(safe-area-inset-top, 0px));
    padding-bottom: 0.25rem;
  }

  .site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__mark-wrap) {
    width: 38px;
    height: 38px;
  }

  .site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__mark) {
    width: 20px;
    height: 20px;
  }

  .site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__name) {
    font-size: clamp(1.28rem, 5.5vw, 1.55rem);
  }

  .site-header--over-hero .site-header__logo--stacked :deep(.shee-logo__tag) {
    font-size: 0.55rem;
    letter-spacing: 0.26em;
  }

  .site-header--over-hero .site-header__nav-row {
    justify-content: flex-end;
    min-height: 2.65rem;
    padding-top: 0.1rem;
    padding-bottom: 0.55rem;
  }
}

@media (min-width: 960px) {
  .site-header--over-hero .site-header__brand {
    padding-top: calc(1.15rem + env(safe-area-inset-top, 0px));
    padding-bottom: 0.85rem;
  }

  .site-header__nav-row {
    min-height: 3.5rem;
  }

  .site-header--solid {
    min-height: 4.5rem;
  }

  .site-header--solid .site-header__nav-row {
    min-height: 4.5rem;
  }

  .site-header__ig,
  .site-header__wa {
    display: grid;
    place-items: center;
    width: 2.5rem;
    height: 2.5rem;
    flex-shrink: 0;
    color: #fff;
    transition: color 0.2s ease, opacity 0.2s ease;
  }

  .site-header--solid .site-header__ig,
  .site-header--solid .site-header__wa {
    color: var(--header-ink);
  }

  .site-header__ig:hover,
  .site-header__wa:hover {
    color: var(--header-rose);
  }

  .site-header--over-hero .site-header__ig:hover,
  .site-header--over-hero .site-header__wa:hover {
    color: #fff;
    opacity: 0.8;
  }

  .site-header__ig svg,
  .site-header__wa svg {
    width: 1rem;
    height: 1rem;
    fill: currentColor;
  }

  .site-header__nav {
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.1rem;
    transform: translateX(-50%);
  }

  .site-header__nav a {
    display: inline-flex;
    align-items: center;
    height: 100%;
    padding: 0 1rem;
    color: #fff;
    font: 600 0.76rem/1 var(--font-body);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    text-decoration: none;
    text-shadow: 0 1px 10px rgba(20, 16, 18, 0.25);
    transition: color 0.2s ease, opacity 0.2s ease;
  }

  .site-header--over-hero .site-header__nav a {
    color: #fff;
  }

  .site-header--solid .site-header__nav a {
    color: var(--header-muted);
    text-shadow: none;
  }

  .site-header__nav a:hover,
  .site-header__nav a.router-link-exact-active,
  .site-header__nav a.is-active {
    color: #fff;
    opacity: 0.85;
  }

  .site-header--solid .site-header__nav a:hover,
  .site-header--solid .site-header__nav a.router-link-exact-active,
  .site-header--solid .site-header__nav a.is-active {
    color: var(--header-ink);
    opacity: 1;
  }

  .site-header__cta {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    min-height: 2.6rem;
    padding: 0 1.25rem;
    border: 1px solid rgba(255, 255, 255, 0.85);
    color: #fff !important;
    font: 700 0.7rem/1 var(--font-body);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    text-decoration: none;
    white-space: nowrap;
    transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
  }

  .site-header--over-hero .site-header__cta:hover {
    background: #fff;
    color: var(--header-ink) !important;
  }

  .site-header--solid .site-header__cta {
    border-color: transparent;
    background: var(--header-rose);
    color: #fff !important;
  }

  .site-header--solid .site-header__cta:hover {
    background: var(--header-rose-hover);
  }

  .site-header__menu-toggle {
    display: none !important;
  }

  .site-header--solid .site-header__logo--compact :deep(.shee-logo__mark-wrap) {
    background: var(--header-rose);
    box-shadow: 0 4px 14px rgba(222, 150, 141, 0.28);
  }
}

.site-header__ig:focus-visible,
.site-header__wa:focus-visible,
.site-header__cta:focus-visible,
.site-header__nav a:focus-visible,
.site-header__menu-toggle:focus-visible,
.site-header__drawer-mail:focus-visible {
  outline: 2px solid var(--header-rose);
  outline-offset: 3px;
}

/* Drawer */
.site-header__backdrop {
  position: fixed;
  inset: 0;
  z-index: 65;
  background: rgba(39, 37, 42, 0.4);
}

.site-header__drawer {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: flex;
  flex-direction: column;
  height: 100dvh;
  padding:
    calc(1.5rem + env(safe-area-inset-top, 0px))
    max(1.5rem, env(safe-area-inset-right, 0px))
    calc(2rem + env(safe-area-inset-bottom, 0px))
    max(1.5rem, env(safe-area-inset-left, 0px));
  background: #fff;
  overflow-y: auto;
}

.site-header__drawer-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.65rem;
  margin: 0.5rem 0 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid var(--color-line);
  text-align: center;
}

.site-header__drawer-close {
  position: absolute;
  top: calc(1rem + env(safe-area-inset-top, 0px));
  right: max(1rem, env(safe-area-inset-right, 0px));
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border: 1px solid var(--color-line);
  border-radius: 50%;
  background: #fff;
  cursor: pointer;
}

.site-header__drawer-close span {
  position: relative;
  width: 16px;
  height: 16px;
}

.site-header__drawer-close span::before,
.site-header__drawer-close span::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: #27252a;
}

.site-header__drawer-close span::before {
  transform: translateY(-50%) rotate(45deg);
}

.site-header__drawer-close span::after {
  transform: translateY(-50%) rotate(-45deg);
}

.site-header__drawer-label {
  margin: 0;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.site-header__drawer-mail {
  margin: 0;
  color: var(--header-muted);
  font: 400 0.88rem/1.3 var(--font-body);
  text-decoration: none;
}

.site-header__drawer-mail:hover {
  color: var(--header-rose);
}

.site-header__drawer-links {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.site-header__drawer-links a {
  display: flex;
  align-items: center;
  min-height: 3rem;
  padding: 0.85rem 0.25rem;
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
  color: #27252a;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  text-decoration: none;
}

.site-header__drawer-cta {
  width: 100%;
  margin-top: auto;
  padding-top: 1.75rem;
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.25s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
}

.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.menu-slide-enter-from,
.menu-slide-leave-to {
  transform: translateY(12px);
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .site-header,
  .site-header__menu-line,
  .site-header__ig,
  .site-header__wa,
  .site-header__cta,
  .site-header__nav a,
  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .menu-slide-enter-active,
  .menu-slide-leave-active {
    transition: none !important;
  }
}
</style>
