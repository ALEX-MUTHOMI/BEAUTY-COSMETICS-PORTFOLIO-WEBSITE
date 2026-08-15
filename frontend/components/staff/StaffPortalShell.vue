<template>
  <div class="staff-shell">
    <aside class="staff-shell__sidebar" aria-label="Staff portal navigation">
      <div class="staff-shell__brand-block">
        <StaffSheeBrand to="/staff/dashboard" size="sm" />
        <p class="staff-shell__eyebrow">Staff desk</p>
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
      <button type="button" class="staff-shell__signout" @click="signOut">Sign out</button>
    </aside>

    <header class="staff-shell__topbar">
      <div class="staff-shell__topbar-brand">
        <StaffSheeBrand to="/staff/dashboard" size="sm" class="staff-shell__mobile-brand" />
        <div class="staff-shell__title-block">
          <p class="staff-shell__eyebrow staff-shell__eyebrow--desktop">Staff desk</p>
          <h1>{{ title }}</h1>
        </div>
      </div>
      <div class="staff-shell__actions">
        <StaffThemeToggle variant="icon" />
        <slot name="actions" />
      </div>
    </header>

    <main class="staff-shell__main" tabindex="-1">
      <slot />
    </main>

    <nav class="staff-shell__bottom" aria-label="Primary staff navigation">
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

import { ensureBookingCsrfToken } from '~/src/booking/bookingCsrf'
import StaffSheeBrand from './StaffSheeBrand.vue'
import StaffThemeToggle from './StaffThemeToggle.vue'
import { canSeePaymentsDesk, getStaffMe, postStaffLogout } from '~/src/staff/staffPortalApi'
import { applyStaffTheme, resolveStaffTheme } from '~/src/staff/theme'

const props = withDefaults(
  defineProps<{
    title: string
    apiBaseUrl?: string
  }>(),
  {
    apiBaseUrl: '',
  },
)

const allNavItems = [
  { label: 'Home', short: 'Home', path: '/staff/dashboard', icon: '01' },
  { label: 'Bookings', short: 'Bookings', path: '/staff/bookings', icon: '02' },
  { label: 'Reschedules', short: 'Moves', path: '/staff/reschedules', icon: '03' },
  { label: 'Payments', short: 'Pay', path: '/staff/payments', icon: '04' },
  { label: 'Gallery', short: 'Gallery', path: '/staff/gallery', icon: '05' },
  { label: 'Settings', short: 'Settings', path: '/staff/settings', icon: '06' },
]

const permissions = ref<string[] | null>(null)
const signingOut = ref(false)

const visibleNavItems = computed(() =>
  allNavItems.filter((item) => {
    if (item.path !== '/staff/payments') return true
    return canSeePaymentsDesk(permissions.value)
  }),
)

/** Uncluttered mobile tabs — Moves/Payments open from Bookings. */
const mobileNavPaths = ['/staff/dashboard', '/staff/bookings', '/staff/gallery', '/staff/settings']
const mobileNavItems = computed(() =>
  allNavItems
    .filter((item) => mobileNavPaths.includes(item.path))
    .map((item, index) => ({
      ...item,
      icon: String(index + 1).padStart(2, '0'),
    })),
)

onMounted(async () => {
  applyStaffTheme(resolveStaffTheme())
  const me = await getStaffMe(props.apiBaseUrl)
  if (me.ok && me.data) {
    permissions.value = me.data.permissions
  }
})

async function signOut() {
  if (signingOut.value) return
  signingOut.value = true
  try {
    const csrf = (await ensureBookingCsrfToken(props.apiBaseUrl || '', { forceRefresh: true })) || ''
    if (csrf) {
      await postStaffLogout(props.apiBaseUrl || '', csrf)
    }
  } catch {
    // Always leave the desk UI even if logout network fails.
  } finally {
    if (typeof window !== 'undefined') {
      window.location.assign('/staff/login')
    }
  }
}
</script>

<style scoped>
.staff-shell {
  --staff-text: var(--color-ink, #27272a);
  --staff-muted: var(--color-muted, #8a8580);
  --staff-surface: var(--color-paper, #fffcf8);
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
  --staff-radius: 0.85rem;
  --staff-bottom-nav: 4.75rem;
  --staff-sidebar: 17rem;
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-columns: var(--staff-sidebar) minmax(0, 1fr);
  grid-template-rows: auto 1fr;
  color: var(--staff-text);
  font-family: var(--staff-body);
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--staff-primary) 12%, transparent), transparent 30rem),
    linear-gradient(140deg, var(--staff-cream) 0%, var(--staff-surface) 52%, var(--staff-parchment) 100%);
}

