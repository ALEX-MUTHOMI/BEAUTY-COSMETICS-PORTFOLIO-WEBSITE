<template>
  <footer id="contact" class="site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <SheeLogo variant="light" to="/" />
        <p class="site-footer__address">
          {{ LANDING_ADDRESS_LINES[0] }}<br />
          {{ LANDING_ADDRESS_LINES[1] }}
        </p>
      </div>

      <div class="site-footer__col">
        <p class="site-footer__heading">Links</p>
        <NuxtLink to="/#welcome">About</NuxtLink>
        <NuxtLink to="/#services">Our Services</NuxtLink>
        <NuxtLink to="/#packages">Packages</NuxtLink>
        <NuxtLink to="/book">{{ LANDING_PRIMARY_CTA }}</NuxtLink>
      </div>

      <div class="site-footer__col">
        <p class="site-footer__heading">Timing</p>
        <ul class="site-footer__hours">
          <li><strong>Monday</strong> 9:00 am – 6:00 pm · singles</li>
          <li><strong>Tue &amp; Wed</strong> Full packages only</li>
          <li><strong>Thu – Sat</strong> 8:00 am – 7:00 pm · singles</li>
          <li><strong>Sunday</strong> Closed</li>
        </ul>
      </div>

      <div class="site-footer__col">
        <p class="site-footer__heading">Booking</p>
        <p class="site-footer__note">Appointments are confirmed after online payment only. No phone bookings.</p>
        <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
        <NuxtLink to="/book">{{ LANDING_PRIMARY_CTA }}</NuxtLink>
        <NuxtLink to="/staff/login">Staff login</NuxtLink>
      </div>
    </div>

    <div class="site-footer__bottom">
      <p>&copy; {{ year }} Shee Aesthetics. All rights reserved.</p>
      <div class="site-footer__legal">
        <a href="/privacy">Privacy Policy</a>
        <span>/</span>
        <a href="/terms">Terms of Use</a>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { LANDING_ADDRESS_LINES, LANDING_PRIMARY_CTA } from '@/landing/landingContent'

const year = new Date().getFullYear()
</script>

<style scoped>
.site-footer {
  background: var(--color-footer);
  color: rgba(255, 255, 255, 0.72);
  padding: var(--space-xl) 1.5rem 0;
}

.site-footer__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.3fr 1fr 1fr 1fr;
  gap: var(--space-lg);
}

.site-footer__address {
  margin: 1.25rem 0 0;
  font: 400 0.92rem/1.7 var(--font-body);
  color: rgba(255, 255, 255, 0.65);
}

.site-footer__heading {
  margin: 0 0 1.1rem;
  font: 600 0.95rem var(--font-body);
  color: #fff;
}

.site-footer__col {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.site-footer__col a {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font: 400 0.92rem var(--font-body);
}

.site-footer__col a:hover {
  color: var(--color-rose);
}

.site-footer__hours {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  font: 400 0.92rem/1.55 var(--font-body);
}

.site-footer__note {
  margin: 0;
  font: 400 0.85rem/1.55 var(--font-body);
  color: rgba(255, 255, 255, 0.55);
}

.site-footer__hours strong {
  color: #fff;
  font-weight: 600;
}

.site-footer__bottom {
  width: var(--container);
  margin: var(--space-lg) auto 0;
  padding: var(--space-md) 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  font: 400 0.82rem var(--font-body);
  color: rgba(255, 255, 255, 0.45);
}

.site-footer__legal {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.site-footer__legal a {
  color: rgba(255, 255, 255, 0.45);
  text-decoration: none;
}

@media (max-width: 767px) {
  .site-footer {
    padding-bottom: calc(var(--mobile-book-bar-height) + env(safe-area-inset-bottom, 0px));
  }
}

@media (max-width: 900px) {
  .site-footer__inner { grid-template-columns: 1fr 1fr; }
  .site-footer__brand { grid-column: 1 / -1; }
}

@media (max-width: 560px) {
  .site-footer__inner { grid-template-columns: 1fr; }
}
</style>
