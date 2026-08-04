<template>
  <div class="section-heading" :class="{ 'section-heading--center': align === 'center' }">
    <p v-if="eyebrow" class="section-heading__eyebrow">{{ eyebrow }}</p>
    <h2 class="section-heading__title">{{ title }}</h2>
    <p v-if="description" class="section-heading__description">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    eyebrow?: string
    title: string
    description?: string
    align?: 'left' | 'center'
  }>(),
  { align: 'center' },
)
</script>

<style scoped>
.section-heading {
  max-width: 62ch;
}

.section-heading--center {
  max-width: 52ch;
  margin-inline: auto;
  text-align: center;
}

.section-heading__eyebrow {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-rose);
}

.section-heading__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 500;
  font-size: clamp(2rem, 4.5vw, 2.75rem);
  line-height: 1.15;
  color: var(--color-ink);
}

.section-heading__description {
  margin: 1rem 0 0;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-text-muted);
}
</style>
