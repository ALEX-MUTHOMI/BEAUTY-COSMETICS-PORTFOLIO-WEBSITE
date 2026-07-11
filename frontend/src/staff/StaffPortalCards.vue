<template>
  <section class="portal-grid" :aria-label="label">
    <template v-if="loading">
      <article v-for="index in 4" :key="index" class="portal-card portal-card--skeleton" aria-label="Loading summary">
        <span />
        <strong />
        <span />
      </article>
    </template>
    <template v-else>
      <article v-for="card in cards" :key="card.label" class="portal-card">
        <p>{{ card.label }}</p>
        <strong>{{ card.value }}</strong>
        <span>{{ card.hint }}</span>
      </article>
    </template>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  cards: Array<{ label: string; value: string | number; hint: string }>
  loading?: boolean
}>()
</script>

<style scoped>
.portal-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.portal-card {
  min-height: 9rem;
  display: grid;
  align-content: space-between;
  padding: 1.2rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0;
  background: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
  box-shadow: var(--shadow-card, 0 0 40px rgba(39, 37, 42, 0.06));
  font-family: var(--font-body, 'Manrope', sans-serif);
}

.portal-card p,
.portal-card span {
  margin: 0;
  color: var(--color-muted, #89858d);
}

.portal-card strong {
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1;
}

.portal-card--skeleton span,
.portal-card--skeleton strong {
  min-height: 1rem;
  border-radius: 0;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), #fff, var(--color-rose-soft, #f5e8e6));
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

.portal-card--skeleton strong {
  min-height: 2.6rem;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 960px) {
  .portal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .portal-grid {
    grid-template-columns: 1fr;
  }
}
</style>
