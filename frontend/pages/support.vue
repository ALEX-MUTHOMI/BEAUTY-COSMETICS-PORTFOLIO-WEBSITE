<template>
  <main class="support-page">
    <div class="support-page__container">
      <!-- Masthead -->
      <header class="support-masthead">
        <span class="support-masthead__brand">Shee Aesthetics</span>
        <span class="support-masthead__eyebrow">Studio Desk &amp; Inquiries</span>
        <h1 class="support-masthead__title">{{ CUSTOMER_SUPPORT_PAGE.title }}</h1>
        <p class="support-masthead__lead">
          {{ CUSTOMER_SUPPORT_PAGE.lead }}
        </p>
      </header>

      <!-- Main Editorial Two-Column Grid -->
      <div class="support-layout">
        <!-- Left Column: The Meru Studio & Booking Rhythms -->
        <section class="support-panel support-panel--studio" aria-label="Studio Location and Hours">
          <div class="panel-header">
            <span class="panel-header__kicker">Location &amp; Rhythms</span>
            <h2 class="panel-header__title">Private Meru Sanctuary</h2>
            <p class="panel-header__desc">
              Every visit is scheduled exclusively 1-on-1 to ensure unhurried, private care and dedicated attention.
            </p>
          </div>

          <!-- Location Detail -->
          <div class="studio-detail">
            <div class="studio-detail__icon" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                <circle cx="12" cy="10" r="3" />
              </svg>
            </div>
            <div class="studio-detail__content">
              <h3 class="studio-detail__label">Studio Address</h3>
              <p class="studio-detail__text">{{ CUSTOMER_SUPPORT_PAGE.studioAddress }}</p>
              <span class="studio-detail__subtext">Meru Town Centre &bull; Private appointment suite</span>
            </div>
          </div>

          <!-- Booking Schedule -->
          <div class="studio-schedule">
            <h3 class="studio-schedule__title">Weekly Appointment Schedule</h3>

            <div class="schedule-row">
              <div class="schedule-row__day">Tuesday &amp; Wednesday</div>
              <div class="schedule-row__type">
                <strong>Full Care Packages</strong>
                <span>Dedicated head-to-toe wellness and signature glow packages</span>
              </div>
            </div>

            <div class="schedule-row">
              <div class="schedule-row__day">Mon, Thu &ndash; Sat</div>
              <div class="schedule-row__type">
                <strong>Single Treatments</strong>
                <span>Targeted facials, tension massage, waxing, and bespoke makeup</span>
              </div>
            </div>

            <div class="schedule-row schedule-row--closed">
              <div class="schedule-row__day">Sunday</div>
              <div class="schedule-row__type">
                <strong>Closed</strong>
                <span>Studio rest &amp; sanctuary sanitization</span>
              </div>
            </div>
          </div>

          <!-- Direct Voice & Email Touchpoints -->
          <div class="studio-direct-lines">
            <a :href="`tel:${CUSTOMER_SUPPORT_PAGE.phoneE164}`" class="direct-line-item">
              <div class="direct-line-item__icon" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                </svg>
              </div>
              <div class="direct-line-item__text">
                <span class="direct-line-item__label">Call the Studio</span>
                <span class="direct-line-item__value">{{ CUSTOMER_SUPPORT_PAGE.phoneDisplay }}</span>
              </div>
            </a>

            <a :href="`mailto:${CUSTOMER_SUPPORT_PAGE.email}`" class="direct-line-item">
              <div class="direct-line-item__icon" aria-hidden="true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
              </div>
              <div class="direct-line-item__text">
                <span class="direct-line-item__label">Email Inquiries</span>
                <span class="direct-line-item__value">{{ CUSTOMER_SUPPORT_PAGE.email }}</span>
              </div>
            </a>
          </div>
        </section>

        <!-- Right Column: Direct WhatsApp Concierge & Guest Policies -->
        <section class="support-panel support-panel--concierge" aria-label="Direct Concierge and Guest Guidance">
          <!-- Primary Obsidian WhatsApp Card -->
          <div class="concierge-card concierge-card--whatsapp">
            <div class="concierge-card__status">
              <span class="status-dot" aria-hidden="true"></span>
              <span>Direct Studio Line</span>
            </div>

            <h2 class="concierge-card__title">WhatsApp Concierge</h2>
            <p class="concierge-card__desc">
              Have a quick question about slot availability, custom bridal arrangements, M-Pesa payment, or need to reschedule? Message Shee directly.
            </p>

            <div class="concierge-card__actions">
              <a
                :href="whatsappUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="concierge-btn concierge-btn--wa"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2zm0 1.67c2.2 0 4.26.86 5.82 2.42a8.2 8.2 0 0 1 2.41 5.82c0 4.54-3.7 8.24-8.23 8.24-1.44 0-2.84-.37-4.08-1.07l-.29-.17-3.12.82.83-3.04-.19-.31a8.2 8.2 0 0 1-1.26-4.47c0-4.54 3.7-8.24 8.11-8.24z" />
                </svg>
                <span>Chat on WhatsApp</span>
              </a>
              <span class="concierge-card__hint">Quick response during studio hours</span>
            </div>
          </div>

          <!-- Essential Guest Guidance (Accordion / Restful Tiles) -->
          <div class="guest-guidance">
            <h3 class="guest-guidance__title">Peace of Mind for Your Visit</h3>

            <div class="guidance-tile">
              <div class="guidance-tile__header">
                <span class="guidance-tile__bullet" aria-hidden="true">&bull;</span>
                <h4 class="guidance-tile__heading">M-Pesa STK Push Payment</h4>
              </div>
              <p class="guidance-tile__body">
                Your booking prompt is sent directly to your phone. If your screen is locked or the prompt does not appear, tap <em>Resend Prompt</em> on the payment screen. You will never be charged twice.
              </p>
            </div>

            <div class="guidance-tile">
              <div class="guidance-tile__header">
                <span class="guidance-tile__bullet" aria-hidden="true">&bull;</span>
                <h4 class="guidance-tile__heading">Rescheduling &amp; Changes</h4>
              </div>
              <p class="guidance-tile__body">
                We understand plans change. Notify us at least 24 hours prior to your scheduled slot via WhatsApp or phone, and we will gladly move your appointment to another open time.
              </p>
            </div>

            <div class="guidance-tile">
              <div class="guidance-tile__header">
                <span class="guidance-tile__bullet" aria-hidden="true">&bull;</span>
                <h4 class="guidance-tile__heading">Private Consultation on Arrival</h4>
              </div>
              <p class="guidance-tile__body">
                Every facial, massage, and makeup session begins with a brief skin check and consultation to adjust formulas, oils, and intensity to your exact preferences.
              </p>
            </div>
          </div>

          <!-- Quick Navigation to FAQ & Services -->
          <div class="support-quick-nav">
            <span>Looking for answers to common questions?</span>
            <NuxtLink to="/faq" class="support-quick-link">
              Explore Studio FAQ &rarr;
            </NuxtLink>
          </div>
        </section>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CUSTOMER_SUPPORT_PAGE } from '~/src/landing/clientPagesContent'

