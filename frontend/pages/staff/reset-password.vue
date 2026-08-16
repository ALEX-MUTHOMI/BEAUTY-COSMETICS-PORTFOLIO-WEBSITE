<template>
  <main class="staff-auth-page">
    <header class="staff-auth-page__header">
      <StaffSheeBrand to="/staff/login" size="sm" />
      <StaffThemeToggle variant="icon" />
    </header>

    <section class="staff-auth-page__card">
      <p class="eyebrow">Staff desk</p>
      <h1>Choose a new password</h1>
      <p class="lead">Paste the code from your email. Use at least 15 characters.</p>

      <form @submit.prevent="submit">
        <label>
          Reset code
          <input v-model="token" autocomplete="one-time-code" required :disabled="submitting" />
        </label>
        <label>
          New password
          <input
            v-model="password"
            autocomplete="new-password"
            minlength="15"
            type="password"
            required
            :disabled="submitting"
            @input="onPasswordInput"
          />
        </label>
        <label>
          Confirm password
          <input
            v-model="confirm"
            autocomplete="new-password"
            minlength="15"
            type="password"
            required
            :disabled="submitting"
            @input="onPasswordInput"
          />
        </label>
        <p v-if="hint" class="status status--error" role="status" aria-live="polite">{{ hint }}</p>
        <p v-if="message" class="status" role="status" aria-live="polite">{{ message }}</p>
        <button type="submit" :disabled="submitting || !canSubmit">
          {{ submitting ? 'Updating…' : 'Update password' }}
        </button>
      </form>

      <NuxtLink class="back" to="/staff/login">Back to sign in</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import StaffSheeBrand from '~/components/staff/StaffSheeBrand.vue'
import StaffThemeToggle from '~/components/staff/StaffThemeToggle.vue'
import { ensureBookingCsrfToken } from '~/src/booking/bookingCsrf'
import { confirmStaffPasswordReset } from '~/src/staff/staffAuth'
import { clientStaffPasswordHint, mapStaffPasswordApiMessage } from '~/src/staff/staffUxHelpers'
import { applyStaffTheme, resolveStaffTheme } from '~/src/staff/theme'

definePageMeta({ layout: false })
useHead({
  title: 'Reset Staff Password | Shee Aesthetics',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})

const route = useRoute()
const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

const token = ref('')
const password = ref('')
const confirm = ref('')
const submitting = ref(false)
const message = ref('')
const hint = ref('')

const canSubmit = computed(() => {
  if (!token.value.trim()) return false
  if (clientStaffPasswordHint(password.value, { confirm: confirm.value })) return false
  return password.value.length >= 15 && password.value === confirm.value
})

onMounted(() => {
  applyStaffTheme(resolveStaffTheme())
  const fromQuery = route.query.token
  if (typeof fromQuery === 'string' && fromQuery.trim()) {
    token.value = fromQuery.trim()
  }
})

function onPasswordInput() {
  message.value = ''
  hint.value = clientStaffPasswordHint(password.value, { confirm: confirm.value }) || ''
}

async function submit() {
  const clientHint = clientStaffPasswordHint(password.value, { confirm: confirm.value })
  if (clientHint) {
    hint.value = clientHint
    return
  }
  if (submitting.value || !token.value.trim()) return
  submitting.value = true
  message.value = ''
  hint.value = ''
  try {
    const csrfToken = (await ensureBookingCsrfToken(apiBaseUrl, { forceRefresh: true })) || ''
    if (!csrfToken) {
      message.value = 'We could not update the password. Please try again.'
      return
    }
    const result = await confirmStaffPasswordReset(apiBaseUrl, token.value, password.value, csrfToken)
    if (result.ok) {
      password.value = ''
      confirm.value = ''
      message.value = 'Password updated. Sign in with your new password.'
      await navigateTo('/staff/login')
      return
    }
    message.value = mapStaffPasswordApiMessage(result.message)
  } catch {
    message.value = 'This reset link is invalid or expired.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.staff-auth-page {
  min-height: 100vh;
  min-height: 100dvh;
  display: grid;
  grid-template-rows: auto 1fr;
  padding: 1rem clamp(1rem, 4vw, 2rem) 2rem;
  color: var(--color-ink);
  font-family: var(--font-body);
  background:
    radial-gradient(ellipse 50% 40% at 88% 0%, color-mix(in srgb, var(--color-rose) 14%, transparent), transparent 70%),
    linear-gradient(168deg, var(--color-cream) 0%, var(--color-paper) 48%, var(--color-parchment) 100%);
}

.staff-auth-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.staff-auth-page__card {
  width: min(100%, 26rem);
  margin: 0 auto;
  align-self: start;
  display: grid;
  gap: 0.95rem;
  padding: 1.35rem 1.25rem 1.5rem;
  border: 1px solid var(--color-line);
  border-radius: 1rem;
  background: var(--color-paper);
  box-shadow: var(--shadow-card);
}

.eyebrow {
  margin: 0;
  color: var(--color-rose-dark);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font: 600 0.7rem/1.2 var(--font-body);
}

.staff-auth-page h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.7rem, 5vw, 2.15rem);
  font-weight: 400;
  line-height: 1.15;
}

.lead,
.status {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.95rem;
  line-height: 1.45;
}

.status--error {
  color: #8a3a36;
}

form,
label {
  display: grid;
  gap: 0.55rem;
}

label {
  font: 600 0.78rem/1.2 var(--font-body);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-muted);
}

input,
button {
  min-height: 3rem;
  border-radius: 0.85rem;
}

input {
  border: 1px solid var(--color-line);
  padding: 0 0.95rem;
  background: var(--color-stone);
  color: var(--color-ink);
  font: 1rem var(--font-body);
  text-transform: none;
  letter-spacing: normal;
}

input:focus {
  outline: 0;
  border-color: var(--color-rose);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-rose) 22%, transparent);
  background: var(--color-paper);
}

button {
  border: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  background: var(--color-rose-dark);
  color: #fff;
  font: 600 0.82rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: #84534c;
}

button:active:not(:disabled) {
  background: #734842;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.back {
  color: var(--color-muted);
  font: 0.92rem var(--font-body);
  text-decoration: none;
}

.back:hover {
  color: var(--color-ink);
}

@media (min-width: 720px) {
  .staff-auth-page__card {
    align-self: center;
  }
}
</style>
