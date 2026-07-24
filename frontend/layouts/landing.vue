<template>
  <div class="landing-shell" :class="{ 'landing-shell--no-book-bar': !showMobileBookBar }">
    <SiteHeader />
    <div v-if="welcomeBackHref" class="welcome-back" role="status">
      <p class="welcome-back__text">Welcome back — continue your last booking</p>
      <NuxtLink :to="welcomeBackHref" class="welcome-back__cta" @click="onWelcomeBack">
        Continue
      </NuxtLink>
    </div>
    <slot />
    <SiteFooter />

    <aside
      v-if="showMobileBookBar"
      class="mobile-book-bar"
      aria-label="Quick booking"
    >
      <a
        v-if="contactIsLive"
        class="mobile-book-bar__wa"
        :href="whatsappUrl"
        target="_blank"
        rel="noopener noreferrer"
        :aria-label="whatsappLabel"
        @click="onWaClick"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" width="22" height="22">
          <path
            fill="currentColor"
            d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 1.67c2.2 0 4.26.86 5.82 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.23 8.24-1.44 0-2.84-.37-4.08-1.07l-.29-.17-3.12.82.83-3.04-.19-.31a8.2 8.2 0 0 1-1.26-4.47c0-4.54 3.7-8.24 8.11-8.24z"
          />
        </svg>
      </a>
      <SiteButton
        v-if="bookIsExternal"
        :href="bookHref"
        variant="primary"
        class="mobile-book-bar__cta"
        @click="onBookClick"
      >
        {{ LANDING_PRIMARY_CTA }}
      </SiteButton>
      <SiteButton
        v-else
        :to="bookHref"
        variant="primary"
        class="mobile-book-bar__cta"
        @click="onBookClick"
      >
        {{ LANDING_PRIMARY_CTA }}
      </SiteButton>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'
import { lastBookHref, SERVICES_BOOK_ENTRY } from '@/landing/bookingHandoff'
import { trackFunnelEvent } from '@/landing/funnelEvents'
import { useLandingBookCta } from '@/landing/useLandingBookCta'

const route = useRoute()

const showMobileBookBar = computed(() => {
  const path = route.path || ''
  if (path === '/book' || path.startsWith('/book/')) return false
  if (path.startsWith('/booking/')) return false
  return true
})

const { bookHref, bookIsExternal, contact } = useLandingBookCta()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel

const welcomeBackHref = computed(() => {
  if (!import.meta.client) return ''
  if (route.path.startsWith('/book') || route.path.startsWith('/booking')) return ''
  const last = lastBookHref()
  return last && last !== SERVICES_BOOK_ENTRY ? last : ''
})

function onBookClick() {
  trackFunnelEvent('cta_book_click', { surface: 'mobile_sticky', href: bookHref.value })
}

function onWaClick() {
  trackFunnelEvent('wa_click', { surface: 'mobile_sticky' })
}

function onWelcomeBack() {
  trackFunnelEvent('cta_book_click', { surface: 'welcome_back', href: welcomeBackHref.value })
}

useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
  ],
})
</script>

<style scoped>
.landing-shell {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-paper);
}

.welcome-back {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 0.55rem 1rem;
  background: #f7ece9;
  border-bottom: 1px solid var(--color-line, #e8e4e1);
}

.welcome-back__text {
  margin: 0;
  font: 500 0.88rem/1.35 var(--font-body);
  color: var(--color-ink);
}

.welcome-back__cta {
  font: 700 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-rose-dark, #b56b62);
  text-decoration: underline;
  text-underline-offset: 0.18em;
}

.mobile-book-bar {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 45;
  padding: 0.65rem 1rem calc(0.65rem + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(
    to top,
    rgba(243, 242, 241, 0.98) 70%,
    rgba(243, 242, 241, 0.88)
  );
  border-top: 0;
  box-shadow: 0 -12px 32px rgba(39, 37, 42, 0.06);
  backdrop-filter: blur(12px);
}

.mobile-book-bar__wa {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 2.85rem;
  height: 2.85rem;
  border-radius: 999px;
  background: #128c7e;
  color: #fff;
  text-decoration: none;
}

.mobile-book-bar__cta {
  flex: 1 1 auto;
  width: auto;
}

@media (min-width: 768px) {
  .mobile-book-bar {
    display: none;
  }
}
</style>
