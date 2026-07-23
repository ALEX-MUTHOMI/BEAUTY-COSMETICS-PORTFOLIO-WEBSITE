<template>
  <h1 class="hero-handwrite" :aria-label="text">
    <span
      v-for="(ch, i) in chars"
      :key="`${text}-${i}`"
      class="hero-handwrite__ch"
      :class="{ 'hero-handwrite__ch--space': ch === ' ' }"
      :style="{ '--i': i }"
      aria-hidden="true"
    >{{ ch === ' ' ? '\u00A0' : ch }}</span>
  </h1>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  text: string
}>()

const chars = computed(() => Array.from(props.text))
</script>

<style scoped>
.hero-handwrite {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  margin: 0;
  max-width: 14ch;
  font-family: var(--font-script);
  font-size: clamp(2.65rem, 11vw, 7.5rem);
  font-weight: 400;
  line-height: 1.02;
  letter-spacing: 0.01em;
  color: #fff;
  text-align: center;
  text-shadow: 0 2px 28px rgba(20, 16, 18, 0.32);
}

.hero-handwrite__ch {
  display: inline-block;
  opacity: 0;
  transform: translateY(0.12em) rotate(-4deg);
  filter: blur(1.5px);
  animation: hero-handwrite-draw 0.42s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: calc(var(--i) * 110ms + 220ms);
}

.hero-handwrite__ch--space {
  width: 0.28em;
  transform: none;
  filter: none;
  animation: hero-handwrite-space 0.01s linear forwards;
  animation-delay: calc(var(--i) * 110ms + 220ms);
}

@keyframes hero-handwrite-draw {
  0% {
    opacity: 0;
    transform: translateY(0.14em) rotate(-6deg) scale(0.92);
    filter: blur(2px);
  }
  40% {
    opacity: 1;
    filter: blur(0.5px);
  }
  100% {
    opacity: 1;
    transform: translateY(0) rotate(0deg) scale(1);
    filter: blur(0);
  }
}

@keyframes hero-handwrite-space {
  to {
    opacity: 1;
  }
}

@media (min-width: 768px) {
  .hero-handwrite {
    font-size: clamp(4.5rem, 11vw, 7.5rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero-handwrite__ch,
  .hero-handwrite__ch--space {
    opacity: 1;
    transform: none;
    filter: none;
    animation: none;
  }
}
</style>
