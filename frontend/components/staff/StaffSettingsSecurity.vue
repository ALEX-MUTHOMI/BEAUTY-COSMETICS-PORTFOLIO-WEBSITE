<template>
  <StaffPortalShell title="Settings" :api-base-url="apiBaseUrl">
    <section class="settings-list" aria-label="Account settings">
      <article class="settings-row">
        <div>
          <h2>Appearance</h2>
          <p>Light or dark for your desk.</p>
        </div>
        <StaffThemeToggle />
      </article>

      <article class="settings-row">
        <div>
          <h2>Reset password</h2>
          <p>We’ll email a reset link.</p>
        </div>
        <NuxtLink class="settings-link" to="/staff/forgot-password">Reset password</NuxtLink>
      </article>

      <article class="settings-row settings-row--signout">
        <div>
          <h2>Sign out</h2>
          <p>Leave the desk on this device.</p>
        </div>
        <button type="button" class="settings-btn" :disabled="signingOut" @click="signOut">
          {{ signingOut ? 'Signing out…' : 'Sign out' }}
        </button>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { ensureBookingCsrfToken } from '~/src/booking/bookingCsrf'
import StaffPortalShell from './StaffPortalShell.vue'
import StaffThemeToggle from './StaffThemeToggle.vue'
import { postStaffLogout } from '~/src/staff/staffPortalApi'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
  }>(),
  { apiBaseUrl: '' },
)

const signingOut = ref(false)

async function signOut() {
  if (signingOut.value) return
  signingOut.value = true
  try {
    const csrf = (await ensureBookingCsrfToken(props.apiBaseUrl || '', { forceRefresh: true })) || ''
    if (csrf) await postStaffLogout(props.apiBaseUrl || '', csrf)
  } catch {
    // Still leave the desk.
  } finally {
    if (typeof window !== 'undefined') {
      window.location.assign('/staff/login')
    }
  }
}
</script>

<style scoped>
.settings-list {
  display: grid;
  gap: 0.75rem;
  max-width: 36rem;
}

.settings-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.15rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  border-radius: 0.85rem;
  background: var(--color-paper, #fffcf8);
}

.settings-row h2,
.settings-row p {
  margin: 0;
  font-family: var(--font-body, 'Manrope', sans-serif);
}

.settings-row h2 {
  margin-bottom: 0.35rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: 1.2rem;
  font-weight: 400;
}

.settings-row p {
  color: var(--color-muted, #8a8580);
  font-size: 0.92rem;
}

.settings-link,
.settings-btn {
  min-height: 2.7rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 0.85rem;
  padding: 0 1rem;
  text-decoration: none;
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  flex-shrink: 0;
}

.settings-link {
  color: #fff;
  background: #27272a;
}

.settings-btn {
  color: #fff;
  background: #965f57;
}

.settings-btn:hover:not(:disabled) {
  background: #84534c;
}

.settings-btn:active:not(:disabled) {
  background: #734842;
}

:global(html[data-staff-theme='dark']) .settings-link {
  color: #0b0b0d;
  background: #f4f4f5;
}

:global(html[data-staff-theme='dark']) .settings-btn {
  color: #fff;
  background: #b07a71;
}

.settings-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 560px) {
  .settings-row {
    flex-direction: column;
    align-items: stretch;
  }

  .settings-link,
  .settings-btn {
    width: 100%;
  }
}
</style>
