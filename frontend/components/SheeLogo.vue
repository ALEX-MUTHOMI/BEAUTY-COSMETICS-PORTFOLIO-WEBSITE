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
    size?: 'sm' | 'md' | 'lg'
    /** Home 3: mark above name, centered column */
    layout?: 'inline' | 'stacked'
  }>(),
  { to: '/', variant: 'default', size: 'md', layout: 'inline' },
)

const markSize = computed(() => {
  if (props.layout === 'stacked') {
    if (props.size === 'lg') return 40
    if (props.size === 'sm') return 28
    return 34
  }
  if (props.size === 'lg') return 36
  if (props.size === 'sm') return 26
  return 30
})

const logoClasses = computed(() => [
  props.variant !== 'default' ? `shee-logo--${props.variant}` : '',
  props.size !== 'md' ? `shee-logo--${props.size}` : '',
  props.layout === 'stacked' ? 'shee-logo--stacked' : '',
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
  width: 46px;
  height: 46px;
  border-radius: 50%;
  background: var(--color-rose);
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.35);
}

.shee-logo__mark {
  width: 26px;
  height: 26px;
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

.shee-logo--sm {
  gap: 0.65rem;
}

.shee-logo--sm .shee-logo__mark-wrap {
  width: 44px;
  height: 44px;
}

.shee-logo--sm .shee-logo__mark {
  width: 26px;
  height: 26px;
}

.shee-logo--sm .shee-logo__name {
  font-size: 1.65rem;
}

.shee-logo--sm .shee-logo__tag {
  font-size: 0.62rem;
  letter-spacing: 0.28em;
}

.shee-logo__text {
  display: flex;
  flex-direction: column;
  line-height: 1.05;
}

.shee-logo__name {
  font-family: var(--font-script);
  font-size: 1.85rem;
  font-weight: 400;
  letter-spacing: 0.02em;
  line-height: 1;
  color: var(--color-ink);
}

.shee-logo__tag {
  margin-top: 0.15rem;
  font-family: var(--font-body);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.shee-logo--lg .shee-logo__name {
  font-size: clamp(2.25rem, 5vw, 3.25rem);
}

.shee-logo--lg .shee-logo__tag {
  font-size: 0.72rem;
  letter-spacing: 0.32em;
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

/* Mellis Home 3 — mark above brand, centered */
.shee-logo--stacked {
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  text-align: center;
}

.shee-logo--stacked .shee-logo__text {
  align-items: center;
}

.shee-logo--stacked .shee-logo__name {
  font-size: clamp(1.85rem, 2.4vw, 2.35rem);
  letter-spacing: 0.04em;
}

.shee-logo--stacked .shee-logo__tag {
  margin-top: 0.2rem;
  font-size: 0.68rem;
  letter-spacing: 0.32em;
}

.shee-logo--stacked.shee-logo--sm .shee-logo__mark-wrap {
  width: 52px;
  height: 52px;
}

.shee-logo--stacked.shee-logo--sm .shee-logo__mark {
  width: 28px;
  height: 28px;
}

.shee-logo--stacked.shee-logo--sm .shee-logo__name {
  font-size: clamp(1.65rem, 4vw, 2rem);
}

.shee-logo--stacked.shee-logo--md .shee-logo__mark-wrap,
.shee-logo--stacked:not(.shee-logo--sm):not(.shee-logo--lg) .shee-logo__mark-wrap {
  width: 58px;
  height: 58px;
}

.shee-logo--stacked:not(.shee-logo--sm):not(.shee-logo--lg) .shee-logo__mark {
  width: 32px;
  height: 32px;
}

.shee-logo--stacked.shee-logo--light .shee-logo__mark-wrap,
.shee-logo--stacked.shee-logo--hero .shee-logo__mark-wrap {
  background: transparent;
  border: 1.5px solid rgba(255, 255, 255, 0.85);
  box-shadow: none;
}

.shee-logo--stacked.shee-logo--light .shee-logo__tag,
.shee-logo--stacked.shee-logo--hero .shee-logo__tag {
  color: rgba(255, 255, 255, 0.88);
}
</style>
