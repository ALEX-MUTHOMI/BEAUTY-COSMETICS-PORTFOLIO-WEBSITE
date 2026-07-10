<template>
  <main class="legal-page">
    <div class="legal-page__inner">
      <p class="label">Legal</p>
      <h1>Privacy Policy</h1>
      <p>
        Shee Aesthetics collects the information you provide when booking online, including your name,
        email, and phone number. We use this only to perform your booking contract: manage the visit,
        initiate M-Pesa payment, send confirmation, and deliver your PDF receipt. This is not marketing.
      </p>
      <p>
        We do not sell your personal data. You do not need to create a customer account to book.
        Payment is processed securely at checkout. For privacy rights questions, email
        <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>.
      </p>
      <NuxtLink to="/" class="legal-page__back">Back to home</NuxtLink>
    </div>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'landing' })

useHead({ title: 'Privacy Policy | Shee Aesthetics' })
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

.legal-page h1 {
  margin: 0 0 1.25rem;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 400;
}

.legal-page p {
  margin: 0 0 1rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.legal-page a {
  color: var(--color-rose);
}

.legal-page__back {
  display: inline-block;
  margin-top: 1.5rem;
  font: 600 0.8rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose);
}
</style>
