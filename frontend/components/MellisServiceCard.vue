<template>
  <NuxtLink :to="ctaTo" class="treat-tile">
    <div class="treat-tile__media">
      <img
        :src="image"
        :alt="name"
        class="treat-tile__photo"
        loading="lazy"
        decoding="async"
        width="640"
        height="800"
      />
    </div>
    <div class="treat-tile__caption">
      <h3 class="treat-tile__title">{{ displayName }}</h3>
      <span class="treat-tile__action">{{ ctaLabel }}</span>
    </div>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    name: string
    image: string
    ctaTo?: string
    ctaLabel?: string
  }>(),
  {
    ctaTo: '/services',
    ctaLabel: 'Explore',
  },
)

/** Short spa names — drop redundant “Care” where the photo already says it. */
const displayName = computed(() => {
  const n = props.name.trim()
  if (/facial/i.test(n)) return 'Facials'
  if (/massage/i.test(n)) return 'Massage'
  if (/wax/i.test(n)) return 'Waxing'
  if (/makeup|make-up|make up/i.test(n)) return 'Makeup'
  return n
})
</script>

<style scoped>
.treat-tile {
  display: flex;
  flex-direction: column;
  height: 100%;
  text-decoration: none;
  color: inherit;
  -webkit-tap-highlight-color: transparent;
}

.treat-tile__media {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4 / 5;
  background: var(--color-cream);
}

.treat-tile__photo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 30%;
  transition: transform 0.85s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1));
}

@media (hover: hover) {
  .treat-tile:hover .treat-tile__photo {
    transform: scale(1.05);
  }

  .treat-tile:hover .treat-tile__action {
    color: var(--color-rose-dark);
  }
}

.treat-tile__caption {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 1rem 0.5rem 0.25rem;
  text-align: center;
}

.treat-tile__title {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.15rem, 2.8vw, 1.4rem);
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: 0.01em;
  color: var(--color-ink);
}

.treat-tile__action {
  font-family: var(--font-body);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-rose);
  transition: color 0.25s ease;
}

.treat-tile:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 4px;
}
</style>
