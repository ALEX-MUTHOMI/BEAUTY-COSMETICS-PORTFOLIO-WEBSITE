<template>
  <main class="staff-auth-page">
    <header class="staff-auth-page__header">
      <StaffSheeBrand to="/staff/login" size="sm" />
      <StaffThemeToggle variant="icon" />
    </header>

    <section class="staff-auth-page__card">
      <p class="eyebrow">Staff desk</p>
      <h1>Forgot password</h1>
      <p class="lead">Enter your work email. We’ll send a reset link if the account exists.</p>

      <form v-if="!sent" @submit.prevent="submit">
        <label>
          Email
          <input
            v-model.trim="email"
            autocomplete="username"
            type="email"
            inputmode="email"
            required
            :disabled="submitting"
          />
        </label>
        <p v-if="message" class="status" role="status" aria-live="polite">{{ message }}</p>
        <button type="submit" :disabled="submitting || !email">
          {{ submitting ? 'Sending…' : 'Send reset link' }}
        </button>
      </form>

      <div v-else class="sent" role="status">
        <h2>Check your email</h2>
        <p>{{ message }}</p>
        <NuxtLink class="continue" to="/staff/reset-password">I have a reset code</NuxtLink>
      </div>

      <NuxtLink class="back" to="/staff/login">Back to sign in</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import StaffSheeBrand from '../../src/staff/StaffSheeBrand.vue'
import StaffThemeToggle from '../../src/staff/StaffThemeToggle.vue'
import { ensureBookingCsrfToken } from '../../src/booking/bookingCsrf'
import { requestStaffPasswordReset } from '../../src/staff/staffAuth'
import { applyStaffTheme, resolveStaffTheme } from '../../src/staff/theme'

definePageMeta({ layout: false })
useHead({
  title: 'Forgot Password | Shee Aesthetics',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

const email = ref('')
const submitting = ref(false)
const message = ref('')
const sent = ref(false)

onMounted(() => {
  applyStaffTheme(resolveStaffTheme())
})

async function submit() {
  if (submitting.value || !email.value) return
  submitting.value = true
  message.value = ''
  try {
    const csrfToken = (await ensureBookingCsrfToken(apiBaseUrl, { forceRefresh: true })) || ''
    if (!csrfToken) {
      message.value = 'We could not start the reset. Please try again.'
      return
    }
    const result = await requestStaffPasswordReset(apiBaseUrl, email.value, csrfToken)
    // Always show the same outcome (no account enumeration).
    message.value = result.message || 'If the account exists, reset instructions have been sent.'
    sent.value = true
  } catch {
    message.value = 'If the account exists, reset instructions have been sent.'
    sent.value = true
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
.status,
.sent p {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.95rem;
  line-height: 1.45;
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
button,
.continue {
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

button,
.continue {
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
  text-decoration: none;
  cursor: pointer;
}

button:hover:not(:disabled),
.continue:hover {
  background: #84534c;
}

button:active:not(:disabled),
.continue:active {
  background: #734842;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.sent {
  display: grid;
  gap: 0.75rem;
}

.sent h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 400;
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
