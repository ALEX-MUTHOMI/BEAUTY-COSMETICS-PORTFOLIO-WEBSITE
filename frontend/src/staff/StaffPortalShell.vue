<template>
  <div class="staff-shell">
    <aside class="staff-shell__sidebar" aria-label="Staff portal navigation">
      <div class="staff-shell__brand-block">
        <StaffSheeBrand to="/staff/dashboard" size="sm" />
        <p class="staff-shell__eyebrow">Staff portal</p>
      </div>
      <nav class="staff-shell__side-nav">
        <NuxtLink
          v-for="item in visibleNavItems"
          :key="item.path"
          :to="item.path"
          class="staff-shell__nav-link"
        >
          <span class="staff-shell__nav-index" aria-hidden="true">{{ item.icon }}</span>
          <span class="staff-shell__nav-label">{{ item.label }}</span>
        </NuxtLink>
      </nav>
    </aside>

    <header class="staff-shell__topbar">
      <div class="staff-shell__topbar-brand">
        <StaffSheeBrand to="/staff/dashboard" size="sm" class="staff-shell__mobile-brand" />
        <div class="staff-shell__title-block">
          <p class="staff-shell__eyebrow">Staff portal</p>
          <h1>{{ title }}</h1>
        </div>
      </div>
      <div class="staff-shell__actions">
        <slot name="actions" />
        <NuxtLink
          v-if="showMobilePaymentsLink"
          class="staff-shell__desk-link"
          to="/staff/payments"
        >
          Pay
        </NuxtLink>
        <NuxtLink class="staff-shell__desk-link" to="/staff/settings">Settings</NuxtLink>
      </div>
    </header>

    <main class="staff-shell__main" tabindex="-1">
      <slot />
    </main>

    <nav class="staff-shell__bottom" aria-label="Mobile staff portal navigation">
      <NuxtLink
        v-for="item in mobileNavItems"
        :key="item.path"
        :to="item.path"
        class="staff-shell__bottom-link"
      >
        <span class="staff-shell__bottom-index" aria-hidden="true">{{ item.icon }}</span>
        <span class="staff-shell__bottom-label">{{ item.short }}</span>
      </NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import StaffSheeBrand from './StaffSheeBrand.vue'
import { canSeePaymentsDesk, getStaffMe } from './staffPortalApi'

const props = withDefaults(
  defineProps<{
    title: string
    /** Same-origin relative base when omitted (Nuxt proxy). Avoid useRuntimeConfig in src SFCs. */
    apiBaseUrl?: string
  }>(),
  {
    apiBaseUrl: '',
  },
)

const allNavItems = [
  { label: 'Dashboard', short: 'Home', path: '/staff/dashboard', icon: '01' },
  { label: 'Bookings', short: 'Bookings', path: '/staff/bookings', icon: '02' },
  { label: 'Reschedules', short: 'Moves', path: '/staff/reschedules', icon: '03' },
  { label: 'Payments', short: 'Pay', path: '/staff/payments', icon: '04' },
  { label: 'Gallery', short: 'Gallery', path: '/staff/gallery', icon: '05' },
  { label: 'Settings', short: 'Settings', path: '/staff/settings', icon: '06' },
]

/** null = permissions not loaded / me unreachable — keep current nav (stub-safe). */
const permissions = ref<string[] | null>(null)

const visibleNavItems = computed(() =>
  allNavItems.filter((item) => {
    if (item.path !== '/staff/payments') return true
    return canSeePaymentsDesk(permissions.value)
  }),
)

/** Primary one-thumb workflow on phone; Payments/Settings stay in desktop sidebar. */
const mobileNavPaths = ['/staff/dashboard', '/staff/bookings', '/staff/reschedules', '/staff/gallery']
const mobileNavItems = computed(() =>
  visibleNavItems.value.filter((item) => mobileNavPaths.includes(item.path)),
)

const showMobilePaymentsLink = computed(() =>
  visibleNavItems.value.some((item) => item.path === '/staff/payments'),
)

onMounted(async () => {
  const me = await getStaffMe(props.apiBaseUrl)
  if (me.ok && me.data) {
    permissions.value = me.data.permissions
  }
})
</script>

