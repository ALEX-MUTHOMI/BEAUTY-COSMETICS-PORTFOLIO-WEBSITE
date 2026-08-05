<template>
  <NuxtLayout name="landing">
    <main class="site-error">
      <img
        :src="flowerSrc"
        alt=""
        class="site-error__bloom site-error__bloom--tl"
        data-testid="mellis-flower"
        aria-hidden="true"
        width="120"
        height="120"
        decoding="async"
      />
      <img
        :src="flowerSrc"
        alt=""
        class="site-error__bloom site-error__bloom--br"
        data-testid="mellis-flower"
        aria-hidden="true"
        width="140"
        height="140"
        decoding="async"
      />
      <div class="site-error__inner">
        <p class="site-error__script" aria-hidden="true">{{ NOT_FOUND_PAGE.script }}</p>
        <p class="site-error__eyebrow">{{ isNotFound ? NOT_FOUND_PAGE.eyebrow : 'Error' }}</p>
        <h1 class="site-error__title">
          {{ isNotFound ? NOT_FOUND_PAGE.title : 'Something went wrong' }}
        </h1>
        <p class="site-error__lead">
          {{ isNotFound ? NOT_FOUND_PAGE.lead : errorLead }}
        </p>
        <div class="site-error__actions">
          <SiteButton to="/" variant="outline" @click="clearError">Home</SiteButton>
          <SiteButton to="/services" variant="outline" @click="clearError">Services</SiteButton>
          <SiteButton to="/book" variant="primary" @click="clearError">Book now</SiteButton>
        </div>
        <NuxtLink to="/faq" class="site-error__faq" @click="clearError">{{ NOT_FOUND_PAGE.faqLink }}</NuxtLink>
      </div>
    </main>
  </NuxtLayout>
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'

import { MELLIS_FLOWER_SRC, NOT_FOUND_PAGE } from '@/landing/clientPagesContent'

const props = defineProps<{ error: NuxtError }>()

const isNotFound = computed(() => props.error?.statusCode === 404)
const flowerSrc = MELLIS_FLOWER_SRC
const errorLead = 'Please try again soon. If it keeps happening, message us from the header.'

useHead({
  title: computed(() =>
    isNotFound.value ? 'Page not found | Shee Aesthetics' : 'Error | Shee Aesthetics',
  ),
})
</script>

<style scoped>
.site-error {
  position: relative;
  isolation: isolate;
  min-height: min(72vh, 40rem);
  display: grid;
  place-items: center;
  padding: clamp(3rem, 10vh, 6rem) 1.25rem;
  background:
    radial-gradient(ellipse 70% 55% at 50% 0%, rgba(176, 122, 113, 0.1), transparent 60%),
    linear-gradient(180deg, var(--color-paper) 0%, var(--color-parchment) 100%);
  overflow: hidden;
}

.site-error__bloom {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  opacity: 0.22;
  filter: saturate(1.3) brightness(1.02);
}

.site-error__bloom--tl {
  top: 1rem;
  left: max(0.5rem, env(safe-area-inset-left));
  width: min(120px, 24vw);
  transform: rotate(-22deg);
}

.site-error__bloom--br {
  right: max(0.5rem, env(safe-area-inset-right));
  bottom: 1.5rem;
  width: min(140px, 28vw);
  transform: rotate(150deg);
}

.site-error__inner {
  position: relative;
  z-index: 1;
  width: min(32rem, 100%);
  text-align: center;
}

.site-error__script {
  margin: 0 0 0.35rem;
  font-family: var(--font-script);
  font-size: clamp(2.4rem, 8vw, 3.4rem);
  line-height: 1;
  color: var(--color-rose);
  opacity: 0.85;
}

.site-error__eyebrow {
  margin: 0 0 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.28em;
  font: 600 0.72rem/1 var(--font-body);
  color: var(--color-muted);
}

.site-error__title {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(2rem, 5vw, 2.75rem);
  letter-spacing: -0.02em;
  color: var(--color-ink);
}

.site-error__lead {
  margin: 0 auto 2rem;
  max-width: 36ch;
  font: 400 1rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.site-error__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
}

.site-error__faq {
  display: inline-block;
  margin-top: 1.75rem;
  font: 600 0.78rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose);
}

.site-error__faq:hover {
  color: var(--color-rose-dark);
}
</style>
