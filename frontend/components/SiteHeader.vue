<template>
  <header class="site-header">
    <div class="site-header__top">
      <div class="site-header__top-inner">
        <div class="site-header__contact">
          <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
          <a href="tel:+254712000000">+254 712 000 000</a>
        </div>
        <div class="site-header__social" aria-label="Social links">
          <a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"/></svg></a>
          <a href="#" aria-label="Facebook"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 9V7.5c0-.83.67-1.5 1.5-1.5H16V3h-2.5C11.57 3 10 4.57 10 6.5V9H8v3h2v9h3v-9h2.5l.5-3H13z"/></svg></a>
          <a href="#" aria-label="Pinterest"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 0 0-3.17 17.45c-.08-.72-.15-1.83.03-2.62.17-.72 1.1-4.57 1.1-4.57s-.28-.56-.28-1.39c0-1.3.75-2.27 1.69-2.27.8 0 1.18.6 1.18 1.32 0 .8-.51 2-.78 3.11-.22.93.47 1.69 1.39 1.69 1.67 0 2.95-1.76 2.95-4.3 0-2.25-1.62-3.82-3.93-3.82-2.68 0-4.25 2.01-4.25 4.09 0 .81.31 1.68.7 2.15a.3.3 0 0 1 .07.28l-.27 1.08c-.04.18-.14.22-.33.13-1.24-.58-2.02-2.4-2.02-3.87 0-3.15 2.29-6.04 6.61-6.04 3.47 0 6.17 2.47 6.17 5.77 0 3.45-2.17 6.22-5.19 6.22-1.01 0-1.97-.53-2.3-1.15l-.63 2.4c-.23.88-.85 1.98-1.27 2.65A9 9 0 1 0 12 3z"/></svg></a>
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
          <SiteButton to="/book" variant="primary">Book Now</SiteButton>
        </div>

        <button
          class="site-header__menu-toggle"
          type="button"
          :aria-expanded="menuOpen"
          aria-controls="site-header-mobile-nav"
          aria-label="Toggle menu"
          @click="menuOpen = !menuOpen"
        >
          <span /><span /><span />
        </button>
      </div>
    </div>

    <div v-if="menuOpen" id="site-header-mobile-nav" class="site-header__mobile-nav">
      <NuxtLink to="/" @click="menuOpen = false">Home</NuxtLink>
      <NuxtLink to="/#services" @click="menuOpen = false">Our Services</NuxtLink>
      <NuxtLink to="/#packages" @click="menuOpen = false">Packages</NuxtLink>
      <NuxtLink to="/#singles" @click="menuOpen = false">Singles</NuxtLink>
      <NuxtLink to="/#gallery" @click="menuOpen = false">Gallery</NuxtLink>
      <NuxtLink to="/#contact" @click="menuOpen = false">Contact</NuxtLink>
      <SiteButton to="/book" variant="primary">Book Now</SiteButton>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const menuOpen = ref(false)
</script>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: var(--color-paper);
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

.site-header__contact a {
  color: var(--color-rose);
  text-decoration: none;
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
  gap: 2rem;
  padding: 1.15rem 0;
  border-bottom: 1px solid var(--color-line);
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
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  padding: 0.4rem;
  cursor: pointer;
  margin-left: auto;
}

.site-header__menu-toggle span {
  width: 24px;
  height: 2px;
  background: var(--color-ink);
}

.site-header__mobile-nav {
  display: none;
}

@media (max-width: 960px) {
  .site-header__top { display: none; }
  .site-header__nav, .site-header__actions { display: none; }
  .site-header__menu-toggle { display: flex; }
  .site-header__mobile-nav {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    padding: 0 1.5rem 1.25rem;
  }
  .site-header__mobile-nav a {
    text-decoration: none;
    font: 600 0.8rem var(--font-body);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--color-ink);
  }
}
</style>
