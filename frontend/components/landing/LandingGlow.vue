<template>
  <!-- Get to know us — content first on mobile; Mellis oval left on desktop -->
  <section id="behind-the-glow" class="glow home-section" aria-labelledby="glow-heading">
    <div class="glow__inner">
      <div class="glow__copy">
        <p class="glow__eyebrow">{{ GLOW_SECTION_EYEBROW }}</p>
        <h2 id="glow-heading" class="glow__heading">{{ GLOW_SECTION_HEADING }}</h2>
        <p class="glow__text">{{ GLOW_SECTION_TEXT }}</p>
        <p class="glow__artist">
          <span class="glow__name">{{ GLOW_ARTIST_NAME }}</span>
          <span class="glow__line">{{ GLOW_ARTIST_LINE }}</span>
        </p>
        <a
          class="glow__continue"
          :href="GLOW_CONTINUE_HASH"
          @click="scrollToGlowWork"
        >
          {{ GLOW_CONTINUE_LABEL }}
        </a>
      </div>
      <div class="glow__media">
        <div class="glow__flower-sketch" aria-hidden="true">
          <svg viewBox="0 0 240 280" fill="none" xmlns="http://www.w3.org/2000/svg" class="glow__flower-svg">
            <path d="M120 270 C110 210 95 160 75 110 C65 85 45 60 20 40 C38 65 50 95 55 130 C60 165 65 210 70 270" stroke="#c88478" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" opacity="0.65"/>
            <path d="M115 200 C140 180 175 170 210 165 C180 185 150 210 125 240" stroke="#c88478" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
            <path d="M80 120 C65 90 85 60 115 40 C105 70 95 98 80 120 Z" stroke="#c88478" stroke-width="1.5" fill="rgba(230, 165, 152, 0.15)" stroke-linecap="round" opacity="0.7"/>
            <path d="M115 40 C140 22 180 28 200 58 C170 65 140 82 115 105 C110 82 112 58 115 40 Z" stroke="#c88478" stroke-width="1.5" fill="rgba(230, 165, 152, 0.18)" stroke-linecap="round" opacity="0.7"/>
            <path d="M80 120 C50 128 25 150 10 180 C32 168 60 156 90 148" stroke="#c88478" stroke-width="1.5" stroke-linecap="round" opacity="0.55"/>
            <circle cx="110" cy="72" r="3.5" fill="#c88478" opacity="0.75"/>
            <circle cx="128" cy="60" r="3" fill="#c88478" opacity="0.75"/>
            <circle cx="142" cy="78" r="3" fill="#c88478" opacity="0.75"/>
          </svg>
        </div>
        <div class="glow__accent-circle" aria-hidden="true" />
        <figure class="glow__mirror">
          <img
            src="/images/therapist.png"
            alt="Shee, beauty artist and founder at Shee Aesthetics"
            class="glow__photo"
            loading="lazy"
            decoding="async"
            width="480"
            height="600"
          />
        </figure>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import {
  GLOW_SECTION_EYEBROW,
  GLOW_SECTION_HEADING,
  GLOW_SECTION_TEXT,
  GLOW_ARTIST_NAME,
  GLOW_ARTIST_LINE,
  GLOW_CONTINUE_LABEL,
  GLOW_CONTINUE_HASH,
} from '@/landing/landingContent'

function scrollToGlowWork(event: Event) {
  event.preventDefault()
  const el = document.getElementById('our-work')
  if (!el) return
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' })
  if (import.meta.client) {
    window.history.replaceState(null, '', '#our-work')
  }
}
</script>

<style scoped>
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

/* Get to know us — content-first mobile; Mellis oval frame; desktop image-left */
.glow {
  position: relative;
  z-index: 1;
  margin-top: -1px;
  padding: clamp(1.75rem, 5vw, 3.25rem) 1rem clamp(1.5rem, 4vw, 2.5rem);
  overflow: hidden;
  background: var(--color-paper);
}

.glow__inner {
  width: var(--container);
  max-width: 64rem;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.65rem;
  align-items: center;
  justify-items: center;
  text-align: center;
}

