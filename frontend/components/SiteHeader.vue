<template>
  <header class="site-header" :class="{ 'site-header--menu-open': menuOpen }">
    <div class="site-header__top">
      <div class="site-header__top-inner">
        <div class="site-header__contact">
          <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
          <NuxtLink to="/book" class="site-header__policy">Pay online to book</NuxtLink>
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
        <SheeLogo />

        <nav class="site-header__nav" aria-label="Primary">
          <NuxtLink to="/">Home</NuxtLink>
          <NuxtLink to="/#services">Our Services</NuxtLink>
          <NuxtLink to="/#packages">Packages</NuxtLink>
          <NuxtLink to="/#singles">Singles</NuxtLink>
          <NuxtLink to="/#gallery">Gallery</NuxtLink>
          <NuxtLink to="/#contact">Contact</NuxtLink>
        </nav>

        <div class="site-header__actions">
          <SiteButton to="/book" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
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
          @click="menuOpen = false"
        />
      </Transition>
      <Transition name="menu-slide">
        <nav
          v-if="menuOpen"
          id="site-header-mobile-nav"
          class="site-header__drawer"
          aria-label="Mobile"
        >
          <p class="site-header__drawer-label">{{ LANDING_LOCATION_LABEL }}</p>
          <NuxtLink to="/" @click="closeMenu">Home</NuxtLink>
          <NuxtLink to="/#services" @click="closeMenu">Services</NuxtLink>
          <NuxtLink to="/#packages" @click="closeMenu">Packages</NuxtLink>
          <NuxtLink to="/#singles" @click="closeMenu">Singles</NuxtLink>
          <NuxtLink to="/#gallery" @click="closeMenu">Gallery</NuxtLink>
          <NuxtLink to="/#contact" @click="closeMenu">Contact</NuxtLink>
          <SiteButton to="/book" variant="primary" class="site-header__drawer-cta" @click="closeMenu">
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

.site-header__main-inner {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-line);
}

@media (min-width: 768px) {
  .site-header__main-inner {
    gap: 2rem;
    padding: 1.15rem 0;
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
  margin-left: auto;
  min-width: 44px;
  min-height: 44px;
  padding: 0.5rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  background: var(--color-cream);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.25s,
    background-color 0.25s;
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
  background: rgba(39, 37, 42, 0.35);
  backdrop-filter: blur(2px);
}

.site-header__drawer {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 56;
  display: flex;
  flex-direction: column;
  gap: 0;
  width: min(18rem, 86vw);
  height: 100dvh;
  padding: calc(4.75rem + env(safe-area-inset-top, 0px)) 1.5rem 1.5rem;
  background: var(--color-paper);
  border-left: 1px solid var(--color-line);
  box-shadow: -12px 0 40px rgba(39, 37, 42, 0.1);
}

.site-header__drawer-label {
  margin: 0 0 1.25rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.site-header__drawer a {
  padding: 0.85rem 0;
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
  text-decoration: none;
  font: 500 0.95rem var(--font-body);
  color: var(--color-ink);
  transition: color 0.2s;
}

.site-header__drawer a:hover {
  color: var(--color-rose);
}

.site-header__drawer-cta {
  width: 100%;
  margin-top: auto;
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.28s ease;
}

.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
}

.menu-slide-enter-active,
.menu-slide-leave-active {
  transition: transform 0.32s var(--ease-story);
}

.menu-slide-enter-from,
.menu-slide-leave-to {
  transform: translateX(100%);
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
}

@media (prefers-reduced-motion: reduce) {
  .site-header__menu-line,
  .menu-fade-enter-active,
  .menu-fade-leave-active,
  .menu-slide-enter-active,
  .menu-slide-leave-active {
    transition: none;
  }
}
</style>
