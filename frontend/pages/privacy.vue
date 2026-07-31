<template>
  <main class="privacy-page">
    <div class="privacy-page__inner">
      <!-- Header -->
      <header class="privacy-page__header">
        <p class="privacy-page__script" aria-hidden="true">Shee</p>
        <span class="privacy-page__eyebrow">Client Privacy</span>

        <div class="title-lockup">
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--left"
            width="36"
            height="36"
            aria-hidden="true"
          />
          <h1 class="privacy-page__title">Privacy Policy</h1>
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--right"
            width="36"
            height="36"
            aria-hidden="true"
          />
        </div>

        <p class="privacy-page__lead">
          We collect only what is necessary to confirm your booking, process M-Pesa payments, and send your receipt.
        </p>
      </header>

      <!-- Clear Commitments -->
      <section class="privacy-summary" aria-label="Privacy Summary">
        <div class="summary-card">
          <h2 class="summary-card__title">How we treat your data</h2>
          <div class="summary-points">
            <p><strong>Booking details:</strong> We ask for your full name, phone number, and email address strictly to reserve your slot, send the M-Pesa payment prompt, and email your receipt.</p>
            <p><strong>No data sharing:</strong> We do not sell, rent, or share your contact details with advertisers or third parties.</p>
            <p><strong>Guest checkout:</strong> You do not need to create or store a password to book an appointment.</p>
          </div>
        </div>
      </section>

      <!-- Rights Submission Form -->
      <section class="privacy-form-section" aria-label="Data Rights Request">
        <h2 class="privacy-form-section__title">Request or update your records</h2>
        <p class="privacy-form-section__lead">
          Under the Kenya Data Protection Act, you can request a copy of your booking history or ask us to delete your contact details anytime.
        </p>

        <form class="privacy-form" @submit.prevent="onSubmit">
          <div class="form-row">
            <label class="form-field">
              <span class="form-field__label">Request type</span>
              <select v-model="form.requestType" required class="form-field__input">
                <option value="access">Access my booking history</option>
                <option value="rectification">Update my contact details</option>
                <option value="erasure">Delete my contact details</option>
                <option value="objection">Opt out of notifications</option>
              </select>
            </label>

            <label class="form-field">
              <span class="form-field__label">Email address</span>
              <input
                v-model="form.email"
                type="email"
                autocomplete="email"
                required
                maxlength="120"
                placeholder="your.email@example.com"
                class="form-field__input"
              />
            </label>
          </div>

          <div class="form-row">
            <label class="form-field">
              <span class="form-field__label">Phone number (optional)</span>
              <input
                v-model="form.phone"
                type="tel"
                autocomplete="tel"
                maxlength="16"
                placeholder="07XX XXX XXX"
                class="form-field__input"
              />
            </label>
          </div>

          <label class="form-field">
            <span class="form-field__label">Additional notes (optional)</span>
            <textarea
              v-model="form.details"
              rows="3"
              maxlength="500"
              placeholder="Provide any booking dates or details to help us locate your record..."
              class="form-field__input form-field__textarea"
            />
          </label>

          <p v-if="error" class="form-msg form-msg--error" role="alert">{{ error }}</p>
          <p v-if="ticketId" class="form-msg form-msg--ok" role="status">
            Request received. Your reference ticket is: <code>{{ ticketId }}</code>
          </p>

          <div class="form-actions">
            <button type="submit" class="privacy-submit-btn" :disabled="submitting">
              {{ submitting ? 'Sending...' : 'Submit request' }}
            </button>
          </div>
        </form>
      </section>

      <!-- Footer Help & Links -->
      <footer class="privacy-page__footer">
        <p class="privacy-page__contact-text">
          Direct inquiries: <a href="mailto:bookings@sheeaesthetics.co.ke" class="privacy-page__email-link">bookings@sheeaesthetics.co.ke</a>
        </p>
        <div class="privacy-page__sublinks">
          <NuxtLink to="/terms" class="privacy-page__link">Terms of Service</NuxtLink>
          <span class="privacy-page__sep" aria-hidden="true">&bull;</span>
          <NuxtLink to="/support" class="privacy-page__link">Contact</NuxtLink>
          <span class="privacy-page__sep" aria-hidden="true">&bull;</span>
          <NuxtLink to="/" class="privacy-page__link">Home</NuxtLink>
        </div>
      </footer>
    </div>
  </main>
</template>

<script setup lang="ts">
/**
 * Privacy Policy Page
 * Handles displaying privacy terms and submitting data rights requests.
 */
import { reactive, ref } from 'vue'

import {
  submitPrivacyRightsRequest,
  type PrivacyRequestType,
} from '~/src/booking/privacyRightsApi'

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Privacy Policy | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content: 'Learn how Shee Aesthetics protects customer details for bookings and M-Pesa payments in Meru Town.',
    },
  ],
})

const config = useRuntimeConfig()
const apiBaseUrl = String(config.public.apiBaseUrl || '')

