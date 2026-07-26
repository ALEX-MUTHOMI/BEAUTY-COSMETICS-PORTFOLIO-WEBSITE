<template>
  <a
    class="ig-link"
    :class="[`ig-link--${variant}`, { 'ig-link--block': block }]"
    :href="LANDING_INSTAGRAM_URL"
    target="_blank"
    rel="noopener noreferrer"
    :aria-label="ariaLabel"
  >
    <svg class="ig-link__icon" viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">
      <path
        fill="currentColor"
        d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11zm0 2a3.5 3.5 0 1 0 0 7 3.5 3.5 0 0 0 0-7zm5.75-3.25a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5z"
      />
    </svg>
    <span class="ig-link__label">{{ label }}</span>
  </a>
</template>

<script setup lang="ts">
/**
 * Branded Instagram CTA — glyph + label for work footer, lightbox, site footer.
 */
import { LANDING_INSTAGRAM_URL } from '@/landing/landingContent'

withDefaults(
  defineProps<{
    label?: string
    ariaLabel?: string
    /** light = on dark panels; rose = on paper sections; ghost = footer list */
    variant?: 'light' | 'rose' | 'ghost'
    block?: boolean
  }>(),
  {
    label: 'More on Instagram',
    ariaLabel: 'Shee Aesthetics on Instagram',
    variant: 'rose',
    block: false,
  },
)
</script>

<style scoped>
.ig-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  min-height: 2.75rem;
  padding: 0.55rem 1.1rem;
  border: 1px solid transparent;
  text-decoration: none;
  font: 600 0.78rem/1.2 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  -webkit-tap-highlight-color: transparent;
  transition:
    color 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;
}

.ig-link--block {
  width: 100%;
}

.ig-link__icon {
  flex-shrink: 0;
}

.ig-link--rose {
  color: var(--color-rose-dark);
  background: rgba(176, 122, 113, 0.1);
  border-color: rgba(176, 122, 113, 0.28);
}

.ig-link--rose:hover,
.ig-link--rose:focus-visible {
  color: #fff;
  background: var(--color-rose);
  border-color: var(--color-rose);
}

.ig-link--light {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.4);
}

.ig-link--light:hover,
.ig-link--light:focus-visible {
  background: rgba(255, 255, 255, 0.16);
  border-color: #fff;
}

.ig-link--ghost {
  min-height: 0;
  padding: 0;
  gap: 0.45rem;
  color: rgba(255, 255, 255, 0.72);
  background: transparent;
  border: 0;
  font: 400 0.92rem/1.4 var(--font-body);
  letter-spacing: 0;
  text-transform: none;
}

.ig-link--ghost:hover,
.ig-link--ghost:focus-visible {
  color: var(--color-rose);
}

.ig-link--ghost .ig-link__icon {
  width: 1rem;
  height: 1rem;
}
</style>
