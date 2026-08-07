<template>
  <!-- Our work — Pinterest masonry; primary proof for new clients -->
  <section id="our-work" class="work home-section">
    <ScrollReveal variant="up">
      <header class="section-head">
        <div class="title-lockup">
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--left"
            width="64"
            height="64"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
          <h2>Clients by Shee</h2>
          <img
            src="/images/flower.png"
            alt=""
            class="title-lockup__flower title-lockup__flower--right"
            width="64"
            height="64"
            loading="lazy"
            decoding="async"
            aria-hidden="true"
          />
        </div>
      </header>
    </ScrollReveal>
    <div class="work__masonry" aria-label="Shee client and studio work">
      <button
        v-for="(img, index) in workImages"
        :key="img.id"
        type="button"
        class="work__tile"
        :class="`work__tile--${img.shape}`"
        :aria-label="img.alt"
        @click="openWorkLightbox(img)"
      >
        <img
          :src="img.src"
          :alt="img.alt"
          class="work__photo"
          loading="lazy"
          decoding="async"
          :width="img.width"
          :height="img.height"
          :fetchpriority="index < 2 ? 'low' : 'auto'"
        />
      </button>
    </div>
    <ScrollReveal variant="fade" :delay="80">
      <p class="work__footer">
        <InstagramLink class="work__ig" />
      </p>
    </ScrollReveal>
  </section>

  <Teleport to="body">
    <div
      v-if="lightboxImage"
      class="work-lightbox"
      role="dialog"
      aria-modal="true"
      :aria-label="lightboxImage.alt"
      @click.self="closeWorkLightbox"
    >
      <button type="button" class="work-lightbox__close" aria-label="Close" @click="closeWorkLightbox">
        Close
      </button>
      <img
        :src="lightboxImage.src"
        :alt="lightboxImage.alt"
        class="work-lightbox__photo"
        width="1200"
        height="1600"
      />
      <p class="work-lightbox__caption">{{ lightboxImage.alt }}</p>
      <div class="work-lightbox__actions">
        <SiteButton
          v-if="primaryCtaIsExternal"
          :href="primaryCtaHref"
          variant="primary"
          @click="closeWorkLightbox"
        >
          Book this vibe
        </SiteButton>
        <SiteButton
          v-else
          :to="primaryCtaHref"
          variant="primary"
          @click="closeWorkLightbox"
        >
          Book this vibe
        </SiteButton>
        <InstagramLink variant="light" />
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { fetchHomeWorkGallery, STATIC_HOME_WORK, type HomeWorkImage } from '@/landing/homeWorkGallery'
import { useLandingContact } from '@/landing/useLandingContact'
import { primaryBookHref, primaryBookIsExternal } from '@/landing/primaryBookHref'
import { trackFunnelEvent } from '@/landing/funnelEvents'

const config = useRuntimeConfig()
const contact = useLandingContact()
const contactIsLive = contact.isLive
const whatsappUrl = contact.whatsappUrl

const { data: workGallery } = await useAsyncData(
  'home-work-gallery',
  () => fetchHomeWorkGallery(String(config.public.apiBaseUrl || '')),
  { default: () => STATIC_HOME_WORK },
)
const workImages = computed(() => (workGallery.value ?? STATIC_HOME_WORK).slice(0, 8))

const primaryCtaHref = computed(() =>
  primaryBookHref(new Date(), {
    contactIsLive: contactIsLive.value,
    whatsappUrl: whatsappUrl.value,
  }),
)
const primaryCtaIsExternal = computed(() => primaryBookIsExternal(primaryCtaHref.value))

const lightboxImage = ref<HomeWorkImage | null>(null)

function openWorkLightbox(img: HomeWorkImage) {
  lightboxImage.value = img
  trackFunnelEvent('gallery_open', { id: img.id })
}

function closeWorkLightbox() {
  lightboxImage.value = null
}
</script>

<style scoped>
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

