<template>
  <NuxtLink v-if="to" :to="to" class="site-btn" :class="variantClass" :aria-label="ariaLabel">
    <slot />
  </NuxtLink>
  <a v-else-if="href" :href="href" class="site-btn" :class="variantClass" :aria-label="ariaLabel">
    <slot />
  </a>
  <button v-else type="button" class="site-btn" :class="variantClass" :aria-label="ariaLabel">
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    to?: string
    href?: string
    variant?: 'primary' | 'ghost' | 'outline' | 'light' | 'ghost-light' | 'text'
    /**
     * Accessible name for screen readers.
     * Required if the button content is icon-only or visually obscured.
     */
    ariaLabel?: string
  }>(),
  { variant: 'primary' },
)

const variantClass = computed(() => `site-btn--${props.variant}`)
</script>

<style scoped>
.site-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  min-height: 2.75rem;
  padding: 0.85rem 1.75rem;
  font: 600 0.78rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
  transition:
    background-color 0.3s var(--ease-story),
    color 0.3s var(--ease-story),
    border-color 0.3s var(--ease-story),
    transform 0.3s var(--ease-story),
    box-shadow 0.3s var(--ease-story);
}

.site-btn:hover {
  transform: translateY(-2px);
}

.site-btn--primary {
  background: var(--color-rose);
  color: #fff;
}

.site-btn--primary:hover {
  background: var(--color-rose-dark);
}

.site-btn--outline {
  background: transparent;
  border-color: var(--color-line);
  color: var(--color-ink);
}

.site-btn--outline:hover {
  border-color: var(--color-rose);
  color: var(--color-rose);
}

.site-btn--ghost {
  background: var(--color-cream);
  color: var(--color-ink);
  letter-spacing: 0.06em;
  text-transform: none;
  font-weight: 500;
  font-size: 0.9rem;
}

.site-btn--ghost:hover {
  background: var(--color-rose-soft);
}

.site-btn--light {
  background: #fff;
  color: var(--color-ink);
}

.site-btn--light:hover {
  background: var(--color-cream);
}

.site-btn--ghost-light {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.35);
}

.site-btn--ghost-light:hover {
  background: rgba(255, 255, 255, 0.22);
}

.site-btn--text {
  background: transparent;
  color: var(--color-rose);
  padding: 0;
  letter-spacing: 0.14em;
}

.site-btn--text:hover {
  color: var(--color-rose-dark);
}
</style>
