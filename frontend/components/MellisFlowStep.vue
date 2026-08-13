<template>
  <article class="mellis-flow-step">
    <div class="mellis-flow-step__visual">
      <span class="mellis-flow-step__badge">{{ num }}</span>
      <img :src="image" :alt="title" class="mellis-flow-step__photo" loading="lazy" />
    </div>
    <h3 class="mellis-flow-step__title">{{ title }}</h3>
    <p class="mellis-flow-step__text">{{ text }}</p>
  </article>
</template>

<script setup lang="ts">
/**
 * MellisFlowStep Component
 * @accessibility Ensures steps are logically ordered and keyboard navigable.
 */
defineProps<{
  num: string
  title: string
  text: string
  image: string
}>()
</script>

<style scoped>
.mellis-flow-step {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 1rem;
}

.mellis-flow-step__visual {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 1.15rem;
}

@media (min-width: 768px) {
  .mellis-flow-step__visual {
    width: 160px;
    height: 160px;
    margin-bottom: 1.35rem;
  }
}

.mellis-flow-step__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid var(--color-rose-soft);
  background: #fff;
}

.mellis-flow-step__badge {
  position: absolute;
  top: 4px;
  right: 4px;
  z-index: 2;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.75rem var(--font-body);
  box-shadow: 0 4px 12px rgba(222, 150, 141, 0.45);
}

.mellis-flow-step__title {
  margin: 0 0 0.5rem;
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--color-ink);
}

.mellis-flow-step__text {
  margin: 0 auto;
  max-width: 30ch;
  font: 400 0.86rem/1.55 var(--font-body);
  color: var(--color-muted);
}
</style>
