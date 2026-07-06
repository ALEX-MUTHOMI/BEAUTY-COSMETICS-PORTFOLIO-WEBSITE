<template>
  <main class="services-page">
    <header class="services-hero">
      <div class="services-hero__inner">
        <p class="label">{{ pageIntro.eyebrow }}</p>
        <h1>{{ pageIntro.title }}</h1>
        <p class="services-hero__lead">{{ pageIntro.lead }}</p>
        <p class="services-hero__note">{{ pageIntro.note }}</p>
      </div>
    </header>

    <section class="services-picker" aria-label="Choose a service category">
      <div
        class="services-tabs"
        role="tablist"
        aria-label="Service categories"
      >
        <button
          v-for="category in serviceCategories"
          :id="`tab-${category.id}`"
          :key="category.id"
          type="button"
          role="tab"
          class="services-tab"
          :class="{ 'services-tab--active': activeCategoryId === category.id }"
          :aria-selected="activeCategoryId === category.id"
          :aria-controls="`panel-${category.id}`"
          @click="selectCategory(category.id)"
        >
          <span class="services-tab__icon-wrap" aria-hidden="true">
            <img :src="category.icon" alt="" class="services-tab__icon" width="22" height="22" />
          </span>
          <span class="services-tab__label">{{ category.cardTitle }}</span>
        </button>
      </div>

      <div
        :id="`panel-${activeCategory.id}`"
        role="tabpanel"
        class="services-panel"
        :class="`services-panel--${activeCategory.id}`"
        :aria-labelledby="`tab-${activeCategory.id}`"
      >
        <div class="services-panel__inner">
          <div class="services-panel__intro">
            <div class="services-panel__visual">
              <img
                :src="activeCategory.image"
                :alt="activeCategory.imageAlt"
                class="services-panel__photo"
                loading="eager"
                decoding="async"
                width="400"
                height="400"
              />
              <span class="services-panel__icon-wrap" aria-hidden="true">
                <img :src="activeCategory.icon" alt="" width="26" height="26" />
              </span>
            </div>
            <div class="services-panel__copy">
              <p class="label">{{ activeCategory.daysNote }}</p>
              <h2>{{ activeCategory.name }}</h2>
              <p class="services-panel__text">{{ activeCategory.intro }}</p>
              <p class="services-panel__hint">
                Tap a treatment below to select it, then book your visit.
              </p>
            </div>
          </div>

          <div class="services-panel__grid">
            <ServiceTreatmentCard
              v-for="(treatment, index) in activeCategory.treatments"
              :key="treatment.name"
              :name="treatment.name"
              :description="treatment.description"
              :duration="treatment.duration"
              :price="treatment.price"
              :highlights="treatment.highlights"
              :index="index"
              :variant="activeCategory.id"
              :selected="selectedTreatmentName === treatment.name"
              @select="selectTreatment(treatment.name)"
            />
          </div>

          <div class="services-panel__book" :class="{ 'services-panel__book--ready': selectedTreatmentName }">
            <p v-if="selectedTreatmentName" class="services-panel__chosen">
              You selected <strong>{{ selectedTreatmentName }}</strong>
            </p>
            <p v-else class="services-panel__chosen services-panel__chosen--muted">
              Select a treatment above to continue
            </p>
            <SiteButton
              to="/book"
              variant="primary"
              class="services-panel__cta"
              :class="{ 'services-panel__cta--disabled': !selectedTreatmentName }"
            >
              {{ LANDING_PRIMARY_CTA }}
            </SiteButton>
          </div>
        </div>
      </div>
    </section>

    <section class="services-cta">
      <div class="services-cta__inner">
        <h2>Need a full visit?</h2>
        <p>Tuesday and Wednesday packages combine facial, waxing, massage and makeup in one room.</p>
        <div class="services-cta__actions">
          <SiteButton to="/#packages" variant="primary">View packages</SiteButton>
          <SiteButton to="/book" variant="text">{{ LANDING_PRIMARY_CTA }}</SiteButton>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { LANDING_PRIMARY_CTA } from '@/landing/landingContent'
import {
  SERVICES_PAGE_INTRO,
  serviceCategories,
} from '@/landing/servicesContent'

const route = useRoute()
const router = useRouter()

const pageIntro = SERVICES_PAGE_INTRO
const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'

const validIds = serviceCategories.map((c) => c.id)
const activeCategoryId = ref(validIds[0] ?? 'facials')
const selectedTreatmentName = ref<string | null>(null)

const activeCategory = computed(
  () => serviceCategories.find((c) => c.id === activeCategoryId.value) ?? serviceCategories[0]!,
)

function selectCategory(id: string) {
  if (!validIds.includes(id)) return
  activeCategoryId.value = id
  selectedTreatmentName.value = null
  router.replace({ hash: `#${id}` })
}

function selectTreatment(name: string) {
  selectedTreatmentName.value = name
}

function syncFromHash() {
  const hash = route.hash.replace('#', '')
  if (hash && validIds.includes(hash)) {
    activeCategoryId.value = hash
    selectedTreatmentName.value = null
  }
}

onMounted(syncFromHash)
watch(() => route.hash, syncFromHash)

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
  padding: clamp(2.5rem, 6vh, 4rem) 1rem 1.5rem;
  background: linear-gradient(180deg, var(--color-cream) 0%, var(--color-paper) 100%);
  border-bottom: 1px solid var(--color-line);
}

.services-hero__inner {
  width: var(--container);
  margin: 0 auto;
  max-width: 42rem;
}

