<template>
  <component
    :is="linkTag"
    v-bind="linkAttrs"
    class="staff-shee-brand"
    :class="sizeClass"
    aria-label="Shee Aesthetics"
  >
    <span class="staff-shee-brand__mark" aria-hidden="true" />
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
  display: block;
  width: 2.75rem;
  height: 2.75rem;
  flex-shrink: 0;
  border-radius: 50%;
  /* Brand rose mark — never inverted by dark theme. */
  background-color: #c98980;
  background-image: url('/images/logo-mark.png');
  background-repeat: no-repeat;
  background-position: center;
  background-size: 1.55rem 1.55rem;
  box-shadow: 0 4px 14px rgba(201, 137, 128, 0.35);
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
  gap: 0.5rem;
}

.staff-shee-brand--sm .staff-shee-brand__mark {
  width: 2.25rem;
  height: 2.25rem;
  background-size: 1.25rem 1.25rem;
  box-shadow: 0 3px 10px rgba(201, 137, 128, 0.22);
}

.staff-shee-brand--sm .staff-shee-brand__name {
  font-size: 1.35rem;
}

.staff-shee-brand--sm .staff-shee-brand__tag {
  font-size: 0.58rem;
  letter-spacing: 0.24em;
}

@media (max-width: 380px) {
  .staff-shee-brand--sm .staff-shee-brand__tag {
    letter-spacing: 0.18em;
  }
}

.staff-shee-brand--lg .staff-shee-brand__mark {
  width: 3.4rem;
  height: 3.4rem;
  background-size: 1.9rem 1.9rem;
}

.staff-shee-brand--lg .staff-shee-brand__name {
  font-size: clamp(2.2rem, 6vw, 3rem);
}
</style>
