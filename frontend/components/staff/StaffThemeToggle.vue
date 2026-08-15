<template>
  <button
    class="theme-toggle"
    :class="{ 'theme-toggle--icon': variant === 'icon' }"
    type="button"
    :aria-label="label"
    :title="label"
    @click="toggleTheme"
  >
    <template v-if="variant === 'icon'">
      <span class="theme-toggle__glyph" aria-hidden="true">
        <svg v-if="theme === 'dark'" viewBox="0 0 24 24" width="18" height="18">
          <circle cx="12" cy="12" r="4" fill="currentColor" />
          <g stroke="currentColor" stroke-width="1.7" stroke-linecap="round">
            <path d="M12 2.6v2" />
            <path d="M12 19.4v2" />
            <path d="M2.6 12h2" />
            <path d="M19.4 12h2" />
            <path d="M5.2 5.2l1.4 1.4" />
            <path d="M17.4 17.4l1.4 1.4" />
            <path d="M5.2 18.8l1.4-1.4" />
            <path d="M17.4 6.6l1.4-1.4" />
          </g>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="18" height="18">
          <path
            fill="currentColor"
            d="M15.2 3.1a8.8 8.8 0 1 0 5.7 15.6 7.2 7.2 0 0 1-5.7-15.6z"
          />
        </svg>
      </span>
    </template>
    <template v-else>
      <span class="theme-toggle__badge" aria-hidden="true">{{ theme === 'dark' ? 'Dark' : 'Light' }}</span>
      {{ theme === 'dark' ? 'Switch to light' : 'Switch to dark' }}
    </template>
  </button>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { applyStaffTheme, nextStaffTheme, persistStaffTheme, resolveStaffTheme, type StaffTheme } from '~/src/staff/theme'

withDefaults(
  defineProps<{
    variant?: 'full' | 'icon'
  }>(),
  { variant: 'full' },
)

const theme = ref<StaffTheme>('light')
const label = computed(() =>
  theme.value === 'dark' ? 'Switch to light mode' : 'Switch to dark mode',
)

onMounted(() => {
  theme.value = resolveStaffTheme()
  applyStaffTheme(theme.value)
})

function toggleTheme() {
  theme.value = nextStaffTheme(theme.value)
  applyStaffTheme(theme.value)
  persistStaffTheme(theme.value)
}

defineExpose({ theme })
</script>

<style scoped>
.theme-toggle {
  min-height: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border: 1px solid var(--staff-border, var(--desk-line, var(--color-line, rgba(39, 37, 42, 0.14))));
  border-radius: 999px;
  padding: 0 0.95rem;
  color: var(--staff-text, var(--desk-ink, var(--color-ink, #27272a)));
  background: var(--staff-surface, var(--desk-paper, var(--color-paper, #fffcf8)));
  cursor: pointer;
  font: 600 0.82rem/1 var(--font-body, 'Manrope', ui-sans-serif, system-ui, sans-serif);
  touch-action: manipulation;
}

.theme-toggle__badge {
  min-width: 2.7rem;
  min-height: 1.55rem;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  color: #fff;
  background: var(--staff-primary, var(--desk-rose, var(--color-rose, #c98980)));
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.theme-toggle--icon {
  width: 2.75rem;
  min-width: 2.75rem;
  height: 2.75rem;
  padding: 0;
}

.theme-toggle__glyph {
  display: inline-grid;
  place-items: center;
  color: inherit;
}

.theme-toggle:hover {
  border-color: var(--staff-primary, var(--desk-rose, var(--color-rose, #c98980)));
}

.theme-toggle:focus-visible {
  outline: 0;
  box-shadow: 0 0 0 3px rgba(201, 137, 128, 0.28);
}

.theme-toggle:active {
  transform: translateY(1px);
}
</style>
