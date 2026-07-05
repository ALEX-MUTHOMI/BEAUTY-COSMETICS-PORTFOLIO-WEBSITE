<template>
  <Transition name="loader-fade">
    <div
      v-if="visible"
      class="site-loader"
      role="status"
      aria-live="polite"
      aria-label="Loading Shee Aesthetics"
    >
      <div class="site-loader__panel">
        <div class="site-loader__ring" aria-hidden="true">
          <span />
        </div>
        <img src="/images/logo-mark.png" alt="" class="site-loader__mark" width="80" height="80" />
        <p class="site-loader__brand">Shee Aesthetics</p>
        <p class="site-loader__text">Loading…</p>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    minDuration?: number
    assets?: string[]
  }>(),
  {
    minDuration: 450,
    assets: () => ['/images/hero-1.jpg', '/images/logo-mark.png'],
  },
)

const visible = ref(true)

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function preload(src: string, timeoutMs = 1800): Promise<void> {
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
  const started = Date.now()
  const maxWait = props.minDuration + 900

  const dismiss = () => {
    visible.value = false
    document.documentElement.classList.add('site-ready')
    document.documentElement.classList.remove('is-loading')
  }

  const safety = setTimeout(dismiss, maxWait)

  Promise.all([...props.assets.map((src) => preload(src))])
    .catch(() => undefined)
    .finally(() => {
      clearTimeout(safety)
      const remaining = Math.max(0, props.minDuration - (Date.now() - started))
      wait(remaining).then(dismiss)
    })
})
</script>

<style scoped>
.site-loader {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: grid;
  place-items: center;
  background: var(--color-cream);
}

.site-loader__panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.15rem;
  position: relative;
}

.site-loader__ring {
  position: absolute;
  top: -18px;
  width: 116px;
  height: 116px;
}

.site-loader__ring span {
  display: block;
  width: 100%;
  height: 100%;
  border: 2px solid var(--color-rose-soft);
  border-top-color: var(--color-rose);
  border-radius: 50%;
  animation: loader-spin 1.1s linear infinite;
}

.site-loader__mark {
  animation: loader-pulse 1.6s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

.site-loader__brand {
  margin: 0;
  font: 700 1.05rem system-ui, -apple-system, 'Segoe UI', sans-serif;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-ink);
}

.site-loader__text {
  margin: 0;
  font: 500 0.78rem system-ui, -apple-system, 'Segoe UI', sans-serif;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.loader-fade-leave-active {
  transition:
    opacity 0.3s var(--ease-story, ease),
    visibility 0.3s;
}

.loader-fade-leave-to {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

@keyframes loader-spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes loader-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.88;
  }
}

@media (prefers-reduced-motion: reduce) {
  .site-loader__mark,
  .site-loader__ring span {
    animation: none;
  }
}
</style>