const runtimeConfig = useRuntimeConfig()

useHead({
  title: 'Contact & Customer Support | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content:
        'Contact Shee Aesthetics in Meru Town for appointment bookings, WhatsApp support, M-Pesa inquiries, and directions.',
    },
  ],
})

const whatsappDigits = computed(() => {
  const cfg = String(runtimeConfig.public.whatsappE164 || '').replace(/\D/g, '')
  return cfg || CUSTOMER_SUPPORT_PAGE.whatsappE164
})

const whatsappUrl = computed(() => {
  const text = encodeURIComponent(
    'Hello Shee Aesthetics, I have an inquiry regarding appointments at your Meru studio.',
  )
  return `https://wa.me/${whatsappDigits.value}?text=${text}`
})
</script>

<style scoped>
.support-page {
  min-height: 100vh;
  background-color: var(--color-paper, #e5e1dc);
  color: var(--color-ink, #252223);
  padding: calc(var(--header-pad, 2rem) + 4.5rem) 1.5rem 5rem;
}

.support-page__container {
  max-width: 1140px;
  margin: 0 auto;
}

/* Masthead */
.support-masthead {
  text-align: center;
  margin-bottom: 3.5rem;
}

.support-masthead__brand {
  display: block;
  font-family: var(--font-script, 'Parisienne', cursive);
  font-size: clamp(2rem, 4.5vw, 3rem);
  color: var(--color-rose, #b07a71);
  line-height: 1.1;
  margin-bottom: 0.35rem;
}

.support-masthead__eyebrow {
  display: inline-block;
  font-family: var(--font-sans, 'Manrope', sans-serif);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--color-muted, #786f6a);
  margin-bottom: 0.75rem;
}

.support-masthead__title {
  font-family: var(--font-serif, 'Fraunces', serif);
  font-size: clamp(2.2rem, 5vw, 3.4rem);
  font-weight: 400;
  letter-spacing: -0.02em;
  color: var(--color-ink, #252223);
  line-height: 1.15;
  margin: 0 0 1rem;
}

.support-masthead__lead {
  font-family: var(--font-sans, 'Manrope', sans-serif);
  font-size: clamp(0.98rem, 1.8vw, 1.12rem);
  line-height: 1.6;
  color: var(--color-muted, #6b605c);
  max-width: 620px;
  margin: 0 auto;
}

/* Two-Column Editorial Layout */
.support-layout {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 900px) {
  .support-layout {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}

/* Panels */
.support-panel {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.support-panel--studio {
  background: linear-gradient(165deg, #f3ede7 0%, #e8dfd7 100%);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 1.25rem;
  padding: 2.25rem;
  box-shadow: 0 10px 30px rgba(37, 34, 35, 0.04);
}

.panel-header__kicker {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose-dark, #965f57);
  margin-bottom: 0.35rem;
}

.panel-header__title {
  font-family: var(--font-serif, 'Fraunces', serif);
  font-size: 1.85rem;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: var(--color-ink, #252223);
  margin: 0 0 0.65rem;
}

.panel-header__desc {
  font-size: 0.95rem;
  line-height: 1.55;
  color: var(--color-muted, #6b605c);
  margin: 0;
}

/* Studio Detail */
.studio-detail {
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(176, 122, 113, 0.2);
  border-radius: 0.85rem;
}

.studio-detail__icon {
  flex-shrink: 0;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  background: rgba(176, 122, 113, 0.15);
  color: var(--color-rose-dark, #965f57);
  display: grid;
  place-items: center;
}

.studio-detail__label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-rose-dark, #965f57);
  margin: 0 0 0.2rem;
}

.studio-detail__text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-ink, #252223);
  margin: 0 0 0.2rem;
}

.studio-detail__subtext {
  font-size: 0.85rem;
  color: var(--color-muted, #786f6a);
}

/* Studio Schedule */
.studio-schedule {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.studio-schedule__title {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-ink, #252223);
  margin: 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid rgba(176, 122, 113, 0.2);
}

.schedule-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px dashed rgba(176, 122, 113, 0.2);
  font-size: 0.92rem;
}

.schedule-row:last-child {
  border-bottom: none;
}

.schedule-row__day {
  font-weight: 700;
  color: var(--color-ink, #252223);
}

.schedule-row__type {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.schedule-row__type strong {
  color: var(--color-ink, #252223);
  font-weight: 600;
}

.schedule-row__type span {
  font-size: 0.85rem;
  color: var(--color-muted, #786f6a);
}

.schedule-row--closed .schedule-row__day,
.schedule-row--closed .schedule-row__type strong {
  color: var(--color-muted, #8a827d);
}

/* Studio Direct Lines */
.studio-direct-lines {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 0.5rem;
}

@media (max-width: 550px) {
  .studio-direct-lines {
    grid-template-columns: 1fr;
  }
}

.direct-line-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.9rem 1.1rem;
  background: rgba(255, 255, 255, 0.65);
  border: 1px solid rgba(176, 122, 113, 0.24);
  border-radius: 0.75rem;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s ease;
}

.direct-line-item:hover {
  background: #ffffff;
  border-color: var(--color-rose, #b07a71);
  transform: translateY(-2px);
}

.direct-line-item__icon {
  color: var(--color-rose-dark, #965f57);
}

.direct-line-item__text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.direct-line-item__label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-muted, #786f6a);
}

.direct-line-item__value {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-ink, #252223);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Right Column: Concierge Card */
.concierge-card--whatsapp {
  background: linear-gradient(165deg, #241e20 0%, #171516 100%);
  border: 1px solid rgba(176, 122, 113, 0.35);
  border-radius: 1.25rem;
  padding: 2.25rem;
  color: #f7f3ef;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.12);
}

.concierge-card__status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #e0cdc6;
  margin-bottom: 0.75rem;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: #4ade80;
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
}

.concierge-card__title {
  font-family: var(--font-serif, 'Fraunces', serif);
  font-size: 2rem;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: #ffffff;
  margin: 0 0 0.85rem;
}

.concierge-card__desc {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #cfc6c0;
  margin: 0 0 1.75rem;
}

.concierge-card__actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.concierge-btn--wa {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  padding: 0.95rem 1.75rem;
  background: linear-gradient(135deg, #b07a71 0%, #965f57 100%);
  color: #ffffff;
  font-family: var(--font-sans, 'Manrope', sans-serif);
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 9999px;
  text-decoration: none;
  transition: all 0.25s ease;
  box-shadow: 0 4px 14px rgba(176, 122, 113, 0.35);
}

.concierge-btn--wa:hover {
  background: linear-gradient(135deg, #be877e 0%, #a46b63 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(176, 122, 113, 0.45);
}

.concierge-card__hint {
  font-size: 0.8rem;
  color: #a89f9a;
  text-align: center;
}

/* Guest Guidance */
.guest-guidance {
  background: #f0eae4;
  border: 1px solid rgba(176, 122, 113, 0.24);
  border-radius: 1.25rem;
  padding: 1.85rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.guest-guidance__title {
  font-family: var(--font-serif, 'Fraunces', serif);
  font-size: 1.25rem;
  font-weight: 400;
  color: var(--color-ink, #252223);
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(176, 122, 113, 0.2);
}

.guidance-tile {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.guidance-tile__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.guidance-tile__bullet {
  color: var(--color-rose, #b07a71);
  font-size: 1.2rem;
  line-height: 1;
}

.guidance-tile__heading {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--color-ink, #252223);
  margin: 0;
}

.guidance-tile__body {
  font-size: 0.88rem;
  line-height: 1.55;
  color: var(--color-muted, #6b605c);
  margin: 0;
  padding-left: 1.2rem;
}

.guidance-tile__body em {
  font-style: normal;
  font-weight: 600;
  color: var(--color-ink, #252223);
}

/* Quick Navigation */
.support-quick-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.1rem 1.5rem;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(176, 122, 113, 0.22);
  border-radius: 0.9rem;
  font-size: 0.88rem;
  color: var(--color-muted, #6b605c);
}

@media (max-width: 550px) {
  .support-quick-nav {
    flex-direction: column;
    text-align: center;
  }
}

.support-quick-link {
  font-weight: 600;
  color: var(--color-rose-dark, #965f57);
  text-decoration: none;
  white-space: nowrap;
  transition: color 0.2s ease;
}

.support-quick-link:hover {
  color: var(--color-ink, #252223);
}
</style>
