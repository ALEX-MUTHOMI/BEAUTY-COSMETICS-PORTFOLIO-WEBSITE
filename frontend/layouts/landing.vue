<template>
  <div
    class="landing-shell"
    :class="{
      'landing-shell--no-book-bar': !showMobileBookBar,
      'landing-shell--home': isHome,
      'landing-shell--resume': showWelcomeBack,
    }"
  >
    <SiteHeader />

    <Teleport to="body">
      <aside
        v-if="showWelcomeBack"
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
          <button
            type="button"
            class="welcome-back__dismiss"
            aria-label="Dismiss resume booking"
            @click="dismissWelcomeBack"
          >
            <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
              <path
                fill="currentColor"
                d="M18.3 5.71a1 1 0 0 0-1.41 0L12 10.59 7.11 5.7A1 1 0 0 0 5.7 7.11L10.59 12 5.7 16.89a1 1 0 1 0 1.41 1.41L12 13.41l4.89 4.89a1 1 0 0 0 1.41-1.41L13.41 12l4.89-4.89a1 1 0 0 0 0-1.4z"
              />
            </svg>
          </button>
        </div>
      </aside>
    </Teleport>

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
import { computed, onMounted, ref, watch } from 'vue'
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'
import { lastBookHref, SERVICES_BOOK_ENTRY } from '@/landing/bookingHandoff'
import { trackFunnelEvent } from '@/landing/funnelEvents'
import { useLandingBookCta } from '~/composables/useLandingBookCta'

const WELCOME_BACK_DISMISS_KEY = 'shee:welcome-back-dismissed'

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

const welcomeDismissed = ref(false)

const welcomeBackHref = computed(() => {
  if (!import.meta.client) return ''
  if (route.path.startsWith('/book') || route.path.startsWith('/booking')) return ''
  const last = lastBookHref()
  return last && last !== SERVICES_BOOK_ENTRY ? last : ''
})

const showWelcomeBack = computed(
  () => Boolean(welcomeBackHref.value) && !welcomeDismissed.value,
)

function readWelcomeDismissed() {
  if (!import.meta.client) return false
  try {
    return sessionStorage.getItem(WELCOME_BACK_DISMISS_KEY) === '1'
  } catch {
    return false
  }
}

function dismissWelcomeBack() {
  welcomeDismissed.value = true
  try {
    sessionStorage.setItem(WELCOME_BACK_DISMISS_KEY, '1')
  } catch {
    /* ignore */
  }
  syncWelcomeBarOffset()
  trackFunnelEvent('welcome_back_dismiss', { surface: 'welcome_back' })
}

onMounted(() => {
  welcomeDismissed.value = readWelcomeDismissed()
  syncWelcomeBarOffset()
})

watch(showWelcomeBack, () => {
  syncWelcomeBarOffset()
})

watch(welcomeBackHref, (href) => {
  if (!href) welcomeDismissed.value = readWelcomeDismissed()
})

function syncWelcomeBarOffset() {
  if (!import.meta.client) return
  const offset = showWelcomeBack.value
    ? 'calc(3.15rem + env(safe-area-inset-top, 0px))'
    : '0px'
  document.documentElement.style.setProperty('--welcome-bar-offset', offset)
  document.documentElement.classList.toggle('has-welcome-back', showWelcomeBack.value)
}

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
  --welcome-resume-offset: 3.15rem;
}

.landing-shell--home.landing-shell--resume :deep(.hero__content) {
  padding-top: calc(
    max(var(--site-header-height, 3.75rem), env(safe-area-inset-top, 0px)) + var(--welcome-resume-offset)
  );
}

/* Fixed top strip — never scrolls; sits above header */
.welcome-back--overlay {
  position: fixed;
  z-index: 55;
  top: 0;
  left: 0;
  right: 0;
  transform: none;
  width: 100%;
  margin: 0;
  padding: env(safe-area-inset-top, 0px) 0 0;
  background:
    radial-gradient(ellipse 80% 120% at 0% 50%, rgba(222, 150, 141, 0.22), transparent 55%),
    linear-gradient(165deg, #322a2b 0%, #262122 55%, #1e1a1b 100%);
  border: 0;
  border-bottom: 1px solid rgba(222, 150, 141, 0.35);
  box-shadow: 0 10px 28px rgba(20, 16, 18, 0.28);
  pointer-events: none;
}

.welcome-back--overlay .welcome-back__inner {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  width: min(100% - 1.5rem, 40rem);
  margin: 0 auto;
  padding: 0.55rem 0.35rem 0.55rem 0.15rem;
  border-radius: 0;
  background: transparent;
  border: 0;
  box-shadow: none;
}

.welcome-back__mark {
  flex: 0 0 auto;
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: #f0b8ac;
  box-shadow: 0 0 0 4px rgba(222, 150, 141, 0.28);
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
  color: #f0b8ac;
}

.welcome-back__text {
  margin: 0.08rem 0 0;
  font: 600 0.78rem/1.25 var(--font-body);
  color: #fff8f4;
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
  color: #1a1718;
  background: #f0b8ac;
  -webkit-tap-highlight-color: transparent;
}

.welcome-back__cta:hover {
  background: var(--color-rose);
  color: #fff;
}

.welcome-back__dismiss {
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  width: 2.1rem;
  height: 2.1rem;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 50%;
  color: rgba(255, 248, 244, 0.72);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: color 0.15s ease, background 0.15s ease;
}

.welcome-back__dismiss:hover,
.welcome-back__dismiss:focus-visible {
  color: #fff;
  background: rgba(255, 255, 255, 0.16);
  outline: none;
}

.welcome-back__dismiss:focus-visible {
  outline: 2px solid #f0b8ac;
  outline-offset: 2px;
}

@media (max-width: 419px) {
  .welcome-back--overlay .welcome-back__inner {
    width: min(100% - 1rem, 40rem);
    gap: 0.4rem;
    padding: 0.45rem 0.25rem 0.45rem 0.1rem;
  }

  .welcome-back__text {
    font-size: 0.72rem;
  }

  .welcome-back__cta {
    min-height: 2.2rem;
    padding-inline: 0.75rem;
    font-size: 0.64rem;
  }

  .welcome-back__dismiss {
    width: 1.95rem;
    height: 1.95rem;
  }
}

@media (min-width: 768px) {
  .welcome-back--overlay .welcome-back__inner {
    width: min(100% - 2rem, 44rem);
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
