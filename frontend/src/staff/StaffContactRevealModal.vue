<template>
  <div class="modal-backdrop" role="presentation">
    <section class="modal" role="dialog" aria-modal="true" aria-labelledby="contact-reveal-title">
      <h2 id="contact-reveal-title">Confirm it&apos;s you</h2>
      <p>Customer contact details are sensitive. Re-enter your staff password before viewing them.</p>
      <label>
        Staff password
        <input v-model="password" autocomplete="current-password" type="password" />
      </label>
      <p v-if="message" role="status" aria-live="polite">{{ message }}</p>
      <div class="modal__actions">
        <button type="button" @click="$emit('close')">Cancel</button>
        <button type="button" :disabled="loading || !password" @click="submit">
          {{ loading ? 'Checking...' : 'Confirm securely' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { ensureBookingCsrfToken } from '../booking/bookingCsrf'
import { postStaffReauth } from './staffPortalApi'

const props = withDefaults(
  defineProps<{
    /** Injected by Nuxt pages — avoids Nuxt auto-import in Vitest unit mounts. */
    apiBaseUrl?: string
  }>(),
  { apiBaseUrl: '' },
)

const emit = defineEmits<{
  close: []
  confirmed: []
}>()

const password = ref('')
const loading = ref(false)
const message = ref('')

async function submit() {
  if (!password.value || loading.value) return
  loading.value = true
  message.value = ''
  try {
    const apiBaseUrl = String(props.apiBaseUrl || '').trim()
    const csrfToken = await ensureBookingCsrfToken(apiBaseUrl)
    if (!csrfToken) {
      message.value = 'We could not confirm your password. Please try again.'
      return
    }
    const response = await postStaffReauth(apiBaseUrl, password.value, csrfToken)
    if (!response.ok) {
      message.value = 'We could not confirm your password. Please try again.'
      return
    }
    message.value = 'Confirmed. Contact reveal can continue.'
    emit('confirmed')
  } catch {
    message.value = 'We could not confirm your password. Please try again.'
  } finally {
    loading.value = false
    password.value = ''
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(36, 22, 17, 0.48);
}

.modal {
  width: min(100%, 32rem);
  display: grid;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 28px;
  background: #fffaf3;
  box-shadow: 0 30px 90px rgba(36, 22, 17, 0.28);
}

.modal h2,
.modal p {
  margin: 0;
}

.modal label {
  display: grid;
  gap: 0.45rem;
  font-weight: 850;
}

.modal input {
  min-height: 2.8rem;
  border: 1px solid rgba(55, 32, 22, 0.16);
  border-radius: 16px;
  padding: 0 0.8rem;
}

.modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
