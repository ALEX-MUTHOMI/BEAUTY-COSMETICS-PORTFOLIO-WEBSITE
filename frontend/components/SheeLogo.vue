<template>
  <NuxtLink :to="to" class="shee-logo" :class="{ 'shee-logo--light': variant === 'light' }">
    <img src="/images/logo-mark.png" alt="" class="shee-logo__mark" width="52" height="52" />
    <span class="shee-logo__text">
      <span class="shee-logo__name">Shee</span>
      <span class="shee-logo__tag">Aesthetics</span>
    </span>
  </NuxtLink>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    to?: string
    variant?: 'default' | 'light'
  }>(),
  { to: '/', variant: 'default' },
)
</script>

<style scoped>
.shee-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--color-ink);
}

.shee-logo__mark {
  flex-shrink: 0;
  width: 52px;
  height: 52px;
  object-fit: contain;
}

.shee-logo__text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.shee-logo__name {
  font: 700 1.35rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-ink);
}

.shee-logo__tag {
  font: 500 0.68rem/1.2 var(--font-body);
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.shee-logo--light .shee-logo__name,
.shee-logo--light .shee-logo__tag {
  color: #fff;
}

.shee-logo--light .shee-logo__tag {
  color: rgba(255, 255, 255, 0.75);
}
</style>