.glow__copy {
  min-width: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  order: 1;
}

.glow__media {
  position: relative;
  width: min(100%, 22rem);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  order: 2;
}

.glow__flower-sketch {
  position: absolute;
  left: -18%;
  bottom: -6%;
  width: clamp(7.5rem, 42%, 10.5rem);
  pointer-events: none;
  z-index: 0;
  opacity: 0.9;
}

.glow__flower-svg {
  width: 100%;
  height: auto;
  display: block;
}

.glow__accent-circle {
  position: absolute;
  right: -8%;
  bottom: -4%;
  width: clamp(5.5rem, 32%, 7.5rem);
  aspect-ratio: 1;
  border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, #f7d8d0 0%, #e8a99d 68%, #d89689 100%);
  box-shadow: 0 10px 28px rgba(216, 150, 137, 0.28);
  z-index: 1;
  pointer-events: none;
}

/* Mellis Theme vertical oval — soft frame, white rim, botanical accents */
.glow__mirror {
  position: relative;
  z-index: 2;
  margin: 0;
  width: min(100%, 22rem);
  aspect-ratio: 4 / 5;
  padding: 0;
  border-radius: 50% / 46%;
  overflow: hidden;
  background: #ebe4de;
  border: 4px solid #fff;
  box-shadow:
    0 18px 42px rgba(39, 37, 42, 0.16),
    0 0 0 1px rgba(222, 150, 141, 0.22);
}

.glow__photo {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  object-position: center 16%;
  border-radius: 50% / 46%;
  background: #ebe4de;
}

.glow__eyebrow {
  margin: 0 0 0.45rem;
  font: 700 0.68rem/1.3 var(--font-body);
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.glow__heading {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 5.5vw, 2.35rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.glow__text {
  margin: 0.7rem auto 0;
  max-width: 36ch;
  font: 400 0.95rem/1.6 var(--font-body);
  color: var(--color-muted);
}

.glow__artist {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  margin: 0.95rem 0 0;
}

.glow__name {
  font-family: var(--font-script);
  font-size: clamp(1.55rem, 4vw, 1.95rem);
  font-weight: 400;
  line-height: 1.05;
  color: var(--color-rose-dark, #b56b62);
}

.glow__line {
  font: 600 0.7rem/1.35 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.glow__continue {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-top: 1.1rem;
  min-height: 2.75rem;
  min-width: 11rem;
  padding: 0.65rem 1.4rem;
  font: 700 0.7rem/1 var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  text-decoration: none;
  color: #fff;
  background: var(--color-rose);
  transition: background 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.glow__continue:hover,
.glow__continue:focus-visible {
  background: var(--color-rose-dark, #b56b62);
  outline: none;
}

.glow__continue:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 3px;
}

@media (min-width: 900px) {
  .glow {
    padding: clamp(2.25rem, 4.5vw, 3.5rem) 1.5rem clamp(1.75rem, 3.5vw, 2.75rem);
  }

  .glow__inner {
    grid-template-columns: 24rem minmax(0, 1fr);
    gap: clamp(2rem, 4vw, 3.5rem);
    justify-items: start;
    text-align: left;
    align-items: center;
  }

  /* Desktop: Mellis oval left, story right */
  .glow__media {
    order: 1;
    width: 24rem;
    margin: 0;
  }

  .glow__copy {
    order: 2;
    align-items: flex-start;
    text-align: left;
  }

  .glow__mirror {
    width: 24rem;
  }

  .glow__flower-sketch {
    left: -22%;
    bottom: -8%;
    width: 11.5rem;
  }

  .glow__accent-circle {
    width: 8rem;
    right: -12%;
    bottom: -6%;
  }

  .glow__text {
    margin-left: 0;
    margin-right: 0;
    max-width: 38ch;
  }

  .glow__artist {
    align-items: flex-start;
  }

  .glow__heading {
    font-size: clamp(2rem, 2.6vw, 2.55rem);
  }
}
</style>
