<template>
  <NuxtLink :to="to" class="shee-logo" :class="logoClasses" aria-label="Shee Aesthetics home">
    <span class="shee-logo__mark-wrap" aria-hidden="true">
      <img
        src="/images/logo-mark.png"
        alt=""
        class="shee-logo__mark"
        :width="markSize"
        :height="markSize"
      />
    </span>
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

const markSize = computed(() => (props.size === 'lg' ? 34 : 30))

const logoClasses = computed(() => [
  props.variant !== 'default' ? `shee-logo--${props.variant}` : '',
  props.size === 'lg' ? 'shee-logo--lg' : '',
])
</script>

<style scoped>
.shee-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  text-decoration: none;
  color: var(--color-ink);
  flex-shrink: 0;
}

.shee-logo__mark-wrap {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-rose);
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.35);
}

.shee-logo__mark {
  width: 30px;
  height: 30px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.shee-logo--lg .shee-logo__mark-wrap {
  width: 64px;
  height: 64px;
}

.shee-logo--lg .shee-logo__mark {
  width: 36px;
  height: 36px;
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

.shee-logo--light .shee-logo__mark-wrap,
.shee-logo--hero .shee-logo__mark-wrap {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow: none;
}
</style>
