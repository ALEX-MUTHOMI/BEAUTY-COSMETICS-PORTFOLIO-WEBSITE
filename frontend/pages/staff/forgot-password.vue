<template>
  <main class="staff-reset-page">
    <section>
      <p>Staff recovery</p>
      <h1>Reset your staff password.</h1>
      <p class="lead">Enter the email for your staff account. We only send instructions when the account exists.</p>
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

import { ensureBookingCsrfToken } from '../../src/booking/bookingCsrf'
import { requestStaffPasswordReset } from '../../src/staff/staffAuth'

definePageMeta({ layout: false })
useHead({
  title: 'Staff Password Recovery | AestheticOS Portal',
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
  background: linear-gradient(135deg, #fffaf3, #e9c6ab);
}

.staff-reset-page section {
  width: min(100%, 32rem);
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 28px;
  background: #fffdf8;
}

.staff-reset-page .lead,
.staff-reset-page p[role='status'] {
  margin: 0;
  color: #6b4a3a;
}

.staff-reset-page form,
.staff-reset-page label {
  display: grid;
  gap: 0.7rem;
}

.staff-reset-page input,
.staff-reset-page button {
  min-height: 2.8rem;
  border-radius: 16px;
}

.staff-reset-page button {
  border: 0;
  background: #241611;
  color: #fffaf3;
  font-weight: 800;
  cursor: pointer;
}

.staff-reset-page button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
