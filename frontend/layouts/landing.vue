<template>
  <div class="landing-shell">
    <SiteHeader />
    <slot />
    <SiteFooter />

    <aside class="mobile-book-bar" aria-label="Quick booking">
      <SiteButton to="/book" variant="primary" class="mobile-book-bar__cta">{{ LANDING_PRIMARY_CTA }}</SiteButton>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'

useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
  ],
})
</script>

<style scoped>
.landing-shell {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-paper);
}

.mobile-book-bar {
  display: flex;
  align-items: center;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 45;
  padding: 0.65rem 1rem calc(0.65rem + env(safe-area-inset-bottom, 0px));
  background: rgba(255, 255, 255, 0.96);
  border-top: 1px solid var(--color-line);
  box-shadow: 0 -8px 28px rgba(39, 37, 42, 0.08);
  backdrop-filter: blur(10px);
}

.mobile-book-bar__cta {
  width: 100%;
}

@media (min-width: 768px) {
  .mobile-book-bar {
    display: none;
  }
}
</style>
