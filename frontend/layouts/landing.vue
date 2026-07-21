<template>
  <div class="landing-shell" :class="{ 'landing-shell--no-book-bar': !showMobileBookBar }">
    <SiteHeader />
    <slot />
    <SiteFooter />

    <aside
      v-if="showMobileBookBar"
      class="mobile-book-bar"
      aria-label="Quick booking"
    >
      <SiteButton to="/services" variant="primary" class="mobile-book-bar__cta">
        {{ LANDING_PRIMARY_CTA }}
      </SiteButton>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'

const route = useRoute()

/** Hide quick-book bar on transactional booking flows so Continue/Confirm stay tappable. */
const showMobileBookBar = computed(() => {
  const path = route.path || ''
  if (path === '/book' || path.startsWith('/book/')) return false
  if (path.startsWith('/booking/')) return false
  return true
})

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
  background: linear-gradient(
    to top,
    rgba(243, 242, 241, 0.98) 70%,
    rgba(243, 242, 241, 0.88)
  );
  border-top: 0;
  box-shadow: 0 -12px 32px rgba(39, 37, 42, 0.06);
  backdrop-filter: blur(12px);
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
