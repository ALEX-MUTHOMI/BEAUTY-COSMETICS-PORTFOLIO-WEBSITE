<template>
  <header
    ref="headerEl"
    class="site-header"
    :class="{ 'site-header--menu-open': menuOpen }"
  >
    <!-- Mellis top strip: full-bleed · contacts left · social + edge Book now -->
    <div class="site-header__top" aria-label="Contact bar">
      <div class="site-header__top-body">
        <div class="site-header__contact">
          <a href="mailto:bookings@sheeaesthetics.co.ke" class="site-header__chip">
            <span class="site-header__chip-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M3 6.75A1.75 1.75 0 0 1 4.75 5h14.5A1.75 1.75 0 0 1 21 6.75v10.5A1.75 1.75 0 0 1 19.25 19H4.75A1.75 1.75 0 0 1 3 17.25V6.75zm1.75-.25a.25.25 0 0 0-.25.25v.2l7.1 4.44a.75.75 0 0 0 .8 0L20.5 6.95v-.2a.25.25 0 0 0-.25-.25H4.75zM20.5 8.7l-6.55 4.1a2.25 2.25 0 0 1-2.4 0L5 8.7v8.55c0 .138.112.25.25.25h14.5a.25.25 0 0 0 .25-.25V8.7z"/></svg>
            </span>
            bookings@sheeaesthetics.co.ke
          </a>
          <span class="site-header__chip">
            <span class="site-header__chip-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24"><path d="M12 2.25a7.25 7.25 0 0 0-7.25 7.25c0 4.66 5.44 10.86 6.55 12.08a.9.9 0 0 0 1.4 0c1.11-1.22 6.55-7.42 6.55-12.08A7.25 7.25 0 0 0 12 2.25zm0 9.75a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z"/></svg>
            </span>
            {{ LANDING_LOCATION_LABEL }}
          </span>
        </div>

        <div class="site-header__top-tools">
          <a
            class="site-header__ig"
            :href="LANDING_INSTAGRAM_URL"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Instagram"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"/></svg>
          </a>
        </div>
      </div>
      <NuxtLink to="/services" class="site-header__book">Book now</NuxtLink>
    </div>

    <!-- Mellis main: full-bleed 60px pad · Shee script logo left · menu right -->
    <div class="site-header__main">
      <div class="site-header__main-inner">
        <SheeLogo class="site-header__logo" size="sm" />

        <nav class="site-header__nav" aria-label="Primary">
          <NuxtLink to="/">Home</NuxtLink>
          <NuxtLink to="/services">Services</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.fullPackages">Packages</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.singleSessions">Singles</NuxtLink>
          <a href="/#contact" :class="{ 'is-active': route.hash === '#contact' }">Contact</a>
          <NuxtLink to="/services">Book now</NuxtLink>
        </nav>

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
            <SheeLogo size="md" @click="closeMenu" />
            <p class="site-header__drawer-label">{{ LANDING_LOCATION_LABEL }}</p>
          </div>
          <div class="site-header__drawer-links">
            <NuxtLink to="/" @click="closeMenu">Home</NuxtLink>
            <NuxtLink to="/services" @click="closeMenu">Services</NuxtLink>
            <NuxtLink :to="SERVICES_ROUTES.fullPackages" @click="closeMenu">Packages</NuxtLink>
            <NuxtLink :to="SERVICES_ROUTES.singleSessions" @click="closeMenu">Singles</NuxtLink>
            <a href="/#contact" @click="closeMenu">Contact</a>
          </div>
          <SiteButton to="/services" variant="primary" class="site-header__drawer-cta" @click="closeMenu">
            {{ LANDING_PRIMARY_CTA }}
          </SiteButton>
        </nav>
      </Transition>
    </Teleport>
  </header>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
} from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const route = useRoute()
const menuOpen = ref(false)
const headerEl = ref<HTMLElement | null>(null)

let headerResizeObserver: ResizeObserver | null = null

