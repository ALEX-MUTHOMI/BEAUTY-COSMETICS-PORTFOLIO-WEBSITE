<template>
  <NuxtLayout name="landing">
    <main class="site-error">
      <div class="site-error__inner">
        <!-- Brand Script -->
        <p class="site-error__script" aria-hidden="true">
          {{ isNotFound ? NOT_FOUND_PAGE.script : SERVER_ERROR_PAGE.script }}
        </p>

        <!-- Eyebrow Tag -->
        <span class="site-error__eyebrow">
          {{ isNotFound ? NOT_FOUND_PAGE.eyebrow : (errorStatusCode || SERVER_ERROR_PAGE.eyebrow) }}
        </span>

        <!-- Headline -->
        <h1 class="site-error__title">
          {{ isNotFound ? NOT_FOUND_PAGE.title : SERVER_ERROR_PAGE.title }}
        </h1>

        <!-- Lead paragraph -->
        <p class="site-error__lead">
          {{ isNotFound ? NOT_FOUND_PAGE.lead : SERVER_ERROR_PAGE.lead }}
        </p>

        <!-- Primary Action Cluster -->
        <div v-if="isNotFound" class="site-error__actions">
          <NuxtLink to="/" class="site-error__btn site-error__btn--outline" @click="handleRedirect('/')">
            Home
          </NuxtLink>
          <NuxtLink to="/services" class="site-error__btn site-error__btn--outline" @click="handleRedirect('/services')">
            Services
          </NuxtLink>
          <NuxtLink to="/book" class="site-error__btn site-error__btn--primary" @click="handleRedirect('/book')">
            Book appointment
          </NuxtLink>
        </div>

        <div v-else class="site-error__actions">
          <button type="button" class="site-error__btn site-error__btn--primary" @click="handleRetry">
            {{ SERVER_ERROR_PAGE.retryButton }}
          </button>
          <a
            :href="whatsappUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="site-error__btn site-error__btn--outline"
          >
            {{ SERVER_ERROR_PAGE.whatsappButton }}
          </a>
          <NuxtLink to="/" class="site-error__btn site-error__btn--outline" @click="handleRedirect('/')">
            Home
          </NuxtLink>
        </div>

        <!-- Secondary Guidance Links -->
        <nav class="site-error__nav" aria-label="Help Navigation">
          <NuxtLink to="/faq" class="site-error__link" @click="handleClearOnly">
            FAQ
          </NuxtLink>
          <span class="site-error__dot" aria-hidden="true">&bull;</span>
          <NuxtLink to="/support" class="site-error__link" @click="handleClearOnly">
            Contact &amp; Support
          </NuxtLink>
        </nav>
      </div>
    </main>
  </NuxtLayout>
</template>

<script setup lang="ts">
import type { NuxtError } from 'nuxt/app'
import { computed } from 'vue'

import {
  CUSTOMER_SUPPORT_PAGE,
  NOT_FOUND_PAGE,
  SERVER_ERROR_PAGE,
} from '~/src/landing/clientPagesContent'

const props = defineProps<{ error: NuxtError }>()

const errorStatusCode = computed(() => props.error?.statusCode)
const isNotFound = computed(() => errorStatusCode.value === 404)

const whatsappUrl = computed(() => {
  const text = encodeURIComponent('Hello Shee, I experienced a connection issue on the Shee Aesthetics website and need assistance.')
  return `https://wa.me/${CUSTOMER_SUPPORT_PAGE.whatsappE164}?text=${text}`
})

function handleRedirect(path: string) {
  clearError({ redirect: path })
}

function handleClearOnly() {
  clearError()
}

function handleRetry() {
  if (typeof window !== 'undefined') {
    clearError()
    window.location.reload()
  }
}
</script>

<style scoped>
.site-error {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(3rem, 7vh, 5rem) 1.25rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
  text-align: center;
}

.site-error__inner {
  max-width: 36rem;
  margin: 0 auto;
}

.site-error__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.4rem, 6vw, 3.2rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.site-error__eyebrow {
  display: inline-block;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 700 0.7rem/1 var(--font-body);
  color: var(--color-rose-dark, #965f57);
}

.site-error__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.site-error__lead {
  margin: 0 auto 1.75rem;
  max-width: 34ch;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.site-error__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 1.75rem;
}

.site-error__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.15rem;
  border-radius: 999px;
  text-decoration: none;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  border: none;
  transition: opacity 0.18s ease;
}

.site-error__btn--primary {
  background: var(--color-rose, #b07a71);
  color: #ffffff;
}

.site-error__btn--outline {
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
}

.site-error__btn:hover {
  opacity: 0.9;
}

.site-error__nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.site-error__link {
  font: 600 0.76rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark, #965f57);
  transition: color 0.18s ease;
}

.site-error__link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.site-error__dot {
  color: var(--color-muted, #6b605c);
  opacity: 0.4;
}
</style>