.services-hero h1 {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-size: clamp(2rem, 5vw, 2.85rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
}

.services-hero__lead {
  margin: 0 0 0.5rem;
  font: 400 1.05rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.services-hero__note {
  margin: 0;
  font: 600 0.82rem var(--font-body);
  letter-spacing: 0.03em;
  color: var(--color-ink);
}

/* Picker shell */
.services-picker {
  width: var(--container);
  margin: 0 auto;
  padding: 1.25rem 0 calc(4.5rem + env(safe-area-inset-bottom, 0px));
}

.services-tabs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.services-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  min-height: 4.5rem;
  padding: 0.75rem 0.5rem;
  border: 2px solid var(--color-line);
  border-radius: 2px;
  background: #fff;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.2s,
    background-color 0.2s,
    box-shadow 0.2s,
    color 0.2s;
}

.services-tab:hover {
  border-color: var(--color-rose-soft);
  background: var(--color-cream);
}

.services-tab:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.services-tab--active {
  border-color: var(--color-rose);
  background: linear-gradient(165deg, var(--color-rose) 0%, var(--color-rose-dark) 100%);
  box-shadow: 0 8px 24px rgba(222, 150, 141, 0.35);
  color: #fff;
}

.services-tab__icon-wrap {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-rose-soft);
}

.services-tab--active .services-tab__icon-wrap {
  background: rgba(255, 255, 255, 0.2);
}

.services-tab__icon {
  object-fit: contain;
  filter: brightness(0) saturate(100%) invert(72%) sepia(18%) saturate(749%) hue-rotate(319deg) brightness(92%) contrast(89%);
}

.services-tab--active .services-tab__icon {
  filter: brightness(0) invert(1);
}

.services-tab__label {
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-align: center;
  line-height: 1.25;
}

/* Category panel — themed backgrounds */
.services-panel {
  border-radius: 2px;
  border: 1px solid var(--color-line);
  overflow: hidden;
  animation: panel-in 0.28s var(--ease-story, ease) both;
}

.services-panel--facials {
  background: linear-gradient(180deg, #fff5f3 0%, #fff 28%);
}

.services-panel--massage {
  background: linear-gradient(180deg, #f9f0ee 0%, #fff 28%);
}

.services-panel--waxing {
  background: linear-gradient(180deg, #f7ece9 0%, #fff 28%);
}

.services-panel--makeup {
  background: linear-gradient(180deg, #faf2f0 0%, #fff 28%);
}

.services-panel__inner {
  padding: 1.5rem 1rem 1.25rem;
}

.services-panel__intro {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(39, 37, 42, 0.08);
}

.services-panel__visual {
  position: relative;
  width: min(160px, 42vw);
  margin: 0 auto;
  aspect-ratio: 1;
}

.services-panel__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 10px 32px rgba(39, 37, 42, 0.12);
}

.services-panel__icon-wrap {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-rose);
  border: 3px solid #fff;
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.45);
}

.services-panel__icon-wrap img {
  filter: brightness(0) invert(1);
}

.services-panel__copy h2 {
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3.5vw, 2rem);
  font-weight: 400;
  line-height: 1.25;
  text-align: center;
  color: var(--color-ink);
}

.services-panel__text {
  margin: 0 0 0.65rem;
  font: 400 0.95rem/1.7 var(--font-body);
  color: var(--color-muted);
  text-align: center;
}

.services-panel__hint {
  margin: 0;
  font: 600 0.8rem var(--font-body);
  color: var(--color-rose-dark);
  text-align: center;
}

.services-panel__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

.services-panel__book {
  margin-top: 1.5rem;
  padding: 1.15rem 1rem;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px dashed var(--color-line);
  text-align: center;
  transition: border-color 0.2s, background-color 0.2s;
}

.services-panel__book--ready {
  background: #fff;
  border: 2px solid var(--color-rose-soft);
  box-shadow: 0 8px 24px rgba(222, 150, 141, 0.12);
}

.services-panel__chosen {
  margin: 0 0 1rem;
  font: 400 0.95rem var(--font-body);
  color: var(--color-ink);
}

.services-panel__chosen--muted {
  color: var(--color-muted);
}

.services-panel__chosen strong {
  font-weight: 700;
  color: var(--color-rose-dark);
}

.services-panel__cta--disabled {
  opacity: 0.45;
  pointer-events: none;
}

.services-cta {
  padding: clamp(2.5rem, 6vh, 4rem) 1rem;
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
  margin: 0 0 0.65rem;
  font-family: var(--font-display);
  font-size: clamp(1.65rem, 4vw, 2.15rem);
  font-weight: 400;
  color: #fff;
}

.services-cta p {
  margin: 0 0 1.5rem;
  font: 400 0.95rem/1.7 var(--font-body);
  color: rgba(255, 255, 255, 0.78);
}

.services-cta__actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (min-width: 640px) {
  .services-tabs {
    grid-template-columns: repeat(4, 1fr);
  }

  .services-panel__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .services-cta__actions {
    flex-direction: row;
    justify-content: center;
  }
}

@media (min-width: 768px) {
  .services-panel__inner {
    padding: 2rem 1.5rem 1.5rem;
  }

  .services-panel__intro {
    grid-template-columns: auto 1fr;
    gap: 2rem;
  }

  .services-panel__visual {
    margin: 0;
    width: 180px;
  }

  .services-panel__copy h2,
  .services-panel__text,
  .services-panel__hint {
    text-align: left;
  }
}

@media (min-width: 1024px) {
  .services-panel__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .services-panel {
    animation: none;
  }
}
</style>