function closeMenu() {
  menuOpen.value = false
}

function syncHeaderHeight() {
  const height = headerEl.value?.offsetHeight ?? 0
  if (height > 0) {
    const value = `${height}px`
    // Keep both tokens in sync — scroll-padding and sticky chapters use either.
    document.documentElement.style.setProperty('--site-header-height', value)
    document.documentElement.style.setProperty('--header-height', value)
  }
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

watch(
  () => route.fullPath,
  async () => {
    closeMenu()
    await nextTick()
    syncHeaderHeight()
  },
)

onMounted(async () => {
  await nextTick()
  syncHeaderHeight()
  if (headerEl.value && typeof ResizeObserver !== 'undefined') {
    headerResizeObserver = new ResizeObserver(() => syncHeaderHeight())
    headerResizeObserver.observe(headerEl.value)
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  headerResizeObserver?.disconnect()
  headerResizeObserver = null
})
</script>

<style scoped>
/* Mellis-measured: top #fcf5f5 / book #de968d / nav muted #89868d / ink #27252a */
.site-header {
  --header-mellis-rose: #de968d;
  --header-mellis-cream: #fcf5f5;
  --header-mellis-muted: #89868d;
  --header-mellis-ink: #27252a;
  --header-side: 3.75rem; /* Mellis: 60px */

  position: sticky;
  top: 0;
  z-index: 50;
  background: #fff;
}

.site-header--menu-open {
  z-index: 60;
}

/* ========== TOP BAR ========== */
.site-header__top {
  display: none;
  align-items: stretch;
  height: 52px;
  background: var(--header-mellis-cream);
}

.site-header__top-body {
  display: flex;
  flex: 1 1 auto;
  align-items: center;
  justify-content: space-between;
  gap: 1.25rem;
  min-width: 0;
  padding-left: var(--header-side);
  padding-right: 1.25rem;
}

.site-header__contact {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 1.75rem 2.5rem;
  min-width: 0;
}

.site-header__chip {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  min-width: 0;
  color: var(--header-mellis-muted);
  font: 400 0.875rem/1.2 var(--font-body);
  text-decoration: none;
  white-space: nowrap;
}

.site-header__chip:last-child {
  overflow: hidden;
  text-overflow: ellipsis;
}

a.site-header__chip:hover,
a.site-header__chip:focus-visible {
  color: var(--header-mellis-rose);
}

a.site-header__chip:focus-visible,
.site-header__ig:focus-visible,
.site-header__book:focus-visible,
.site-header__nav a:focus-visible,
.site-header__menu-toggle:focus-visible {
  outline: 2px solid var(--header-mellis-rose);
  outline-offset: 3px;
}

.site-header__chip-icon {
  display: grid;
  place-items: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: var(--header-mellis-rose);
  color: #fff;
  flex-shrink: 0;
}

.site-header__chip-icon svg {
  width: 0.7rem;
  height: 0.7rem;
  fill: currentColor;
}

.site-header__top-tools {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-shrink: 0;
}

.site-header__ig {
  display: flex;
  color: var(--header-mellis-ink);
  transition: color 0.2s ease;
}

.site-header__ig:hover {
  color: var(--header-mellis-rose);
}

.site-header__ig svg {
  width: 14px;
  height: 14px;
  fill: currentColor;
}

/* Edge-flush Book now — Mellis: 52× ~202, pad 19px 60px, 12px/700, ls 2px */
.site-header__book {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  align-self: stretch;
  min-width: 12.625rem;
  margin-right: 0;
  padding: 0 3.75rem;
  background: var(--header-mellis-rose);
  color: #fff !important;
  font: 700 0.75rem/1 var(--font-body);
  letter-spacing: 2px;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s ease;
}

.site-header__book:hover {
  background: #d1857c;
}

/* ========== MAIN BAR ========== */
.site-header__main {
  background: #fff;
  box-shadow: 0 1px 0 rgba(39, 37, 42, 0.06);
}

.site-header__main-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  width: 100%;
  min-height: 4rem;
  padding:
    0.55rem max(1rem, env(safe-area-inset-right, 0px))
    0.55rem max(1rem, env(safe-area-inset-left, 0px));
}

.site-header__logo {
  flex-shrink: 0;
}

/* Match header rose to Mellis accents (tokens rose is slightly deeper) */
.site-header__logo :deep(.shee-logo__mark-wrap) {
  background: var(--header-mellis-rose);
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.35);
}

