<template>
  <main class="staff-reset-page">
    <section>
      <StaffSheeBrand to="/staff/login" size="sm" />
      <p class="eyebrow">Staff recovery</p>
      <h1>Reset your staff password</h1>
      <p class="lead">Enter your staff email and we&apos;ll send next steps.</p>
      <form @submit.prevent="submit">
        <label>
          Email
          <input v-model="email" autocomplete="username" type="email" required :disabled="submitting" />
        </label>
        <p v-if="message" role="status" aria-live="polite">{{ message }}</p>
        <button type="submit" :disabled="submitting || !email.trim()">
          {{ submitting ? 'Sending…' : 'Send recovery instructions' }}
        </button>
      </form>
      <NuxtLink to="/staff/login">Back to sign in</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import StaffSheeBrand from '../../src/staff/StaffSheeBrand.vue'
import { ensureBookingCsrfToken } from '../../src/booking/bookingCsrf'
import { requestStaffPasswordReset } from '../../src/staff/staffAuth'

definePageMeta({ layout: false })
useHead({
  title: 'Staff Password Recovery | Shee Aesthetics',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

const email = ref('')
const submitting = ref(false)
const message = ref('')

async function submit() {
  if (submitting.value || !email.value.trim()) return
  submitting.value = true
  message.value = ''
  try {
    const csrfToken = (await ensureBookingCsrfToken(apiBaseUrl)) || ''
    if (!csrfToken) {
      message.value = 'We could not start recovery. Please try again.'
      return
    }
    const result = await requestStaffPasswordReset(apiBaseUrl, email.value, csrfToken)
    message.value = result.message
  } catch {
    message.value = 'If the account exists, reset instructions have been sent.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.staff-reset-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1rem;
  color: var(--color-ink);
  font-family: var(--font-body);
  background:
    radial-gradient(circle at 18% 14%, rgba(222, 150, 141, 0.22), transparent 18rem),
    linear-gradient(165deg, var(--color-cream), #fff 50%, var(--color-rose-soft));
}

.staff-reset-page section {
  width: min(100%, 32rem);
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  border: 1px solid var(--color-line);
  background: color-mix(in srgb, var(--color-paper) 94%, transparent);
  box-shadow: var(--shadow-card);
}

.staff-reset-page .eyebrow {
  margin: 0;
  color: var(--color-rose-dark);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font: 600 0.72rem/1.2 var(--font-body);
}

.staff-reset-page h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.8rem, 5vw, 2.4rem);
  line-height: 1.15;
}

.staff-reset-page .lead,
.staff-reset-page p[role='status'] {
  margin: 0;
  color: var(--color-muted);
}

.staff-reset-page form,
.staff-reset-page label {
  display: grid;
  gap: 0.7rem;
}

.staff-reset-page input,
.staff-reset-page button {
  min-height: 2.8rem;
  border-radius: 0;
}

.staff-reset-page input {
  border: 1px solid var(--color-line);
  padding: 0 1rem;
  background: var(--color-paper);
  color: var(--color-ink);
  font: 1rem var(--font-body);
}

.staff-reset-page button {
  border: 0;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.78rem/1 var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
}

.staff-reset-page button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.staff-reset-page a {
  color: var(--color-muted);
  font: 0.92rem var(--font-body);
}
</style>
