<template>
  <SiteLoader />
  <main class="home">
    <LandingHero />
    <LandingGlow />
    <LandingWork />
    <LandingOffer />
    <LandingSteps />
    <LandingPackages />
    <LandingReviews />
    <LandingVisit />
  </main>
</template>

<script setup lang="ts">
/**
 * Homepage composition (marketing only).
 * Section order: hero → Get to know us → Clients by Shee → offer → steps →
 * visit-path+packages → reviews → visit map.
 * Section SFCs live under `components/landing/`; data helpers under `src/landing/`.
 */
import { useLandingSeo } from '@/landing/useLandingSeo'

definePageMeta({ layout: 'landing' })
useLandingSeo()
</script>

<style scoped>
.home {
  background: var(--color-paper);
  margin: 0;
  padding: 0;
  /* Clear section rhythm — mobile first, breathing room between chapters */
  --home-section-y: clamp(2rem, 5vh, 2.75rem);
  --home-section-y-lg: clamp(2.35rem, 5.5vh, 3.25rem);
  --home-head-gap: 1.15rem;
  --home-seam: 1px solid rgba(44, 44, 48, 0.05);
}

/* Tablet and up — progressive enhancement */
@media (min-width: 768px) {
  .home {
    --home-section-y: 2rem;
    --home-section-y-lg: 2.25rem;
    --home-head-gap: 0.95rem;
  }
}

@media (min-width: 1024px) {
  .home {
    --home-section-y: 2.25rem;
    --home-section-y-lg: 2.5rem;
    --home-head-gap: 1rem;
  }
}
</style>