.section-head {
  width: var(--container);
  margin: 0 auto var(--home-head-gap);
  text-align: center;
  padding: 0 0.25rem;
}

.title-lockup {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.65rem, 2.2vw, 1.15rem);
  max-width: 100%;
}

.title-lockup h2 {
  margin: 0;
  flex: 0 1 auto;
  min-width: 0;
}

.title-lockup__flower {
  width: clamp(2.85rem, 6.5vw, 3.85rem);
  height: auto;
  flex-shrink: 0;
  opacity: 0.78;
  pointer-events: none;
  user-select: none;
}

.title-lockup__flower--left {
  transform: scaleX(-1) rotate(-8deg);
}

.title-lockup__flower--right {
  transform: rotate(8deg);
}

@media (max-width: 479px) {
  .title-lockup__flower {
    width: clamp(1.55rem, 7.5vw, 2rem);
    opacity: 0.68;
  }

  .title-lockup {
    gap: 0.4rem;
  }

  .title-lockup h2 {
    font-size: clamp(1.55rem, 7.2vw, 1.95rem);
  }
}

.section-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.95rem, 4.2vw, 2.85rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

/* Our work — quiet paper; tight seam after Meet your therapist */
.work {
  padding: clamp(1.35rem, 3.5vw, 2.25rem) 1rem var(--home-section-y-lg);
  background: var(--color-paper);
  border-bottom: var(--home-seam);
  scroll-margin-top: calc(var(--site-header-height, 4rem) + 0.5rem);
}

.work__masonry {
  width: var(--container);
  margin: 0 auto;
  column-count: 2;
  column-gap: 0.65rem;
}

.work__tile {
  display: block;
  width: 100%;
  padding: 0;
  border: 0;
  break-inside: avoid;
  margin: 0 0 0.65rem;
  overflow: hidden;
  background: var(--color-cream);
  text-decoration: none;
  text-align: left;
  cursor: pointer;
  font: inherit;
  color: inherit;
  -webkit-tap-highlight-color: transparent;
}

.work__tile--tall .work__photo {
  aspect-ratio: 3 / 4;
}

.work__tile--wide .work__photo {
  aspect-ratio: 4 / 3;
}

.work__tile--square .work__photo {
  aspect-ratio: 1;
}

.work__photo {
  display: block;
  width: 100%;
  height: auto;
  object-fit: cover;
  transition: transform 0.7s var(--ease-story, cubic-bezier(0.22, 1, 0.36, 1));
}

@media (hover: hover) {
  .work__tile:hover .work__photo {
    transform: scale(1.04);
  }
}

.work__tile:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

.work__footer {
  width: var(--container);
  margin: 1.35rem auto 0;
  text-align: center;
}

.work__ig {
  margin-inline: auto;
}

@media (min-width: 768px) {
  .work {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .work__masonry {
    column-count: 3;
    column-gap: 0.85rem;
  }

  .work__tile {
    margin-bottom: 0.85rem;
  }
}

@media (min-width: 1024px) {
  .work__masonry {
    column-count: 4;
    column-gap: 1rem;
  }
}

.work-lightbox {
  position: fixed;
  inset: 0;
  z-index: 80;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
  padding: 1.25rem;
  background: rgba(20, 16, 18, 0.88);
}

.work-lightbox__photo {
  max-width: min(92vw, 28rem);
  max-height: 62vh;
  width: auto;
  height: auto;
  object-fit: contain;
}

.work-lightbox__caption {
  margin: 0;
  max-width: 28rem;
  color: rgba(255, 255, 255, 0.9);
  text-align: center;
  font: 500 0.92rem/1.4 var(--font-body);
}

.work-lightbox__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: center;
}

.work-lightbox__close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  min-height: 2.5rem;
  padding: 0.4rem 0.85rem;
  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 999px;
  background: transparent;
  color: #fff;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  cursor: pointer;
}
</style>
