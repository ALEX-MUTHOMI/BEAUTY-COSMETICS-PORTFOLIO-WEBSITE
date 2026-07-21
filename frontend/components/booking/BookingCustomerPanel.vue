<template>
  <section class="book-customer" aria-labelledby="book-customer-title">
    <header class="book-customer__head">
      <h2 id="book-customer-title">Your details</h2>
    </header>

    <p v-if="submitError" class="book-customer__error" role="alert">{{ submitError }}</p>

    <form class="book-customer__form" novalidate @submit.prevent="emit('submit')">
      <label class="book-customer__field">
        <span>Full name <abbr title="required">*</abbr></span>
        <input
          v-model="customerForm.fullName"
          type="text"
          name="full_name"
          autocomplete="name"
          maxlength="80"
          required
          :disabled="disabled"
        />
      </label>

      <label class="book-customer__field">
        <span>Email <abbr title="required">*</abbr></span>
        <input
          v-model="customerForm.email"
          type="email"
          name="email"
          autocomplete="email"
          maxlength="254"
          required
          :disabled="disabled"
        />
      </label>

      <label class="book-customer__field">
        <span>Confirm email <abbr title="required">*</abbr></span>
        <input
          v-model="customerForm.emailConfirm"
          type="email"
          name="email_confirm"
          autocomplete="email"
          maxlength="254"
          required
          :disabled="disabled"
        />
      </label>

      <label class="book-customer__field">
        <span>Phone <abbr title="required">*</abbr></span>
        <input
          v-model="customerForm.phone"
          type="tel"
          name="phone"
          autocomplete="tel"
          inputmode="tel"
          placeholder="+254…"
          maxlength="20"
          required
          :disabled="disabled"
        />
      </label>

      <p class="book-customer__privacy">
        <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
      </p>

      <label class="book-customer__trap" aria-hidden="true">
        <span>Company</span>
        <input
          v-model="customerForm.honeypot"
          type="text"
          name="company"
          tabindex="-1"
          autocomplete="off"
        />
      </label>

      <label class="book-customer__policy">
        <input v-model="policyAccepted" type="checkbox" :disabled="disabled || !policyText" />
        <span>{{ policyText || 'Loading booking policy…' }}</span>
      </label>

      <div v-if="turnstileRequired" class="book-customer__turnstile">
        <NuxtTurnstile v-model="turnstileToken" :options="{ appearance: 'interaction-only' }" />
      </div>

      <div class="book-customer__actions">
        <button type="button" class="book-customer__back" :disabled="disabled" @click="emit('back')">
          Back
        </button>
        <button type="submit" class="book-customer__submit" :disabled="disabled || !canSubmit">
          {{ disabled ? 'Booking…' : 'Confirm & continue' }}
        </button>
      </div>
    </form>
  </section>
</template>

<script setup lang="ts">
import type { BookingCustomerValidation } from '@/booking/bookingCustomer'

defineProps<{
  policyText: string
  turnstileRequired: boolean
  canSubmit: boolean
  disabled: boolean
  submitError: string | null
}>()

const emit = defineEmits<{
  submit: []
  back: []
}>()

const customerForm = defineModel<BookingCustomerValidation>('customerForm', { required: true })
const policyAccepted = defineModel<boolean>('policyAccepted', { required: true })
const turnstileToken = defineModel<string>('turnstileToken', { required: true })
</script>

<style scoped>
.book-customer {
  margin-top: 1.25rem;
  padding: 1.15rem;
  border-radius: 12px;
  background: #fff;
  border: 1px solid var(--color-line);
}

.book-customer__head h2 {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 400;
}

.book-customer__field abbr {
  text-decoration: none;
  color: var(--color-rose-dark);
  font-weight: 700;
}

.book-customer__privacy {
  margin: 0;
  color: var(--color-muted);
  font-size: 0.82rem;
  line-height: 1.45;
}

.book-customer__privacy a {
  color: var(--color-rose);
}

.book-customer__error {
  margin: 0 0 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #fff5f5;
  color: #9b2c2c;
  font-size: 0.9rem;
}

.book-customer__form {
  display: grid;
  gap: 0.85rem;
}

.book-customer__field {
  display: grid;
  gap: 0.35rem;
  font: 500 0.82rem var(--font-body);
}

.book-customer__field input {
  min-height: 2.75rem;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  padding: 0 0.75rem;
  font: inherit;
}

.book-customer__trap {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.book-customer__policy {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  font-size: 0.86rem;
  color: var(--color-muted);
}

.book-customer__turnstile {
  min-height: 65px;
}

.book-customer__actions {
  display: flex;
  gap: 0.65rem;
  margin-top: 0.35rem;
}

.book-customer__back,
.book-customer__submit {
  flex: 1;
  min-height: 2.75rem;
  border-radius: 999px;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
}

.book-customer__back {
  border: 1px solid var(--color-line);
  background: #fff;
  color: var(--color-ink);
}

.book-customer__submit {
  border: 0;
  background: var(--color-rose);
  color: #fff;
}

.book-customer__back:disabled,
.book-customer__submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
