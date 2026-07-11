<template>
  <div class="staff-shell">
    <aside class="staff-shell__sidebar" aria-label="Staff portal navigation">
      <div class="staff-shell__brand-block">
        <StaffSheeBrand to="/staff/dashboard" size="sm" />
        <p class="staff-shell__eyebrow">Staff portal</p>
      </div>
      <nav>
        <NuxtLink v-for="item in navItems" :key="item.path" :to="item.path">
          <span aria-hidden="true">{{ item.icon }}</span>
          {{ item.label }}
        </NuxtLink>
      </nav>
    </aside>

    <header class="staff-shell__topbar">
      <div>
        <p class="staff-shell__eyebrow">Staff portal</p>
        <h1>{{ title }}</h1>
      </div>
      <div class="staff-shell__actions">
        <slot name="actions" />
      </div>
    </header>

    <main class="staff-shell__main" tabindex="-1">
      <slot />
    </main>

    <nav class="staff-shell__bottom" aria-label="Mobile staff portal navigation">
      <NuxtLink v-for="item in navItems.slice(0, 4)" :key="item.path" :to="item.path">
        <span aria-hidden="true">{{ item.icon }}</span>
        <span>{{ item.short }}</span>
      </NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import StaffSheeBrand from './StaffSheeBrand.vue'

defineProps<{
  title: string
}>()

const navItems = [
  { label: 'Dashboard', short: 'Home', path: '/staff/dashboard', icon: '01' },
  { label: 'Bookings', short: 'Bookings', path: '/staff/bookings', icon: '02' },
  { label: 'Reschedules', short: 'Moves', path: '/staff/reschedules', icon: '03' },
  { label: 'Payments', short: 'Pay', path: '/staff/payments', icon: 'KES' },
  { label: 'Gallery', short: 'Gallery', path: '/staff/gallery', icon: '04' },
  { label: 'Settings', short: 'Settings', path: '/staff/settings', icon: '05' },
]
</script>

<style scoped>
.staff-shell {
  --staff-text: var(--color-ink, #27272a);
  --staff-muted: var(--color-muted, #89858d);
  --staff-surface: color-mix(in srgb, var(--color-paper, #fff) 88%, transparent);
  --staff-border: var(--color-line, rgba(39, 37, 42, 0.1));
  --staff-primary: var(--color-rose, #de968d);
  --staff-primary-strong: var(--color-rose-dark, #c97f76);
  --staff-inverse: #fff;
  --staff-cream: var(--color-cream, #fcf5f5);
  --staff-display: var(--font-display, 'Libre Baskerville', Georgia, serif);
  --staff-body: var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  min-height: 100vh;
  display: grid;
  grid-template-columns: 17rem minmax(0, 1fr);
  grid-template-rows: auto 1fr;
  color: var(--staff-text);
  font-family: var(--staff-body);
  background:
    radial-gradient(circle at top right, rgba(222, 150, 141, 0.18), transparent 28rem),
    linear-gradient(135deg, var(--staff-cream) 0%, #fff 48%, var(--color-rose-soft, #f5e8e6) 100%);
}

:global(html[data-staff-theme='dark']) .staff-shell {
  --staff-text: #f5f0f2;
  --staff-muted: #b7b0b6;
  --staff-surface: rgba(34, 30, 33, 0.9);
  --staff-border: rgba(245, 240, 242, 0.12);
  --staff-primary: #e4a79f;
  --staff-primary-strong: #d18f86;
  --staff-inverse: #1a1719;
  --staff-cream: #1a1719;
  background:
    radial-gradient(circle at top right, rgba(222, 150, 141, 0.14), transparent 28rem),
    linear-gradient(135deg, #141214 0%, #1c181a 48%, #2a2224 100%);
}

.staff-shell__sidebar {
  grid-row: 1 / span 2;
  padding: 1.5rem;
  border-right: 1px solid var(--staff-border);
  background: var(--staff-surface);
  backdrop-filter: blur(18px);
}

.staff-shell__brand-block {
  display: grid;
  gap: 0.65rem;
  margin-bottom: 1.25rem;
}

.staff-shell__eyebrow {
  margin: 0;
  color: var(--staff-muted);
  font: 600 0.72rem/1.2 var(--staff-body);
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.staff-shell nav {
  display: grid;
  gap: 0.45rem;
}

.staff-shell a {
  min-height: 2.8rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 0.95rem;
  border-radius: 0;
  color: var(--staff-text);
  text-decoration: none;
  font: 600 0.95rem/1 var(--staff-body);
}

.staff-shell a span {
  min-width: 2rem;
  min-height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 0;
  color: var(--staff-inverse);
  background: var(--staff-primary);
  font-size: 0.7rem;
}

.staff-shell a.router-link-active,
.staff-shell a:hover,
.staff-shell a:focus-visible {
  outline: 0;
  background: var(--staff-text);
  color: var(--staff-inverse);
}

.staff-shell__topbar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: clamp(1rem, 3vw, 2rem);
}

.staff-shell__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.75rem;
  align-items: center;
}

.staff-shell h1 {
  margin: 0;
  font-family: var(--staff-display);
  font-size: clamp(1.8rem, 4vw, 2.75rem);
  line-height: 1.1;
}

.staff-shell__main {
  padding: 0 clamp(1rem, 3vw, 2rem) 6rem;
}

.staff-shell__bottom {
  display: none;
}

@media (max-width: 860px) {
  .staff-shell {
    grid-template-columns: 1fr;
  }

  .staff-shell__sidebar {
    display: none;
  }

  .staff-shell__bottom {
    position: fixed;
    inset: auto 1rem 1rem;
    z-index: 10;
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    padding: 0.4rem;
    border: 1px solid var(--staff-border);
    border-radius: 0;
    background: var(--staff-surface);
    box-shadow: var(--shadow-card, 0 0 40px rgba(39, 37, 42, 0.06));
    backdrop-filter: blur(18px);
  }

  .staff-shell__bottom a {
    justify-content: center;
    min-height: 3rem;
    padding: 0.25rem;
    flex-direction: column;
    gap: 0.2rem;
    font-size: 0.75rem;
  }
}
</style>
