<template>
  <Transition name="loader-fade">
    <div v-if="loading" class="site-loader" role="status" aria-live="polite" aria-label="Loading">
      <div class="site-loader__panel">
        <img src="/images/logo-mark.png" alt="" class="site-loader__mark" width="72" height="72" />
        <p class="site-loader__brand">Shee Aesthetics</p>
        <div class="site-loader__spinner" aria-hidden="true">
          <span />
          <span />
          <span />
        </div>
        <p class="site-loader__text">Loading…</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    assets?: string[]
  }>(),
  {
    assets: () => [
      '/images/hero-1.jpg',
      '/images/logo-mark.png',
    ],
  },
)

const loading = ref(true)

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function preload(src: string, timeoutMs = 4000): Promise<void> {
  return Promise.race([
    new Promise<void>((resolve) => {
      const img = new Image()
      const finish = () => resolve()
      img.addEventListener('load', finish, { once: true })
      img.addEventListener('error', finish, { once: true })
      img.src = src
      if (img.complete) finish()
    }),
    wait(timeoutMs),
  ])
}

onMounted(() => {
  const dismiss = () => {
    loading.value = false
  }

  // Never block the page longer than 2 seconds.
  const hardTimeout = setTimeout(dismiss, 2000)

  Promise.all([wait(500), ...props.assets.map((src) => preload(src))])
    .catch(() => undefined)
    .finally(() => {
      clearTimeout(hardTimeout)
      dismiss()
    })
})
</script>

<style scoped>
.site-loader {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  background: var(--color-cream);
}

.site-loader__panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1rem;
}

.site-loader__mark {
  animation: loader-pulse 1.4s ease-in-out infinite;
}

.site-loader__brand {
  margin: 0;
  font: 700 1.1rem var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-ink);
}

.site-loader__spinner {
  display: flex;
  gap: 0.45rem;
  margin-top: 0.25rem;
}

.site-loader__spinner span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-rose);
  animation: loader-bounce 1s ease-in-out infinite;
}

.site-loader__spinner span:nth-child(2) {
  animation-delay: 0.15s;
}

.site-loader__spinner span:nth-child(3) {
  animation-delay: 0.3s;
}

.site-loader__text {
  margin: 0;
  font: 500 0.82rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.loader-fade-leave-active {
  transition: opacity 0.55s var(--ease-story, ease), visibility 0.55s;
}

.loader-fade-leave-to {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

@keyframes loader-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.06);
    opacity: 0.85;
  }
}

@keyframes loader-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  40% {
    transform: translateY(-6px);
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-loader__mark,
  .site-loader__spinner span {
    animation: none;
  }
}
</style>
