<template>
  <div class="staff-shell">
    <aside class="staff-shell__sidebar" aria-label="Staff portal navigation">
      <p class="staff-shell__brand">AestheticOS</p>
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
        <StaffThemeToggle />
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
import StaffThemeToggle from './StaffThemeToggle.vue'

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
  --staff-text: #241611;
  --staff-muted: #8a4f34;
  --staff-surface: rgba(255, 253, 248, 0.82);
  --staff-border: rgba(55, 32, 22, 0.12);
  --staff-primary: #7a3f34;
  --staff-inverse: #fffaf3;
  --staff-focus: #d89c73;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 17rem minmax(0, 1fr);
  grid-template-rows: auto 1fr;
  color: var(--staff-text);
  background:
    radial-gradient(circle at top right, rgba(202, 127, 85, 0.22), transparent 28rem),
    linear-gradient(135deg, #fffaf3 0%, #f7eadc 45%, #f0dac6 100%);
}

:global(html[data-staff-theme='dark']) .staff-shell {
  --staff-text: #f8efe7;
  --staff-muted: #cdb9a9;
  --staff-surface: rgba(40, 29, 25, 0.86);
  --staff-border: rgba(255, 239, 226, 0.13);
  --staff-primary: #d59b86;
  --staff-inverse: #180f0c;
  --staff-focus: #e0b083;
  background:
    radial-gradient(circle at top right, rgba(213, 155, 134, 0.18), transparent 28rem),
    linear-gradient(135deg, #120b09 0%, #211714 48%, #33211c 100%);
}

.staff-shell__sidebar {
  grid-row: 1 / span 2;
  padding: 1.5rem;
  border-right: 1px solid var(--staff-border);
  background: var(--staff-surface);
  backdrop-filter: blur(18px);
}

.staff-shell__brand,
.staff-shell__eyebrow {
  margin: 0 0 1rem;
  color: var(--staff-muted);
  font: 900 0.78rem/1.2 ui-sans-serif, system-ui, sans-serif;
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
  border-radius: 18px;
  color: var(--staff-text);
  text-decoration: none;
  font: 850 0.95rem/1 ui-sans-serif, system-ui, sans-serif;
}

.staff-shell a span {
  min-width: 2rem;
  min-height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
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
  font-size: clamp(1.8rem, 4vw, 3rem);
  line-height: 1;
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
    border-radius: 24px;
    background: var(--staff-surface);
    box-shadow: 0 18px 45px rgba(55, 32, 22, 0.2);
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