.site-header__nav {
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
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--header-mellis-cream);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.site-header__menu-line {
  display: block;
  width: 18px;
  height: 2px;
  border-radius: 1px;
  background: var(--header-mellis-ink);
  transition: transform 0.3s ease, opacity 0.3s ease, width 0.3s ease;
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

@media (max-width: 959px) {
  .site-header__main-inner {
    position: relative;
    justify-content: center;
    min-height: 4.25rem;
  }

  .site-header__logo {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    z-index: 1;
  }

  /* Stronger mobile brand mark — script Shee must read at a glance */
  .site-header__logo :deep(.shee-logo) {
    gap: 0.55rem;
  }

  .site-header__logo :deep(.shee-logo__mark-wrap) {
    width: 48px;
    height: 48px;
  }

  .site-header__logo :deep(.shee-logo__mark) {
    width: 28px;
    height: 28px;
  }

  .site-header__logo :deep(.shee-logo__name) {
    font-size: 1.85rem;
    line-height: 1;
  }

  .site-header__logo :deep(.shee-logo__tag) {
    font-size: 0.62rem;
    letter-spacing: 0.28em;
  }

  .site-header__menu-toggle {
    z-index: 2;
  }
}

@media (min-width: 960px) {
  .site-header__top {
    display: flex;
  }

  /* Full-bleed like Mellis — keep room for script logo */
  .site-header__main-inner {
    min-height: 72px;
    height: 72px;
    padding: 0 var(--header-side);
  }

  .site-header__logo :deep(.shee-logo__name) {
    font-size: 1.75rem;
  }

  /* Right-clustered menu — Mellis: 15px / 600 / pad 15px / ls 1px */
  .site-header__nav {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    margin-left: auto;
    gap: 0;
    height: 100%;
  }

  .site-header__nav a {
    display: inline-flex;
    align-items: center;
    height: 100%;
    padding: 0 15px;
    color: var(--header-mellis-muted);
    font: 600 15px/1 var(--font-body);
    letter-spacing: 1px;
    text-transform: uppercase;
    text-decoration: none;
    transition: color 0.2s ease;
  }

  .site-header__nav a:hover,
  .site-header__nav a.router-link-exact-active,
  .site-header__nav a.is-active {
    color: var(--header-mellis-ink);
  }

  /* Final nav CTA — rose so it reads with the edge Book now */
  .site-header__nav a:last-child {
    padding-right: 0;
    color: var(--header-mellis-rose);
  }

  .site-header__nav a:last-child:hover,
  .site-header__nav a:last-child.router-link-exact-active {
    color: var(--header-mellis-ink);
  }

  .site-header__menu-toggle {
    display: none !important;
  }
}

/* Mid desktop: drop location chip so email + edge Book stay calm */
@media (min-width: 960px) and (max-width: 1199px) {
  .site-header__contact .site-header__chip:not(a) {
    display: none;
  }

  .site-header__nav a {
    padding: 0 12px;
    font-size: 14px;
  }

  .site-header__book {
    min-width: 11rem;
    padding: 0 2.5rem;
  }
}

@media (min-width: 1400px) {
  .site-header {
    --header-side: 3.75rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-header__menu-line,
  .site-header__ig,
  .site-header__book,
  .site-header__nav a,
  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .menu-slide-enter-active,
  .menu-slide-leave-active {
    transition: none !important;
  }
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
  gap: 0.85rem;
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
</style>
