<template>
  <div
    class="landing-shell"
    :class="{
      'landing-shell--no-book-bar': !showMobileBookBar,
      'landing-shell--home': isHome,
      'landing-shell--resume': Boolean(welcomeBackHref),
    }"
  >
    <SiteHeader />

    <aside
      v-if="welcomeBackHref"
      class="welcome-back welcome-back--overlay"
      role="status"
      aria-label="Continue your last booking"
    >
      <div class="welcome-back__inner">
        <span class="welcome-back__mark" aria-hidden="true" />
        <div class="welcome-back__copy">
          <p class="welcome-back__eyebrow">Welcome back</p>
          <p class="welcome-back__text">Continue your last booking</p>
        </div>
        <NuxtLink :to="welcomeBackHref" class="welcome-back__cta" @click="onWelcomeBack">
          Resume
        </NuxtLink>
      </div>
    </aside>

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
const isHome = computed(() => route.path === '/')

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
  position: relative;
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-paper);
  --home-hero-chrome: 0px;
  --welcome-resume-offset: 0px;
}

.landing-shell--home.landing-shell--resume {
  --welcome-resume-offset: 3.35rem;
}

.landing-shell--home.landing-shell--resume :deep(.hero__content) {
  padding-top: calc(
    max(var(--site-header-height, 3.75rem), env(safe-area-inset-top, 0px)) + var(--welcome-resume-offset)
  );
}

/* Floating resume chip — overlays content, never pushes layout */
.welcome-back--overlay {
  position: fixed;
  z-index: 46;
  top: calc(var(--site-header-height, 4.25rem) + 0.55rem);
  left: 50%;
  transform: translateX(-50%);
  width: min(calc(100% - 1.5rem), 26rem);
  padding: 0;
  background: transparent;
  border: 0;
  pointer-events: none;
}

.welcome-back--overlay .welcome-back__inner {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.55rem 0.55rem 0.55rem 0.75rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(232, 228, 225, 0.95);
  box-shadow:
    0 10px 28px rgba(20, 16, 18, 0.16),
    0 1px 0 rgba(255, 255, 255, 0.85) inset;
  backdrop-filter: blur(14px) saturate(1.1);
  -webkit-backdrop-filter: blur(14px) saturate(1.1);
}

.welcome-back__mark {
  flex: 0 0 auto;
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: var(--color-rose);
  box-shadow: 0 0 0 4px rgba(222, 150, 141, 0.22);
}

.welcome-back__copy {
  flex: 1 1 auto;
  min-width: 0;
}

.welcome-back__eyebrow {
  margin: 0;
  font: 700 0.58rem/1.2 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose-dark, #b56b62);
}

.welcome-back__text {
  margin: 0.08rem 0 0;
  font: 600 0.78rem/1.25 var(--font-body);
  color: var(--color-ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.welcome-back__cta {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.35rem;
  padding: 0.45rem 0.95rem;
  border-radius: 999px;
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
  color: #fff;
  background: var(--color-rose);
  -webkit-tap-highlight-color: transparent;
}

.welcome-back__cta:hover {
  background: var(--color-rose-dark, #b56b62);
}

@media (max-width: 419px) {
  .welcome-back--overlay {
    width: min(calc(100% - 1rem), 26rem);
    top: calc(var(--site-header-height, 3.5rem) + 0.4rem);
  }

  .welcome-back--overlay .welcome-back__inner {
    gap: 0.45rem;
    padding: 0.45rem 0.45rem 0.45rem 0.65rem;
  }

  .welcome-back__text {
    font-size: 0.72rem;
  }

  .welcome-back__cta {
    min-height: 2.2rem;
    padding-inline: 0.8rem;
    font-size: 0.64rem;
  }
}

@media (min-width: 768px) {
  .welcome-back--overlay {
    width: min(calc(100% - 2rem), 28rem);
    top: calc(var(--site-header-height, 5rem) + 0.75rem);
  }

  .welcome-back__text {
    font-size: 0.84rem;
  }

  .welcome-back__cta {
    min-height: 2.5rem;
    padding-inline: 1.1rem;
  }
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
