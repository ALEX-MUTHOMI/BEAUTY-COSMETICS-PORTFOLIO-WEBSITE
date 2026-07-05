<template>
  <main class="services-page">
    <header class="services-hero">
      <div class="services-hero__inner">
        <p class="label">{{ pageIntro.eyebrow }}</p>
        <h1>{{ pageIntro.title }}</h1>
        <p class="services-hero__lead">{{ pageIntro.lead }}</p>
        <p class="services-hero__note">{{ pageIntro.note }}</p>
        <SiteButton to="/book" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
      </div>
    </header>

    <nav class="services-nav" aria-label="Service categories">
      <div class="services-nav__inner">
        <a
          v-for="category in serviceCategories"
          :key="category.id"
          :href="`#${category.id}`"
          class="services-nav__link"
        >
          {{ category.name }}
        </a>
      </div>
    </nav>

    <section
      v-for="(category, index) in serviceCategories"
      :id="category.id"
      :key="category.id"
      class="services-category"
      :class="{ 'services-category--alt': index % 2 === 1 }"
    >
      <div class="services-category__inner">
        <div class="services-category__intro">
          <div class="services-category__visual">
            <img
              :src="category.image"
              :alt="category.imageAlt"
              class="services-category__photo"
              :loading="index === 0 ? 'eager' : 'lazy'"
              :fetchpriority="index === 0 ? 'high' : 'low'"
              decoding="async"
              width="400"
              height="400"
            />
            <span class="services-category__icon-wrap" aria-hidden="true">
              <img :src="category.icon" alt="" class="services-category__icon" width="26" height="26" />
            </span>
          </div>
          <div class="services-category__copy">
            <p class="label">{{ category.daysNote }}</p>
            <h2>{{ category.name }}</h2>
            <p class="services-category__text">{{ category.intro }}</p>
          </div>
        </div>

        <div class="services-category__grid">
          <ServiceTreatmentCard
            v-for="treatment in category.treatments"
            :key="treatment.name"
            :name="treatment.name"
            :description="treatment.description"
            :duration="treatment.duration"
            :price="treatment.price"
            :highlights="treatment.highlights"
          />
        </div>
      </div>
    </section>

    <section class="services-cta">
      <div class="services-cta__inner">
        <h2>Ready to book?</h2>
        <p>Choose your treatment, pick a date, and pay online to confirm your slot.</p>
        <div class="services-cta__actions">
          <SiteButton to="/book" variant="primary">{{ LANDING_PRIMARY_CTA }}</SiteButton>
          <SiteButton to="/#packages" variant="text">View packages</SiteButton>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'
import {
  SERVICES_PAGE_INTRO,
  serviceCategories,
} from '@/landing/servicesContent'

const pageIntro = SERVICES_PAGE_INTRO
const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'

definePageMeta({ layout: 'landing' })

const title = 'Services | Facials, Massage, Waxing & Makeup — Shee Aesthetics Meru'
const description =
  'Explore Shee Aesthetics services in Meru Town: deep cleansing and brightening facials, Swedish and deep tissue massage, body waxing, and everyday to bridal makeup. Book online.'

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogUrl: `${siteUrl}/services`,
  ogType: 'website',
  twitterCard: 'summary_large_image',
})

useHead({
  link: [{ rel: 'canonical', href: `${siteUrl}/services` }],
})
</script>

<style scoped>
.label {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.services-hero {
  padding: clamp(3rem, 8vh, 5rem) 1rem clamp(2rem, 5vh, 3rem);
  background: linear-gradient(180deg, var(--color-cream) 0%, var(--color-paper) 100%);
  border-bottom: 1px solid var(--color-line);
}

.services-hero__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
}

.services-hero h1 {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 2.85rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
}

.services-hero__lead {
  margin: 0 0 0.75rem;
  font: 400 1.05rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.services-hero__note {
  margin: 0 0 1.75rem;
  font: 600 0.82rem var(--font-body);
  letter-spacing: 0.03em;
  color: var(--color-ink);
}

.services-nav {
  position: sticky;
  top: var(--header-height);
  z-index: 5;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid var(--color-line);
  backdrop-filter: blur(8px);
}

.services-nav__inner {
  display: flex;
  gap: 0.5rem;
  width: var(--container);
  margin: 0 auto;
  padding: 0.65rem 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.services-nav__inner::-webkit-scrollbar {
  display: none;
}

.services-nav__link {
  flex-shrink: 0;
  padding: 0.55rem 1rem;
  border: 1px solid var(--color-line);
  border-radius: 999px;
  text-decoration: none;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-ink);
  white-space: nowrap;
  transition: border-color 0.2s, color 0.2s, background-color 0.2s;
}

.services-nav__link:hover,
.services-nav__link:focus-visible {
  border-color: var(--color-rose);
  color: var(--color-rose);
}

.services-category {
  padding: clamp(3rem, 7vh, 5rem) 1rem;
  content-visibility: auto;
  contain-intrinsic-size: auto 600px;
}

.services-category--alt {
  background: var(--color-cream);
}

.services-category__inner {
  width: var(--container);
  margin: 0 auto;
}

.services-category__intro {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
  margin-bottom: 2rem;
}

.services-category__visual {
  position: relative;
  width: min(220px, 58vw);
  margin: 0 auto;
  aspect-ratio: 1;
}

.services-category__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 12px 40px rgba(39, 37, 42, 0.1);
}

.services-category__icon-wrap {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--color-rose);
  border: 3px solid #fff;
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.45);
}

.services-category__icon {
  filter: brightness(0) invert(1);
}

.services-category__copy h2 {
  margin: 0 0 0.85rem;
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 3.5vw, 2.15rem);
  font-weight: 400;
  line-height: 1.25;
  text-align: center;
}

.services-category__text {
  margin: 0;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
  text-align: center;
  max-width: 52ch;
  margin-inline: auto;
}

.services-category__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.services-cta {
  padding: clamp(3rem, 8vh, 5rem) 1rem calc(5rem + env(safe-area-inset-bottom, 0px));
  background: var(--color-footer);
  color: #fff;
  text-align: center;
}

.services-cta__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 36rem;
}

.services-cta h2 {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 4vw, 2.35rem);
  font-weight: 400;
  color: #fff;
}

.services-cta p {
  margin: 0 0 1.75rem;
  font: 400 1rem/1.7 var(--font-body);
  color: rgba(255, 255, 255, 0.78);
}

.services-cta__actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

@media (min-width: 640px) {
  .services-category__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.15rem;
  }

  .services-cta__actions {
    flex-direction: row;
    justify-content: center;
  }
}

@media (min-width: 768px) {
  .services-category__intro {
    grid-template-columns: auto 1fr;
    gap: 2.5rem;
    margin-bottom: 2.5rem;
  }

  .services-category__visual {
    margin: 0;
    width: 200px;
  }

  .services-category__copy h2,
  .services-category__text {
    text-align: left;
    margin-inline: 0;
  }
}

@media (min-width: 1024px) {
  .services-category__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
