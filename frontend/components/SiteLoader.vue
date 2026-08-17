<template>
  <Transition name="loader-fade">
    <div
      v-if="visible"
      class="site-boot-skeleton site-loader"
      :class="{ 'site-boot-skeleton--services': variant === 'services' }"
      role="status"
      aria-live="polite"
      aria-label="Loading Shee Aesthetics"
    >
      <div class="site-boot-skeleton__frame" aria-hidden="true">
        <span class="skel-watermark" />

        <header class="skel-header">
          <div class="skel-header__brand">
            <span class="skel-header__mark skel-bone" />
            <span class="skel-header__wordmark skel-bone" />
          </div>
          <span class="skel-header__nav skel-bone skel-header__nav--desktop" />
          <span class="skel-header__menu skel-bone" />
        </header>

        <template v-if="variant === 'services'">
          <section class="skel-services-hero">
            <span class="skel-bar skel-bar--eyebrow skel-bone" />
            <span class="skel-bar skel-bar--services-title skel-bone" />
          </section>

          <section class="skel-band skel-band--doors">
            <div class="skel-doors">
              <span class="skel-door skel-door--dark skel-bone skel-bone--charcoal" />
              <span class="skel-door skel-door--dark skel-bone skel-bone--charcoal" />
            </div>
          </section>

          <section class="skel-band">
            <div class="skel-band__head">
              <span class="skel-bar skel-bar--section skel-bone" />
            </div>
            <div class="skel-services-cats">
              <span class="skel-cat skel-bone skel-bone--charcoal" />
              <span class="skel-cat skel-bone skel-bone--charcoal" />
              <span class="skel-cat skel-bone skel-bone--charcoal" />
              <span class="skel-cat skel-bone skel-bone--charcoal" />
            </div>
            <div class="skel-services-panel skel-bone skel-bone--charcoal" />
          </section>
        </template>

        <template v-else>
          <!-- Soft IG-style bone placeholders mirroring homepage chapters -->
          <section class="skel-hero">
            <div class="skel-hero__media skel-bone skel-bone--hero" />
            <div class="skel-hero__copy">
              <span class="skel-bar skel-bar--eyebrow skel-bone skel-bone--soft" />
              <span class="skel-bar skel-bar--title skel-bone skel-bone--soft" />
              <span class="skel-bar skel-bar--price skel-bone skel-bone--soft" />
              <span class="skel-bar skel-bar--cta skel-bone skel-bone--soft" />
            </div>
            <div class="skel-hero__dots">
              <span class="skel-dot skel-bone skel-bone--soft" />
              <span class="skel-dot skel-bone skel-bone--soft" />
              <span class="skel-dot skel-bone skel-bone--soft" />
              <span class="skel-dot skel-bone skel-bone--soft" />
            </div>
          </section>

          <section class="skel-band skel-band--welcome">
            <div class="skel-welcome">
              <span class="skel-welcome__media skel-bone" />
              <div class="skel-welcome__copy">
                <span class="skel-bar skel-bar--section skel-bone" />
                <span class="skel-bar skel-bar--line skel-bone" />
                <span class="skel-bar skel-bar--line skel-bar--line-short skel-bone" />
              </div>
            </div>
          </section>

          <section class="skel-band">
            <div class="skel-band__head">
              <span class="skel-bar skel-bar--section skel-bone" />
            </div>
            <div class="skel-band__tiles">
              <span class="skel-tile skel-bone" />
              <span class="skel-tile skel-bone" />
              <span class="skel-tile skel-bone" />
              <span class="skel-tile skel-bone" />
            </div>
          </section>

          <section class="skel-band skel-band--offer">
            <div class="skel-band__head">
              <span class="skel-bar skel-bar--section skel-bone skel-bone--on-dark" />
            </div>
            <div class="skel-offer">
              <span class="skel-offer__cell skel-bone skel-bone--charcoal" />
              <span class="skel-offer__cell skel-bone skel-bone--charcoal" />
              <span class="skel-offer__cell skel-bone skel-bone--charcoal" />
              <span class="skel-offer__cell skel-bone skel-bone--charcoal" />
            </div>
          </section>

          <section class="skel-band skel-band--doors">
            <div class="skel-doors">
              <span class="skel-door skel-door--dark skel-bone skel-bone--charcoal" />
              <span class="skel-door skel-door--photo skel-bone skel-bone--photo" />
            </div>
          </section>
        </template>
      </div>

      <div class="site-boot-skeleton__dock">
        <span class="skel-dock-cta skel-bone" />
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
/**
 * SiteLoader Component
 * Uses aria-live="polite" to inform screen readers of background loading processes.
 */
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { loaderSafetyTimeoutMs } from '~/src/landing/landingContent'

const props = withDefaults(
  defineProps<{
    minDuration?: number
    assets?: string[]
    variant?: 'home' | 'services'
  }>(),
  {
    minDuration: 650,
    assets: () => ['/images/hero-makeup-960.jpg', '/images/logo-mark.png'],
    variant: 'home',
  },
)

const LOADER_SESSION_KEY = 'shee-loader-done'

