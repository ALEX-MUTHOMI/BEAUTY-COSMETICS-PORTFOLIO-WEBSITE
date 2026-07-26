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

      <div class="site-footer__col site-footer__col--visit">
        <p class="site-footer__heading">Visit</p>
        <a class="site-footer__mail" href="mailto:bookings@sheeaesthetics.co.ke">
          bookings@sheeaesthetics.co.ke
        </a>
        <a
          v-if="contactIsLive"
          class="site-footer__contact"
          :href="whatsappUrl"
          target="_blank"
          rel="noopener noreferrer"
          @click="trackFunnelEvent('wa_click', { surface: 'footer' })"
        >
          {{ whatsappLabel }}
        </a>
        <a
          v-if="contactIsLive && phoneTel"
          class="site-footer__contact"
          :href="phoneTel"
        >
          {{ phoneDisplay }}
        </a>
        <p v-else-if="!contactIsLive" class="site-footer__phone-pending">{{ phoneDisplay }}</p>
        <InstagramLink variant="ghost" label="Instagram" aria-label="Shee Aesthetics on Instagram" />
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
.site-footer {
  background: var(--color-footer);
  color: rgba(255, 255, 255, 0.72);
  padding: clamp(2.75rem, 6vw, 4.25rem) 1.25rem 0;
}

.site-footer__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.85rem;
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
  align-items: flex-start;
  gap: 0.55rem;
}

.site-footer__col a,
.site-footer__mail,
.site-footer__contact {
  display: inline-flex;
  align-items: center;
  min-height: 2.75rem;
  padding: 0.25rem 0;
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font: 400 0.92rem/1.4 var(--font-body);
  transition: color 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__col a:hover,
.site-footer__mail:hover,
.site-footer__contact:hover {
  color: var(--color-rose);
}

.site-footer__phone-pending {
  margin: 0;
  color: rgba(255, 255, 255, 0.55);
  font: 400 0.9rem/1.45 var(--font-body);
}

.site-footer__cta {
  margin-top: 0.55rem;
  width: auto;
  max-width: 100%;
}

.site-footer__hours {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  font: 400 0.88rem/1.45 var(--font-body);
  color: rgba(255, 255, 255, 0.68);
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
  display: inline-flex;
  align-items: center;
  min-height: 2.75rem;
  padding: 0.25rem 0.15rem;
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  -webkit-tap-highlight-color: transparent;
}

.site-footer__legal a:hover {
  color: var(--color-rose);
}

@media (max-width: 767px) {
  .site-footer {
    /* Clear sticky mobile book bar */
    padding-bottom: calc(var(--mobile-book-bar-height) + env(safe-area-inset-bottom, 0px));
  }
}

@media (min-width: 561px) {
  .site-footer__inner {
    grid-template-columns: 1.2fr 1fr;
    gap: clamp(1.5rem, 4vw, 2.75rem) clamp(1.25rem, 3vw, 2rem);
  }

  .site-footer__brand {
    grid-column: 1 / -1;
  }
}

@media (min-width: 901px) {
  .site-footer__inner {
    grid-template-columns: 1.45fr 0.9fr 1.15fr 1.05fr;
    align-items: start;
  }

  .site-footer__brand {
    grid-column: auto;
  }
}
</style>
