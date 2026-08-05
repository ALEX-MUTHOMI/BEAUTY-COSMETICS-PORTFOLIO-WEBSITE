<template>
  <main class="faq">
    <SectionHeading
      eyebrow="Help"
      title="Frequently Asked Questions"
      description="Quick answers about booking, payment, and what to do next."
    />

    <div class="faq__content">
      <section class="faq__section" aria-labelledby="faq-booking">
        <h3 id="faq-booking">How does booking work?</h3>
        <p>
          Choose your service, pick an available day and time, then submit your details to reserve a spot.
          After that, complete the M-Pesa payment prompt to confirm.
        </p>
      </section>

      <section class="faq__section" aria-labelledby="faq-confirmation">
        <h3 id="faq-confirmation">Where do I see confirmation?</h3>
        <p>
          After you submit payment, you’ll be taken to a confirmation page that automatically checks your
          booking status. If payment isn’t completed yet, the page will keep polling until it’s done.
        </p>
      </section>

      <section class="faq__section" aria-labelledby="faq-mpesa">
        <h3 id="faq-mpesa">What if I miss the M-Pesa prompt?</h3>
        <p>
          Use the “Resend M-Pesa prompt” option on your confirmation page. Enter the same phone number you
          used when booking.
        </p>
      </section>

      <section class="faq__section" aria-labelledby="faq-limited">
        <h3 id="faq-limited">Why are there “limited spots”?</h3>
        <p>
          Booking availability depends on service duration and shared scheduling capacity for the studio.
          We only show times that can still fit within capacity for the selected day.
        </p>
      </section>

      <section class="faq__section" aria-labelledby="faq-change">
        <h3 id="faq-change">Can I reschedule my appointment?</h3>
        <p>
          Rescheduling is handled by the studio team. If you need to change your appointment, contact us via
          WhatsApp or call using the buttons in the site header/footer.
        </p>
      </section>

      <section class="faq__section" aria-labelledby="faq-contact">
        <h3 id="faq-contact">How do I contact Shee Aesthetics?</h3>
        <p>
          Use WhatsApp (when available) or call/email from the site header/footer. We’ll help you with booking
          questions and any changes you need.
        </p>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
// Static marketing content — no API dependencies.
</script>

<style scoped>
.faq {
  padding: 3rem 1rem;
  max-width: 68rem;
  margin: 0 auto;
}

.faq__content {
  margin-top: 2.25rem;
  display: grid;
  gap: 1.25rem;
}

.faq__section {
  padding: 1.25rem 1.25rem;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 1rem;
  background: #fff;
}

.faq__section h3 {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-weight: 500;
  letter-spacing: -0.02em;
  font-size: 1.25rem;
}

.faq__section p {
  margin: 0;
  color: var(--color-text-muted);
  line-height: 1.75;
}
</style>
