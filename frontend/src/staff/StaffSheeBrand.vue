<template>
  <component
    :is="linkTag"
    v-bind="linkAttrs"
    class="staff-shee-brand"
    :class="sizeClass"
    aria-label="Shee Aesthetics"
  >
    <span class="staff-shee-brand__mark" aria-hidden="true">S</span>
    <span class="staff-shee-brand__text">
      <span class="staff-shee-brand__name">Shee</span>
      <span class="staff-shee-brand__tag">Aesthetics</span>
    </span>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    to?: string
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { to: '', size: 'md' },
)

const sizeClass = computed(() => (props.size !== 'md' ? `staff-shee-brand--${props.size}` : ''))
const linkTag = computed(() => (props.to ? 'a' : 'div'))
const linkAttrs = computed(() => (props.to ? { href: props.to } : {}))
</script>

<style scoped>
.staff-shee-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: var(--color-ink, #27272a);
}

.staff-shee-brand__mark {
  display: grid;
  place-items: center;
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
  background: var(--color-rose, #de968d);
  color: #fff;
  font: 700 1rem/1 var(--font-display, 'Libre Baskerville', Georgia, serif);
}

.staff-shee-brand__text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.staff-shee-brand__name {
  font-family: var(--font-script, 'Parisienne', cursive);
  font-size: 1.85rem;
  font-weight: 400;
}

.staff-shee-brand__tag {
  margin-top: 0.1rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 0.68rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--color-muted, #89858d);
}

.staff-shee-brand--sm {
  gap: 0.55rem;
}

.staff-shee-brand--sm .staff-shee-brand__mark {
  width: 2.35rem;
  height: 2.35rem;
}

.staff-shee-brand--sm .staff-shee-brand__name {
  font-size: 1.45rem;
}

.staff-shee-brand--lg .staff-shee-brand__mark {
  width: 3.4rem;
  height: 3.4rem;
  font-size: 1.2rem;
}

.staff-shee-brand--lg .staff-shee-brand__name {
  font-size: clamp(2.2rem, 6vw, 3rem);
}
</style>
