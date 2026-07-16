<template>
  <header class="site-header" :class="{ 'site-header--menu-open': menuOpen }">
    <div class="site-header__top">
      <div class="site-header__top-inner">
        <div class="site-header__contact">
          <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
          <NuxtLink to="/services" class="site-header__policy">Pay online to book</NuxtLink>
        </div>
        <div class="site-header__social" aria-label="Social links">
          <a :href="LANDING_INSTAGRAM_URL" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"/></svg>
          </a>
        </div>
      </div>
    </div>

    <div class="site-header__main">
      <div class="site-header__main-inner">
        <SheeLogo class="site-header__logo" />

        <nav class="site-header__nav" aria-label="Primary">
          <NuxtLink to="/">Home</NuxtLink>
          <NuxtLink to="/services">Our Services</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.fullPackages">Packages</NuxtLink>
          <NuxtLink :to="SERVICES_ROUTES.singleSessions">Singles</NuxtLink>
          <NuxtLink to="/#gallery">Gallery</NuxtLink>
          <NuxtLink to="/#contact">Contact</NuxtLink>
        </nav>

        <div class="site-header__actions">
          <SiteButton to="/services" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
        </div>

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
          <button
            type="button"
            class="site-header__drawer-close"
            aria-label="Close menu"
            @click="closeMenu"
          >
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
            <NuxtLink to="/#gallery" @click="closeMenu">Gallery</NuxtLink>
            <NuxtLink to="/#contact" @click="closeMenu">Contact</NuxtLink>
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
import { onUnmounted, ref, watch } from 'vue'
import {
  LANDING_INSTAGRAM_URL,
  LANDING_LOCATION_LABEL,
  LANDING_PRIMARY_CTA,
} from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'

const menuOpen = ref(false)

function closeMenu() {
  menuOpen.value = false
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onUnmounted(() => {
  document.body.style.overflow = ''
})
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--color-paper);
}

.site-header--menu-open {
  z-index: 60;
}

.site-header__top {
  background: var(--color-cream);
  border-bottom: 1px solid rgba(222, 150, 141, 0.12);
}

.site-header__top-inner,
.site-header__main-inner {
  width: var(--container);
  margin: 0 auto;
}

.site-header__top-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0;
  font: 500 0.82rem var(--font-body);
}

.site-header__contact {
  display: flex;
  flex-wrap: wrap;
  gap: 1.75rem;
}

.site-header__contact a,
.site-header__policy {
  color: var(--color-rose);
  text-decoration: none;
}

.site-header__policy {
  font-weight: 600;
  letter-spacing: 0.04em;
}

.site-header__social {
  display: flex;
  gap: 0.85rem;
}

.site-header__social a {
  color: var(--color-rose);
  display: flex;
}

.site-header__social svg {
  width: 15px;
  height: 15px;
  fill: currentColor;
}

.site-header--menu-open .site-header__menu-toggle {
  visibility: hidden;
  pointer-events: none;
}

.site-header__main-inner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  max-width: none;
  padding:
    0.65rem max(1rem, env(safe-area-inset-right, 0px))
    0.65rem max(1rem, env(safe-area-inset-left, 0px));
  border-bottom: 1px solid var(--color-line);
}

.site-header__logo {
  min-width: 0;
  flex: 1 1 auto;
}

@media (max-width: 959px) {
  .site-header__logo :deep(.shee-logo) {
    gap: 0.65rem;
  }

  .site-header__logo :deep(.shee-logo__mark-wrap) {
    width: 44px;
    height: 44px;
  }

  .site-header__logo :deep(.shee-logo__mark) {
    width: 26px;
    height: 26px;
  }

  .site-header__logo :deep(.shee-logo__name) {
    font-size: 1.65rem;
  }

  .site-header__logo :deep(.shee-logo__tag) {
    font-size: 0.62rem;
    letter-spacing: 0.28em;
  }
}

@media (min-width: 768px) {
  .site-header__main-inner {
    width: var(--container);
    max-width: var(--container);
    margin: 0 auto;
    gap: 2rem;
    padding: 1.15rem 0;
  }
}

@media (min-width: 960px) {
  .site-header__logo {
    flex: 0 0 auto;
  }
}

.site-header__nav {
  display: flex;
  gap: 2.25rem;
  margin-right: auto;
  margin-left: 0.5rem;
}

.site-header__nav a {
  text-decoration: none;
  color: var(--color-ink);
  font: 600 0.75rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.site-header__nav a:hover {
  color: var(--color-rose);
}

.site-header__menu-toggle {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 5px;
  flex-shrink: 0;
  margin-left: auto;
  min-width: 48px;
  min-height: 48px;
  padding: 0.65rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--color-cream);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.25s,
    background-color 0.25s,
    visibility 0.2s;
}

.site-header__menu-toggle--open {
  border-color: var(--color-rose-soft);
  background: #fff;
}

.site-header__menu-line {
  display: block;
  width: 18px;
  height: 2px;
  border-radius: 1px;
  background: var(--color-ink);
  transition:
    transform 0.3s var(--ease-story),
    opacity 0.3s var(--ease-story),
    width 0.3s var(--ease-story);
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

.site-header__backdrop {
  position: fixed;
  inset: 0;
  z-index: 55;
  background: rgba(39, 37, 42, 0.4);
}

.site-header__drawer {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: none;
  height: 100dvh;
  padding:
    calc(1.5rem + env(safe-area-inset-top, 0px))
    max(1.5rem, env(safe-area-inset-right, 0px))
    calc(2rem + env(safe-area-inset-bottom, 0px))
    max(1.5rem, env(safe-area-inset-left, 0px));
  background: var(--color-paper);
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

.site-header__drawer-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
  margin-top: 0.5rem;
  margin-bottom: 2.25rem;
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
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  padding: 0;
  border: 1px solid var(--color-line);
  border-radius: 50%;
  background: #fff;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
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
  background: var(--color-ink);
  border-radius: 1px;
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
  gap: 0.15rem;
  flex: 1;
}

.site-header__drawer-links a {
  display: flex;
  align-items: center;
  min-height: 3rem;
  padding: 0.85rem 0.25rem;
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
  text-decoration: none;
  font: 500 1.125rem var(--font-body);
  letter-spacing: 0.02em;
  color: var(--color-ink);
  transition: color 0.2s, padding-left 0.2s;
}

.site-header__drawer-links a:hover,
.site-header__drawer-links a:focus-visible {
  color: var(--color-rose);
  padding-left: 0.35rem;
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
  transition:
    transform 0.3s var(--ease-story),
    opacity 0.3s ease;
}

.menu-slide-enter-from,
.menu-slide-leave-to {
  transform: translateY(12px);
  opacity: 0;
}

@media (min-width: 960px) {
  .site-header__top { display: block; }
  .site-header__nav,
  .site-header__actions { display: flex; }
  .site-header__menu-toggle { display: none; }
}

@media (max-width: 959px) {
  .site-header__top { display: none; }
  .site-header__nav,
  .site-header__actions { display: none; }

  .site-header__backdrop {
    z-index: 65;
  }
}

@media (min-width: 960px) {
  .site-header__drawer {
    inset: auto 0 0 auto;
    width: min(100%, 26rem);
    box-shadow: -16px 0 48px rgba(39, 37, 42, 0.12);
  }

  .menu-slide-enter-from,
  .menu-slide-leave-to {
    transform: translateX(100%);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-header__menu-line,
  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .menu-slide-enter-active,
  .menu-slide-leave-active,
  .site-header__drawer-links a {
    transition: none;
  }
}
</style>
