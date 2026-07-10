<template>
  <main class="staff-reset-page">
    <section>
      <p>Staff recovery</p>
      <h1>Choose a new staff password.</h1>
      <p class="lead">Use the reset token from your recovery email. Passwords must be at least 15 characters.</p>
      <form @submit.prevent="submit">
        <label>
          Reset token
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
          />
        </label>
        <p v-if="message" role="status" aria-live="polite">{{ message }}</p>
        <button type="submit" :disabled="submitting || !token.trim() || password.length < 15">
          {{ submitting ? 'Resetting…' : 'Reset password' }}
        </button>
      </form>
      <NuxtLink to="/staff/login">Back to sign in</NuxtLink>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { ensureBookingCsrfToken } from '../../src/booking/bookingCsrf'
import { confirmStaffPasswordReset } from '../../src/staff/staffAuth'

definePageMeta({ layout: false })
useHead({
  title: 'Reset Staff Password | AestheticOS Portal',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})

const route = useRoute()
const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

const token = ref('')
const password = ref('')
const submitting = ref(false)
const message = ref('')

onMounted(() => {
  const fromQuery = route.query.token
  if (typeof fromQuery === 'string' && fromQuery.trim()) {
    token.value = fromQuery.trim()
  }
})

async function submit() {
  if (submitting.value || !token.value.trim() || password.value.length < 15) return
  submitting.value = true
  message.value = ''
  try {
    const csrfToken = (await ensureBookingCsrfToken(apiBaseUrl)) || ''
    if (!csrfToken) {
      message.value = 'We could not reset the password. Please try again.'
      return
    }
    const result = await confirmStaffPasswordReset(apiBaseUrl, token.value, password.value, csrfToken)
    message.value = result.message
    if (result.ok) {
      password.value = ''
      await navigateTo('/staff/login')
    }
  } catch {
    message.value = 'Password reset request is invalid or expired.'
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
