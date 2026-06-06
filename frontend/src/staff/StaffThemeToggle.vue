<template>
  <button class="theme-toggle" type="button" :aria-label="label" @click="toggleTheme">
    <span aria-hidden="true">{{ theme === 'dark' ? 'Dark' : 'Light' }}</span>
    {{ theme === 'dark' ? 'Switch to light' : 'Switch to dark' }}
  </button>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { applyStaffTheme, nextStaffTheme, persistStaffTheme, resolveStaffTheme, type StaffTheme } from './theme'

const theme = ref<StaffTheme>('light')
const label = computed(() => (theme.value === 'dark' ? 'Switch staff portal to light mode' : 'Switch staff portal to dark mode'))

onMounted(() => {
  theme.value = resolveStaffTheme()
  applyStaffTheme(theme.value)
})

function toggleTheme() {
  theme.value = nextStaffTheme(theme.value)
  applyStaffTheme(theme.value)
  persistStaffTheme(theme.value)
}
</script>

<style scoped>
.theme-toggle {
  min-height: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border: 1px solid var(--staff-border, rgba(55, 32, 22, 0.14));
  border-radius: 999px;
  padding: 0 0.9rem;
  color: var(--staff-text, #241611);
  background: var(--staff-surface, #fffdf8);
  cursor: pointer;
  font: 900 0.82rem/1 ui-sans-serif, system-ui, sans-serif;
}

.theme-toggle span {
  min-width: 2.7rem;
  min-height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  color: var(--staff-inverse, #fffaf3);
  background: var(--staff-primary, #7a3f34);
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.theme-toggle:focus-visible {
  outline: 3px solid var(--staff-focus, #d89c73);
  outline-offset: 3px;
}
</style>
