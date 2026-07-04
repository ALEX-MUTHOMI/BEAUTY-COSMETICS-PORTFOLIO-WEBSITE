<template>
  <article
    class="mellis-card"
    :class="{ 'mellis-card--featured': featured }"
  >
    <p v-if="badge" class="mellis-card__badge">{{ badge }}</p>
    <p class="mellis-card__days">Tue &amp; Wed only</p>
    <h3 class="mellis-card__title">{{ name }}</h3>
    <p class="mellis-card__price">{{ price }}</p>
    <p class="mellis-card__text">{{ text }}</p>
    <ul class="mellis-card__includes">
      <li v-for="item in includes" :key="item">{{ item }}</li>
    </ul>
    <SiteButton to="/book" :variant="featured ? 'primary' : 'outline'">
      Book Package Day
    </SiteButton>
  </article>
</template>

<script setup lang="ts">
defineProps<{
  name: string
  text: string
  price: string
  includes: string[]
  featured?: boolean
  badge?: string
}>()
</script>

<style scoped>
.mellis-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
  padding: 2.5rem 2rem 2.25rem;
  background: #fff;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  transition:
    transform 0.4s var(--ease-story),
    box-shadow 0.4s var(--ease-story),
    border-color 0.35s;
}

.mellis-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 22px 48px rgba(39, 37, 42, 0.12);
  border-top-color: var(--color-rose-dark);
}

.mellis-card--featured {
  background: var(--color-cream);
  border-top-width: 4px;
  box-shadow: 0 18px 42px rgba(222, 150, 141, 0.18);
}

.mellis-card__badge {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  margin: 0;
  padding: 0.35rem 1rem;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  white-space: nowrap;
}

.mellis-card__days {
  margin: 0 0 0.75rem;
  font: 600 0.68rem var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

.mellis-card__title {
  margin: 0 0 0.5rem;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--color-ink);
}

.mellis-card__price {
  margin: 0 0 1rem;
  font: 700 1.65rem var(--font-display);
  color: var(--color-rose-dark);
  line-height: 1.2;
}

.mellis-card__text {
  margin: 0 0 1.25rem;
  max-width: 28ch;
  font: 400 0.9rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.mellis-card__includes {
  list-style: none;
  margin: 0 0 1.75rem;
  padding: 0;
  width: 100%;
  text-align: left;
}

.mellis-card__includes li {
  position: relative;
  padding: 0.4rem 0 0.4rem 1.35rem;
  font: 500 0.86rem var(--font-body);
  color: var(--color-ink);
  border-bottom: 1px solid rgba(39, 37, 42, 0.06);
}

.mellis-card__includes li:last-child {
  border-bottom: none;
}

.mellis-card__includes li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-rose);
  transform: translateY(-50%);
}
</style>