:global(html[data-staff-theme='dark']) .staff-shell {
  --staff-text: var(--color-ink);
  --staff-muted: var(--color-muted);
  --staff-surface: var(--color-paper);
  --staff-border: var(--color-line);
  --staff-primary: var(--color-rose);
  --staff-primary-strong: var(--color-rose-dark);
  --staff-inverse: #0b0b0d;
  --staff-cream: var(--color-cream);
  --staff-stone: var(--color-stone);
  --staff-parchment: var(--color-parchment);
  --staff-blush: var(--color-rose-soft);
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--color-rose) 12%, transparent), transparent 28rem),
    linear-gradient(145deg, var(--color-cream) 0%, var(--color-paper) 52%, var(--color-parchment) 100%);
}

.staff-shell__sidebar {
  grid-row: 1 / span 2;
  display: flex;
  flex-direction: column;
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
  flex: 1;
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

.staff-shell__nav-link:hover,
.staff-shell__nav-link:focus-visible {
  outline: 0;
  background: var(--staff-blush);
}

.staff-shell__nav-link.router-link-active {
  background: color-mix(in srgb, var(--staff-blush) 70%, transparent);
  border-left-color: var(--staff-primary);
  font-weight: 600;
}

.staff-shell__nav-link.router-link-active .staff-shell__nav-index {
  color: var(--staff-primary-strong);
}

.staff-shell__signout {
  margin-top: 1rem;
  min-height: 2.75rem;
  border: 1px solid var(--staff-border);
  border-radius: var(--staff-radius);
  background: transparent;
  color: var(--staff-text);
  font: 600 0.85rem/1 var(--staff-body);
  cursor: pointer;
}

.staff-shell__signout:hover,
.staff-shell__signout:focus-visible {
  border-color: var(--staff-primary);
  outline: 0;
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
  gap: 0.85rem;
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

.staff-shell h1 {
  margin: 0.15rem 0 0;
  font-family: var(--staff-display);
  font-size: clamp(1.35rem, 3.2vw, 2.35rem);
  font-weight: 400;
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.staff-shell__main {
  padding: 0 clamp(1rem, 3vw, 2.5rem) calc(var(--staff-bottom-nav) + 1.5rem);
  max-width: 100%;
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

  .staff-shell__eyebrow--desktop {
    display: none;
  }
}

@media (min-width: 1100px) {
  .staff-shell {
    --staff-sidebar: 18.5rem;
  }

  .staff-shell__main {
    padding-inline: clamp(1.5rem, 4vw, 3rem);
  }
}

@media (max-width: 860px) {
  .staff-shell {
    grid-template-columns: 1fr;
    --staff-bottom-nav: calc(4.25rem + env(safe-area-inset-bottom, 0px));
  }

  .staff-shell__sidebar {
    display: none;
  }

  .staff-shell__mobile-brand {
    display: inline-flex;
  }

  .staff-shell__eyebrow--desktop {
    display: none;
  }

  .staff-shell__topbar {
    border-bottom-color: var(--staff-border);
    padding-top: max(0.75rem, env(safe-area-inset-top, 0px));
  }

  .staff-shell__title-block {
    display: none;
  }

  .staff-shell__actions {
    margin-left: auto;
  }

  .staff-shell__actions :deep(.action-link) {
    display: none;
  }

  .staff-shell__bottom {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 20;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    padding: 0.35rem 0.35rem calc(0.35rem + env(safe-area-inset-bottom, 0px));
    border-top: 1px solid var(--staff-border);
    background: color-mix(in srgb, var(--staff-cream) 94%, transparent);
    backdrop-filter: blur(18px);
  }

  .staff-shell__bottom-link {
    min-height: 44px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 0.2rem;
    margin: 0 0.1rem;
    padding: 0.35rem 0.15rem;
    border-radius: 0.65rem;
    color: var(--staff-muted);
    text-decoration: none;
    font: 500 0.66rem/1.1 var(--staff-body);
    transition:
      color 0.18s var(--staff-ease),
      background 0.18s var(--staff-ease);
  }

  .staff-shell__bottom-link:hover,
  .staff-shell__bottom-link:focus-visible {
    outline: 0;
    color: var(--staff-text);
    background: color-mix(in srgb, var(--staff-blush) 55%, transparent);
  }

  .staff-shell__bottom-index {
    font: 600 0.58rem/1 var(--staff-body);
    letter-spacing: 0.1em;
  }

  .staff-shell__bottom-label {
    font-size: 0.7rem;
    font-weight: 600;
  }

  .staff-shell__bottom-link.router-link-active,
  .staff-shell__bottom-link.router-link-active .staff-shell__bottom-label,
  .staff-shell__bottom-link.router-link-active .staff-shell__bottom-index {
    color: var(--staff-primary-strong);
  }

  .staff-shell__bottom-link.router-link-active {
    background: color-mix(in srgb, var(--staff-blush) 85%, transparent);
    font-weight: 600;
  }
}
</style>