<style scoped>
.staff-shell {
  --staff-text: var(--color-ink, #27272a);
  --staff-muted: var(--color-muted, #8a8580);
  --staff-surface: color-mix(in srgb, var(--color-paper, #fffcf8) 92%, transparent);
  --staff-border: var(--color-line, rgba(39, 37, 42, 0.1));
  --staff-primary: var(--color-rose, #c98980);
  --staff-primary-strong: var(--color-rose-dark, #b5746c);
  --staff-inverse: #fff;
  --staff-cream: var(--color-cream, #f7f3ee);
  --staff-stone: var(--color-stone, #efeae3);
  --staff-parchment: var(--color-parchment, #f4efe8);
  --staff-blush: var(--color-rose-soft, #f0e8e4);
  --staff-display: var(--font-display, 'Libre Baskerville', Georgia, serif);
  --staff-body: var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  --staff-ease: var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1));
  --staff-bottom-nav: 4.75rem;
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-columns: 17rem minmax(0, 1fr);
  grid-template-rows: auto 1fr;
  color: var(--staff-text);
  font-family: var(--staff-body);
  background:
    radial-gradient(circle at top right, rgba(201, 137, 128, 0.07), transparent 30rem),
    linear-gradient(140deg, var(--staff-cream) 0%, #fff 52%, var(--staff-parchment) 100%);
}

:global(html[data-staff-theme='dark']) .staff-shell {
  --staff-text: #f5f0f2;
  --staff-muted: #b7b0b6;
  --staff-surface: rgba(34, 30, 33, 0.9);
  --staff-border: rgba(245, 240, 242, 0.12);
  --staff-primary: #d4a39b;
  --staff-primary-strong: #c48f86;
  --staff-inverse: #1a1719;
  --staff-cream: #1a1719;
  --staff-blush: rgba(212, 163, 155, 0.16);
  background:
    radial-gradient(circle at top right, rgba(201, 137, 128, 0.08), transparent 30rem),
    linear-gradient(135deg, #141214 0%, #1c181a 48%, #262022 100%);
}

.staff-shell__sidebar {
  grid-row: 1 / span 2;
  padding: 1.5rem 1.15rem;
  border-right: 1px solid var(--staff-border);
  background: var(--staff-surface);
  backdrop-filter: blur(18px);
}

.staff-shell__brand-block {
  display: grid;
  gap: 0.55rem;
  margin-bottom: 1.5rem;
  padding: 0 0.35rem;
}

.staff-shell__eyebrow {
  margin: 0;
  color: var(--staff-muted);
  font: 600 0.68rem/1.2 var(--staff-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.staff-shell__side-nav {
  display: grid;
  gap: 0.3rem;
}

.staff-shell__nav-link {
  min-height: 2.75rem;
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0 0.85rem;
  border-radius: 0;
  color: var(--staff-text);
  text-decoration: none;
  font: 500 0.92rem/1 var(--staff-body);
  border-left: 2px solid transparent;
  transition:
    background 0.2s var(--staff-ease),
    color 0.2s var(--staff-ease),
    border-color 0.2s var(--staff-ease);
}

.staff-shell__nav-index {
  min-width: 1.35rem;
  color: var(--staff-muted);
  font: 600 0.68rem/1 var(--staff-body);
  letter-spacing: 0.08em;
  flex-shrink: 0;
}

.staff-shell__nav-label {
  min-width: 0;
}

.staff-shell__nav-link:hover,
.staff-shell__nav-link:focus-visible {
  outline: 0;
  background: var(--staff-blush);
  color: var(--staff-text);
}

.staff-shell__nav-link.router-link-active {
  background: color-mix(in srgb, var(--staff-blush) 70%, transparent);
  border-left-color: var(--staff-primary);
  color: var(--staff-text);
  font-weight: 600;
}

.staff-shell__nav-link.router-link-active .staff-shell__nav-index {
  color: var(--staff-primary-strong);
}

.staff-shell__topbar {
  position: sticky;
  top: 0;
  z-index: 8;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: clamp(0.85rem, 2.5vw, 1.35rem) clamp(1rem, 3vw, 2rem);
  border-bottom: 1px solid transparent;
  background: color-mix(in srgb, var(--staff-cream) 78%, transparent);
  backdrop-filter: blur(16px);
}

.staff-shell__topbar-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.staff-shell__mobile-brand {
  display: none;
  flex-shrink: 0;
}

.staff-shell__title-block {
  min-width: 0;
}

.staff-shell__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.65rem;
  align-items: center;
  flex-shrink: 0;
}

.staff-shell__desk-link {
  display: none;
  min-height: 2.5rem;
  align-items: center;
  padding: 0 0.65rem;
  color: var(--staff-muted);
  text-decoration: none;
  font: 600 0.72rem/1 var(--staff-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.staff-shell__desk-link:hover,
.staff-shell__desk-link:focus-visible {
  color: var(--staff-text);
  outline: 0;
}

.staff-shell h1 {
  margin: 0.15rem 0 0;
  font-family: var(--staff-display);
  font-size: clamp(1.35rem, 3.2vw, 2.35rem);
  font-weight: 400;
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.staff-shell__main {
  padding: 0 clamp(1rem, 3vw, 2rem) calc(var(--staff-bottom-nav) + 1.5rem);
}

.staff-shell__bottom {
  display: none;
}

@media (min-width: 861px) {
  .staff-shell__main {
    padding-bottom: 2.5rem;
  }

  .staff-shell__topbar {
    background: transparent;
    backdrop-filter: none;
  }
}

@media (max-width: 860px) {
  .staff-shell {
    grid-template-columns: 1fr;
    --staff-bottom-nav: calc(4.5rem + env(safe-area-inset-bottom, 0px));
  }

  .staff-shell__sidebar {
    display: none;
  }

  .staff-shell__mobile-brand {
    display: inline-flex;
  }

  .staff-shell__desk-link {
    display: inline-flex;
  }

  .staff-shell__topbar {
    flex-wrap: wrap;
    align-items: flex-start;
    border-bottom-color: var(--staff-border);
    padding-top: max(0.75rem, env(safe-area-inset-top, 0px));
  }

  .staff-shell__topbar-brand {
    gap: 0.75rem;
    flex: 1 1 auto;
    min-width: min(100%, 12rem);
  }

  .staff-shell__actions {
    flex: 1 1 auto;
    justify-content: flex-start;
  }

  .staff-shell h1 {
    font-size: clamp(1.15rem, 4.5vw, 1.45rem);
  }

  .staff-shell__bottom {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 20;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0;
    padding: 0.35rem 0.5rem calc(0.35rem + env(safe-area-inset-bottom, 0px));
    border-top: 1px solid var(--staff-border);
    border-radius: 0;
    background: color-mix(in srgb, var(--color-paper, #fffcf8) 94%, transparent);
    box-shadow: 0 -8px 28px rgba(39, 37, 42, 0.04);
    backdrop-filter: blur(18px);
  }

  .staff-shell__bottom-link {
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 0.2rem;
    padding: 0.4rem 0.25rem;
    color: var(--staff-muted);
    text-decoration: none;
    font: 500 0.68rem/1.1 var(--staff-body);
    letter-spacing: 0.02em;
    border-radius: 0;
    transition:
      color 0.2s var(--staff-ease),
      background 0.2s var(--staff-ease);
  }

  .staff-shell__bottom-index {
    font: 600 0.62rem/1 var(--staff-body);
    letter-spacing: 0.1em;
    color: color-mix(in srgb, var(--staff-muted) 80%, transparent);
  }

  .staff-shell__bottom-label {
    font-size: 0.72rem;
    font-weight: 600;
  }

  .staff-shell__bottom-link:hover,
  .staff-shell__bottom-link:focus-visible {
    outline: 0;
    color: var(--staff-text);
    background: transparent;
  }

  .staff-shell__bottom-link.router-link-active {
    color: var(--staff-text);
    background: transparent;
  }

  .staff-shell__bottom-link.router-link-active .staff-shell__bottom-index {
    color: var(--staff-primary-strong);
  }

  .staff-shell__bottom-link.router-link-active .staff-shell__bottom-label {
    color: var(--staff-primary-strong);
  }
}

@media (max-width: 480px) {
  .staff-shell__actions {
    width: 100%;
  }

  .staff-shell__actions :deep(a),
  .staff-shell__actions :deep(button) {
    width: 100%;
    justify-content: center;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    padding-inline: 0.75rem;
  }
}
</style>