const form = reactive({
  requestType: 'access' as PrivacyRequestType,
  email: '',
  phone: '',
  details: '',
})
const submitting = ref(false)
const error = ref('')
const ticketId = ref('')

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
        ? 'Please wait a moment before trying again.'
        : 'Could not process request. Please check your email and try again.'
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
.privacy-page {
  min-height: 100vh;
  padding: clamp(2.5rem, 5vh, 4.5rem) 1.25rem 5rem;
  background: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
}

.privacy-page__inner {
  max-width: 44rem;
  margin: 0 auto;
}

.privacy-page__header {
  text-align: center;
  margin: 0 auto clamp(2rem, 4vh, 3rem);
}

.privacy-page__script {
  margin: 0 0 0.2rem;
  font-family: var(--font-script);
  font-size: clamp(2.2rem, 5.5vw, 3rem);
  line-height: 1;
  color: var(--color-rose, #b07a71);
  opacity: 0.95;
}

.privacy-page__eyebrow {
  display: inline-block;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 700 0.7rem/1 var(--font-body);
  color: var(--color-rose-dark, #965f57);
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}

.title-lockup__flower {
  width: 1.85rem;
  height: auto;
  flex-shrink: 0;
  opacity: 0.65;
  pointer-events: none;
}

.title-lockup__flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.title-lockup__flower--right {
  transform: rotate(8deg);
}

.privacy-page__title {
  margin: 0;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
}

.privacy-page__lead {
  margin: 0 auto;
  font: 400 0.98rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

/* Summary Card */
.privacy-summary {
  margin-bottom: 1.5rem;
}

.summary-card {
  background:
    radial-gradient(ellipse 80% 60% at 0% 0%, rgba(176, 122, 113, 0.08), transparent 60%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  padding: clamp(1.35rem, 3.5vw, 1.75rem);
  box-shadow: 0 2px 8px rgba(23, 21, 22, 0.02);
}

.summary-card__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.2rem;
  color: var(--color-ink, #252223);
  border-bottom: 1px solid rgba(176, 122, 113, 0.18);
  padding-bottom: 0.5rem;
}

.summary-points {
  display: grid;
  gap: 0.75rem;
}

.summary-points p {
  margin: 0;
  font: 400 0.9rem/1.6 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.summary-points strong {
  color: var(--color-ink, #252223);
}

/* Form Section */
.privacy-form-section {
  background:
    radial-gradient(ellipse 80% 60% at 0% 0%, rgba(176, 122, 113, 0.08), transparent 60%),
    linear-gradient(160deg, #f0eae4 0%, #e6ded6 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  padding: clamp(1.35rem, 3.5vw, 1.75rem);
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(23, 21, 22, 0.02);
}

.privacy-form-section__title {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-weight: 400;
  font-size: 1.2rem;
  color: var(--color-ink, #252223);
}

.privacy-form-section__lead {
  margin: 0 0 1.15rem;
  font: 400 0.9rem/1.55 var(--font-body);
  color: var(--color-muted, #6b605c);
}

.privacy-form {
  display: grid;
  gap: 0.75rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
  gap: 0.75rem;
}

.form-field {
  display: grid;
  gap: 0.3rem;
}

.form-field__label {
  font: 600 0.76rem/1.2 var(--font-body);
  color: var(--color-ink, #252223);
}

.form-field__input {
  font: 400 0.9rem/1.4 var(--font-body);
  padding: 0.55rem 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(176, 122, 113, 0.28);
  background: #ded8d2;
  color: var(--color-ink, #252223);
  outline: none;
  transition: border-color 0.18s ease;
}

.form-field__input:focus {
  border-color: var(--color-rose, #b07a71);
}

.form-field__textarea {
  resize: vertical;
  min-height: 4rem;
}

.form-msg {
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  font: 500 0.82rem/1.4 var(--font-body);
  margin: 0;
}

.form-msg--error {
  background: rgba(184, 51, 42, 0.12);
  color: #a32a22;
  border: 1px solid rgba(184, 51, 42, 0.25);
}

.form-msg--ok {
  background: rgba(46, 125, 50, 0.12);
  color: #256629;
  border: 1px solid rgba(46, 125, 50, 0.25);
}

.privacy-submit-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  border: none;
  background: var(--color-card-dark, #1e191b);
  color: #ffffff;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: opacity 0.18s ease;
}

.privacy-submit-btn:hover {
  opacity: 0.9;
}

/* Footer */
.privacy-page__footer {
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.privacy-page__contact-text {
  font: 400 0.9rem/1.5 var(--font-body);
  color: var(--color-muted, #6b605c);
  margin-bottom: 1rem;
}

.privacy-page__email-link {
  color: var(--color-rose-dark, #965f57);
  font-weight: 600;
  text-decoration: none;
}

.privacy-page__email-link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.privacy-page__sublinks {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.privacy-page__link {
  font: 600 0.74rem/1 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose-dark, #965f57);
  transition: color 0.18s ease;
}

.privacy-page__link:hover {
  color: var(--color-rose, #b07a71);
  text-decoration: underline;
}

.privacy-page__sep {
  color: var(--color-muted, #6b605c);
  opacity: 0.4;
}
</style>
