<template>
  <footer id="contact" class="site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__brand">
        <SheeLogo variant="light" to="/" size="md" />
        <p class="site-footer__tagline">Facials, waxing, massage &amp; makeup in Meru Town.</p>
        <p class="site-footer__address">
          {{ LANDING_ADDRESS_LINES[0] }} · {{ LANDING_ADDRESS_LINES[1] }}
        </p>
      </div>

      <nav class="site-footer__col" aria-label="Explore">
        <p class="site-footer__heading">Explore</p>
        <NuxtLink to="/">Home</NuxtLink>
        <NuxtLink to="/services">Services</NuxtLink>
        <NuxtLink :to="SERVICES_ROUTES.fullPackages">Packages</NuxtLink>
        <NuxtLink :to="SERVICES_ROUTES.singleSessions">Treatments</NuxtLink>
      </nav>

      <div class="site-footer__col">
        <p class="site-footer__heading">Hours</p>
        <ul class="site-footer__hours">
          <li><strong>Mon</strong> 7am–7pm · treatments</li>
          <li><strong>Tue–Wed</strong> 7am–7pm · packages</li>
          <li><strong>Thu–Sat</strong> 7am–7pm · treatments</li>
          <li><strong>Sun</strong> Closed</li>
        </ul>
      </div>

      <div class="site-footer__col">
        <p class="site-footer__heading">Visit</p>
        <a href="mailto:bookings@sheeaesthetics.co.ke">bookings@sheeaesthetics.co.ke</a>
        <a
          v-if="contactIsLive"
          :href="whatsappUrl"
          target="_blank"
          rel="noopener noreferrer"
          @click="trackFunnelEvent('wa_click', { surface: 'footer' })"
        >
          {{ whatsappLabel }}
        </a>
        <a v-if="contactIsLive && phoneTel" :href="phoneTel">
          {{ phoneDisplay }}
        </a>
        <p v-else class="site-footer__phone-pending">{{ phoneDisplay }}</p>
        <a
          :href="LANDING_INSTAGRAM_URL"
          target="_blank"
          rel="noopener noreferrer"
        >
          Instagram
        </a>
        <SiteButton
          v-if="bookIsExternal"
          :href="bookHref"
          variant="primary"
          class="site-footer__cta"
          @click="trackFunnelEvent('cta_book_click', { surface: 'footer', href: bookHref })"
        >
          {{ LANDING_PRIMARY_CTA }}
        </SiteButton>
        <SiteButton
          v-else
          :to="bookHref"
          variant="primary"
          class="site-footer__cta"
          @click="trackFunnelEvent('cta_book_click', { surface: 'footer', href: bookHref })"
        >
          {{ LANDING_PRIMARY_CTA }}
        </SiteButton>
      </div>
    </div>

    <div class="site-footer__bottom">
      <p>&copy; {{ year }} Shee Aesthetics</p>
      <div class="site-footer__legal">
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        <span aria-hidden="true">·</span>
        <NuxtLink to="/terms">Terms</NuxtLink>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import {
  LANDING_ADDRESS_LINES,
  LANDING_INSTAGRAM_URL,
  LANDING_PRIMARY_CTA,
} from '@/landing/landingContent'
import { SERVICES_ROUTES } from '@/landing/servicesNavigation'
import { trackFunnelEvent } from '@/landing/funnelEvents'
import { useLandingBookCta } from '@/landing/useLandingBookCta'

const year = new Date().getFullYear()

const { bookHref, bookIsExternal, contact } = useLandingBookCta()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl
const whatsappLabel = contact.whatsappLabel
const phoneDisplay = contact.phoneDisplay
const phoneTel = contact.phoneTel
</script>

<style scoped>
/* Base chrome — keep opaque footer brand plane on all breakpoints */
.site-footer {
  background: var(--color-footer);
  color: rgba(255, 255, 255, 0.7);
  padding: clamp(2.5rem, 6vw, 4rem) 1.25rem 0;
}

.site-footer__phone-pending {
  margin: 0;
  color: rgba(255, 255, 255, 0.55);
  font: 400 0.9rem/1.45 var(--font-body);
}

.site-footer__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
  padding-bottom: clamp(1.75rem, 4vw, 2.5rem);
}

.site-footer__tagline {
  margin: 1.1rem 0 0.45rem;
  max-width: 28ch;
  font: 400 0.95rem/1.55 var(--font-body);
  color: rgba(255, 255, 255, 0.78);
}

.site-footer__address {
  margin: 0;
  font: 400 0.85rem/1.5 var(--font-body);
  color: rgba(255, 255, 255, 0.5);
}

.site-footer__heading {
  margin: 0 0 0.85rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #fff;
}

.site-footer__col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.site-footer__col a {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font: 400 0.92rem/1.4 var(--font-body);
  transition: color 0.15s ease;
}

.site-footer__col a:hover {
  color: var(--color-rose);
}

.site-footer__cta {
  margin-top: 0.35rem;
  color: #fff !important;
  font-weight: 600 !important;
}

.site-footer__hours {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font: 400 0.88rem/1.45 var(--font-body);
}

.site-footer__hours strong {
  color: #fff;
  font-weight: 600;
  margin-right: 0.35rem;
}

.site-footer__bottom {
  width: var(--container);
  margin: 0 auto;
  padding: 1.1rem 0 calc(1.1rem + env(safe-area-inset-bottom, 0px));
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  font: 400 0.8rem var(--font-body);
  color: rgba(255, 255, 255, 0.42);
}

.site-footer__legal {
  display: flex;
  gap: 0.45rem;
  align-items: center;
}

.site-footer__legal a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
}

.site-footer__legal a:hover {
  color: var(--color-rose);
}

@media (max-width: 767px) {
  .site-footer {
    padding-bottom: calc(var(--mobile-book-bar-height) + env(safe-area-inset-bottom, 0px));
  }
}

@media (min-width: 561px) {
  .site-footer__inner {
    grid-template-columns: 1fr 1fr;
    gap: clamp(1.5rem, 4vw, 2.75rem);
  }

  .site-footer__brand {
    grid-column: 1 / -1;
  }
}

@media (min-width: 901px) {
  .site-footer__inner {
    grid-template-columns: 1.4fr 1fr 1.1fr 1fr;
  }

  .site-footer__brand {
    grid-column: auto;
  }
}
</style>
