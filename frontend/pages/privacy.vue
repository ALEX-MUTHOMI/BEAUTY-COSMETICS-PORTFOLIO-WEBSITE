<template>
  <main class="legal-page">
    <div class="legal-page__inner">
      <p class="label">Legal</p>
      <h1>Privacy Policy</h1>
      <p>
        Shee Aesthetics collects the information you provide when booking online: your name, email, and
        phone number. We use this only to perform your booking contract — manage the visit, initiate
        M-Pesa payment, send confirmation, and deliver your PDF receipt. This is not marketing.
      </p>
      <p>
        You do not need a customer account or password to book. We do not sell your personal data.
        Optional “remember this device” stores only an opaque HttpOnly cookie — never your email or
        phone in browser storage. Staff accounts are separate and never share your remembered-device
        cookie.
      </p>
      <p>
        We process data under Kenya’s Data Protection Act, 2019 and apply GDPR-grade safeguards where
        practical. Payment runs through M-Pesa; email providers deliver receipts and security messages.
      </p>

      <h2>What we collect</h2>
      <ul v-if="dataMapEntries.length" class="legal-page__map">
        <li v-for="[field, meta] in dataMapEntries" :key="field">
          <strong>{{ field }}</strong> — {{ meta.purpose }} ({{ meta.lawfulBasis }}; {{ meta.retention }})
        </li>
      </ul>
      <p v-else>
        Name, email, and phone for the appointment and M-Pesa STK; technical logs without cleartext contact
        data. Retention is typically 24 months after your last completed booking, then soft-delete.
      </p>

      <h2>Your rights</h2>
      <p>
        You may request access, correction, erasure, or objection. Submit the form below — you will receive
        a ticket id only (we do not echo your details back). Staff fulfil requests; some financial records
        may be retained for legal or accounting reasons.
      </p>

      <form class="privacy-form" @submit.prevent="onSubmit">
        <label>
          Request type
          <select v-model="form.requestType" required>
            <option value="access">Access</option>
            <option value="rectification">Correction</option>
            <option value="erasure">Erasure</option>
            <option value="objection">Objection</option>
          </select>
        </label>
        <label>
          Email
          <input v-model="form.email" type="email" autocomplete="email" required maxlength="120" />
        </label>
        <label>
          Phone (optional, Kenya)
          <input v-model="form.phone" type="tel" autocomplete="tel" maxlength="16" placeholder="07… or +2547…" />
        </label>
        <label>
          Details (optional)
          <textarea v-model="form.details" rows="3" maxlength="500" />
        </label>
        <p v-if="error" class="privacy-form__error" role="alert">{{ error }}</p>
        <p v-if="ticketId" class="privacy-form__ok" role="status">
          Request accepted. Ticket: <code>{{ ticketId }}</code>
        </p>
        <SiteButton type="submit" variant="primary" :disabled="submitting">
          {{ submitting ? 'Sending…' : 'Submit privacy request' }}
        </SiteButton>
      </form>

      <p>
        Questions:
        <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
      </p>
      <NuxtLink to="/" class="legal-page__back">Back to home</NuxtLink>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import {
  fetchPrivacyDataMap,
  submitPrivacyRightsRequest,
  type PrivacyDataMapField,
  type PrivacyRequestType,
} from '@/booking/privacyRightsApi'

definePageMeta({ layout: 'landing' })

useHead({ title: 'Privacy Policy | Shee Aesthetics' })

const config = useRuntimeConfig()
const apiBaseUrl = String(config.public.apiBaseUrl || '')

const dataMap = ref<Record<string, PrivacyDataMapField>>({})
const dataMapEntries = computed(() => Object.entries(dataMap.value))

const form = reactive({
  requestType: 'access' as PrivacyRequestType,
  email: '',
  phone: '',
  details: '',
})
const submitting = ref(false)
const error = ref('')
const ticketId = ref('')

onMounted(async () => {
  const result = await fetchPrivacyDataMap(apiBaseUrl)
  if ('data' in result) dataMap.value = result.data
})

async function onSubmit() {
  error.value = ''
  ticketId.value = ''
  submitting.value = true
  try {
    const result = await submitPrivacyRightsRequest(apiBaseUrl, {
      requestType: form.requestType,
      email: form.email,
      phone: form.phone,
      details: form.details,
    })
    if ('error' in result) {
      error.value = result.throttled
        ? 'Please wait a moment and try again.'
        : 'Privacy request could not be accepted. Check your email and try again.'
      return
    }
    ticketId.value = result.data.ticketId
    form.details = ''
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.legal-page .label {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.legal-page {
  padding: clamp(3rem, 8vh, 5rem) 1.5rem 4rem;
}

.legal-page__inner {
  width: min(40rem, 100%);
  margin: 0 auto;
}

.legal-page h1,
.legal-page h2 {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-weight: 400;
}

.legal-page h1 {
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  margin-bottom: 1.25rem;
}

.legal-page h2 {
  margin-top: 2rem;
  font-size: 1.35rem;
}

.legal-page p,
.legal-page li {
  margin: 0 0 1rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.legal-page a {
  color: var(--color-rose);
}

.legal-page__map {
  padding-left: 1.1rem;
}

.privacy-form {
  display: grid;
  gap: 0.85rem;
  margin: 1.25rem 0 1.75rem;
}

.privacy-form label {
  display: grid;
  gap: 0.35rem;
  font: 600 0.85rem/1.4 var(--font-body);
  color: var(--color-ink, #1a1a1a);
}

.privacy-form input,
.privacy-form select,
.privacy-form textarea {
  font: 400 1rem/1.4 var(--font-body);
  padding: 0.55rem 0.65rem;
  border: 1px solid color-mix(in srgb, var(--color-rose) 35%, transparent);
  border-radius: 0.35rem;
  background: var(--color-parchment, #ddd8d3);
  color: var(--color-ink);
}

.privacy-form__error {
  color: #8b1e2d;
}

.privacy-form__ok {
  color: var(--color-ink, #1a1a1a);
}

.privacy-form__ok code {
  font-size: 0.9em;
}

.legal-page__back {
  display: inline-block;
  margin-top: 0.5rem;
  font: 600 0.95rem var(--font-body);
}
</style>