function readLoaderDone(): boolean {
  if (!import.meta.client) return false
  try {
    if (localStorage.getItem(LOADER_SESSION_KEY) === '1') return true
    if (sessionStorage.getItem(LOADER_SESSION_KEY) === '1') return true
  } catch {
    /* ignore */
  }
  return false
}

function writeLoaderDone(): void {
  if (!import.meta.client) return
  try {
    localStorage.setItem(LOADER_SESSION_KEY, '1')
    sessionStorage.setItem(LOADER_SESSION_KEY, '1')
  } catch {
    /* ignore */
  }
}

/** SiteLoader alone owns html.is-loading — never set it permanently via page useHead. */
const alreadyDone = readLoaderDone()

const visible = ref(!alreadyDone)

useHead(() => ({
  htmlAttrs: {
    class: visible.value ? 'is-loading' : undefined,
  },
}))

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function preload(src: string, timeoutMs = 1200): Promise<void> {
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

function markReady() {
  visible.value = false
  if (import.meta.client) {
    document.documentElement.classList.add('site-ready', 'site-motion')
    document.documentElement.classList.remove('is-loading')
  }
}

onMounted(() => {
  if (alreadyDone || readLoaderDone()) {
    markReady()
    return
  }

  const started = Date.now()
  const maxWait = loaderSafetyTimeoutMs(props.minDuration)

  const dismiss = () => {
    markReady()
    writeLoaderDone()
  }

  const safety = setTimeout(dismiss, maxWait)

  Promise.all(props.assets.map((src) => preload(src)))
    .catch(() => undefined)
    .finally(() => {
      clearTimeout(safety)
      const remaining = Math.max(0, props.minDuration - (Date.now() - started))
      wait(remaining).then(dismiss)
    })
})

onUnmounted(() => {
  if (import.meta.client) {
    document.documentElement.classList.remove('is-loading')
  }
})
</script>

<style scoped>
.site-boot-skeleton {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: flex;
  flex-direction: column;
  background: var(--color-paper, #e5e1dc);
  pointer-events: none;
  overflow: hidden;
}

.site-boot-skeleton__frame {
  position: relative;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.skel-watermark {
  position: absolute;
  inset: 12% auto auto 55%;
  z-index: 0;
  width: min(42vw, 14rem);
  height: min(42vw, 14rem);
  background-image: url('/images/flower.png');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.04;
  pointer-events: none;
  filter: saturate(0.8);
}

.skel-header {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-shrink: 0;
  padding:
    calc(0.75rem + env(safe-area-inset-top, 0px))
    1.1rem
    0.7rem;
  background: color-mix(in srgb, var(--color-paper, #e5e1dc) 92%, #fff);
}

.skel-header__brand {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.skel-header__mark {
  display: block;
  width: 2.15rem;
  height: 2.15rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.skel-header__wordmark {
  display: block;
  width: 5.75rem;
  height: 0.85rem;
  border-radius: 999px;
}

.skel-header__nav {
  display: none;
  flex: 1 1 auto;
  height: 0.7rem;
  max-width: 20rem;
  margin-inline: auto;
  border-radius: 999px;
}

.skel-header__menu {
  display: block;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
}

.skel-hero {
  position: relative;
  z-index: 1;
  flex: 0 0 auto;
  height: min(52svh, 28rem);
  margin: 0;
  overflow: hidden;
  background: color-mix(in srgb, var(--color-paper, #e5e1dc) 55%, #3a3436 45%);
}

.skel-hero__media {
  position: absolute;
  inset: 0;
}

.skel-hero__copy {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  padding: 4.25rem 1.25rem 3.25rem;
}

.skel-hero__dots {
  position: absolute;
  left: 50%;
  bottom: calc(var(--mobile-book-bar-height, 4.15rem) + 1.1rem);
  z-index: 2;
  display: flex;
  gap: 0.4rem;
  transform: translateX(-50%);
}

.skel-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
}

.skel-bar {
  display: block;
  border-radius: 999px;
}

.skel-bar--eyebrow {
  width: min(38%, 8rem);
  height: 0.45rem;
}

.skel-bar--title {
  width: min(62%, 13.5rem);
  height: 1.55rem;
}

.skel-bar--price {
  width: min(48%, 10.5rem);
  height: 0.5rem;
}

.skel-bar--cta {
  width: min(52%, 10rem);
  height: 2.45rem;
  margin-top: 0.35rem;
  border-radius: 2px;
}

.skel-bar--section {
  width: 5.5rem;
  height: 0.7rem;
  margin: 0 auto 0.85rem;
}

.skel-bar--line {
  width: 100%;
  height: 0.45rem;
  margin-bottom: 0.45rem;
}

.skel-bar--line-short {
  width: 68%;
}

.skel-band {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  padding: 1rem 1.1rem 0.35rem;
  background: var(--color-paper, #e5e1dc);
}

.skel-band__head {
  display: flex;
  justify-content: center;
}

.skel-band--welcome {
  padding-top: 1.15rem;
}

.skel-welcome {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 0.75rem;
  align-items: center;
}

.skel-welcome__media {
  display: block;
  height: 5.5rem;
  border-radius: 4px;
}

.skel-welcome__copy {
  min-width: 0;
}

.skel-welcome__copy .skel-bar--section {
  margin: 0 0 0.65rem;
}

.skel-band__tiles {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.45rem;
}

.skel-tile {
  display: block;
  aspect-ratio: 3 / 4;
  border-radius: 4px;
}

.skel-band--offer {
  padding: 1.15rem 1.1rem 0.85rem;
  background: color-mix(in srgb, var(--color-paper, #e5e1dc) 28%, #2a2426 72%);
}

.skel-offer {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.skel-offer__cell {
  display: block;
  height: 3.35rem;
  border-radius: 3px;
}

.skel-band--doors {
  padding-bottom: 1rem;
}

.skel-doors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

.skel-door {
  display: block;
  height: 5.75rem;
  border-radius: 3px;
}

.skel-services-hero {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 1.25rem 0.75rem;
  background: #fff;
}

.skel-bar--services-title {
  width: min(78%, 16rem);
  height: 1.65rem;
}

.skel-services-cats {
  display: flex;
  gap: 0.55rem;
  overflow: hidden;
  padding-bottom: 0.75rem;
}

.skel-cat {
  display: block;
  flex: 0 0 5.5rem;
  height: 6.5rem;
  border-radius: 3px;
}

.skel-services-panel {
  display: block;
  height: 8.5rem;
  border-radius: 3px;
}

.site-boot-skeleton--services {
  background: #fff;
}

.site-boot-skeleton--services .skel-band {
  background: #fff;
}

.site-boot-skeleton__dock {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.65rem 1rem calc(0.65rem + env(safe-area-inset-bottom, 0px));
  background: color-mix(in srgb, var(--color-paper, #e5e1dc) 88%, #fff);
  border-top: 1px solid color-mix(in srgb, var(--color-ink, #2c2c30) 6%, transparent);
}

.skel-dock-cta {
  display: block;
  width: min(100%, 22rem);
  height: 2.85rem;
  border-radius: 2px;
}

/*
 * Instagram-style bones: same hue as paper, barely darker,
 * soft pulse shimmer — no chalk white / charcoal contrast.
 */
.skel-bone {
  background: color-mix(in srgb, var(--color-paper, #e5e1dc) 72%, var(--color-ink, #2c2c30) 28%);
  background-image: linear-gradient(
    100deg,
    transparent 0%,
    color-mix(in srgb, #fff 22%, transparent) 45%,
    transparent 80%
  );
  background-size: 220% 100%;
  background-repeat: no-repeat;
  animation: skel-shimmer 1.85s ease-in-out infinite;
}

.skel-bone--soft {
  background-color: color-mix(in srgb, #fff 22%, transparent);
}

.skel-bone--hero {
  background-color: color-mix(in srgb, var(--color-paper, #e5e1dc) 40%, #2c2628 60%);
  opacity: 0.85;
}

.skel-bone--charcoal {
  background-color: color-mix(in srgb, #3a3436 78%, var(--color-paper, #e5e1dc) 22%);
  background-image: linear-gradient(
    100deg,
    transparent 0%,
    color-mix(in srgb, #fff 12%, transparent) 45%,
    transparent 80%
  );
}

.skel-bone--photo {
  background-color: color-mix(in srgb, #5a4a48 55%, var(--color-paper, #e5e1dc) 45%);
  background-image: linear-gradient(
    100deg,
    transparent 0%,
    color-mix(in srgb, #fff 16%, transparent) 45%,
    transparent 80%
  );
}

.skel-bone--on-dark {
  background-color: color-mix(in srgb, #fff 18%, transparent);
  background-image: linear-gradient(
    100deg,
    transparent 0%,
    color-mix(in srgb, #fff 14%, transparent) 45%,
    transparent 80%
  );
}

@keyframes skel-shimmer {
  0% {
    background-position: 120% 0;
  }
  100% {
    background-position: -80% 0;
  }
}

.loader-fade-leave-active {
  transition:
    opacity 0.34s var(--ease-story, ease),
    visibility 0.34s;
}

.loader-fade-leave-to {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

@media (min-width: 768px) {
  .skel-header__nav--desktop {
    display: block;
  }

  .skel-header__menu {
    width: 6.25rem;
    height: 2.25rem;
    border-radius: 2px;
  }

  .skel-hero {
    height: min(58vh, 32rem);
  }

  .skel-hero__dots {
    bottom: 2rem;
  }

  .skel-bar--cta {
    width: min(26%, 9.75rem);
  }

  .skel-welcome {
    grid-template-columns: 1.15fr 1fr;
    gap: 1.15rem;
  }

  .skel-welcome__media {
    height: 7.25rem;
  }

  .skel-offer {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .skel-offer__cell {
    height: 4rem;
  }

  .skel-door {
    height: 7.25rem;
  }

  .site-boot-skeleton__dock {
    display: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .skel-bone {
    animation: none;
    background-image: none;
  }
}
</style>
