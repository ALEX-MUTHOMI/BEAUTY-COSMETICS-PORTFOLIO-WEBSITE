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
  gap: 0.85rem;
}

.portal-card {
  min-height: 8.25rem;
  display: grid;
  align-content: space-between;
  gap: 0.55rem;
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.1));
  border-radius: 0;
  background: var(--color-paper, #fffcf8);
  box-shadow: var(--shadow-card, 0 0 40px rgba(39, 37, 42, 0.05));
  font-family: var(--font-body, 'Manrope', sans-serif);
}

.portal-card p,
.portal-card span {
  margin: 0;
  color: var(--color-muted, #89858d);
}

.portal-card p {
  font: 600 0.72rem/1.2 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.portal-card span {
  font-size: 0.82rem;
  line-height: 1.35;
}

.portal-card strong {
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(1.75rem, 3.2vw, 2.75rem);
  font-weight: 400;
  line-height: 1;
  letter-spacing: -0.02em;
}

.portal-card--skeleton span,
.portal-card--skeleton strong {
  min-height: 1rem;
  border-radius: 0;
  background: linear-gradient(90deg, var(--color-rose-soft, #f5e8e6), var(--color-stone, #efeae3), var(--color-rose-soft, #f5e8e6));
  animation: staff-shimmer 1.2s ease-in-out infinite;
}

.portal-card--skeleton strong {
  min-height: 2.4rem;
}

@keyframes staff-shimmer {
  50% {
    opacity: 0.45;
  }
}

@media (max-width: 1024px) {
  .portal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .portal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
  }

  .portal-card {
    min-height: 0;
    padding: 0.9rem 0.85rem;
    gap: 0.4rem;
  }

  .portal-card strong {
    font-size: clamp(1.5rem, 8vw, 1.9rem);
  }

  .portal-card span {
    font-size: 0.75rem;
  }
}
</style>
