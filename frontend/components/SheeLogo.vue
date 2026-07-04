<template>
  <NuxtLink :to="to" class="shee-logo" :class="logoClasses" aria-label="Shee Aesthetics home">
    <img
      src="/images/logo-mark.png"
      alt=""
      class="shee-logo__mark"
      :width="markSize"
      :height="markSize"
    />
    <span class="shee-logo__text">
      <span class="shee-logo__name">Shee</span>
      <span class="shee-logo__tag">Aesthetics</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    to?: string
    variant?: 'default' | 'light' | 'hero'
    size?: 'md' | 'lg'
  }>(),
  { to: '/', variant: 'default', size: 'md' },
)

const markSize = computed(() => (props.size === 'lg' ? 64 : 54))

const logoClasses = computed(() => [
  props.variant !== 'default' ? `shee-logo--${props.variant}` : '',
  props.size === 'lg' ? 'shee-logo--lg' : '',
])
</script>

<style scoped>
.shee-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: var(--color-ink);
}

.shee-logo__mark {
  flex-shrink: 0;
  object-fit: contain;
}

.shee-logo__text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.shee-logo__name {
  font-family: var(--font-script);
  font-size: 2.15rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  color: var(--color-ink);
}

.shee-logo__tag {
  margin-top: 0.1rem;
  font-family: var(--font-display);
  font-size: 0.72rem;
  font-weight: 400;
  letter-spacing: 0.34em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.shee-logo--lg .shee-logo__name {
  font-size: clamp(2.5rem, 6vw, 3.75rem);
}

.shee-logo--lg .shee-logo__tag {
  font-size: 0.78rem;
  letter-spacing: 0.38em;
}

.shee-logo--light .shee-logo__name,
.shee-logo--hero .shee-logo__name {
  color: #fff;
}

.shee-logo--light .shee-logo__tag,
.shee-logo--hero .shee-logo__tag {
  color: rgba(255, 255, 255, 0.78);
}

.shee-logo--hero .shee-logo__mark {
  filter: brightness(0) invert(1);
}
</style>
