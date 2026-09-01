<template>
  <!-- How it works — book → pay → visit (image-free, one layout all breakpoints) -->
  <section class="steps home-section home-floral">
    <!-- Soft edge orchids — transparent line art, visible but quiet -->
    <img
      src="/images/flower-edge.png"
      alt=""
      class="home-floral__edge home-floral__edge--bl"
      width="200"
      height="160"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
    <img
      src="/images/flower-edge.png"
      alt=""
      class="home-floral__edge home-floral__edge--br"
      width="200"
      height="160"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
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
          <h2>How booking works</h2>
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
    <ScrollReveal variant="up" :delay="120">
      <ol class="steps__compact" aria-label="Booking steps">
        <li v-for="step in flowSteps" :key="step.title">
          <span class="steps__compact-num" aria-hidden="true">{{ step.num }}</span>
          <div>
            <strong>{{ step.title }}</strong>
            <p>{{ step.text }}</p>
          </div>
        </li>
      </ol>
    </ScrollReveal>
  </section>
</template>

<script setup lang="ts">
import { flowSteps } from '@/landing/landingContent'
</script>

<style scoped>
.home-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;
  position: relative;
}

.home-floral {
  overflow: hidden;
}

.home-floral__edge {
  position: absolute;
  z-index: 0;
  pointer-events: none;
  user-select: none;
  width: min(11rem, 34vw);
  height: auto;
  opacity: 0.28;
  filter: saturate(0.95) contrast(1.02);
}

.home-floral__edge--br {
  right: 0.75rem;
  bottom: 0.35rem;
  transform: rotate(8deg);
}

.home-floral__edge--bl {
  left: 0.75rem;
  bottom: 0.35rem;
  width: min(13rem, 40vw);
  transform: rotate(-12deg) scaleX(-1);
}

.home-floral > :not(.home-floral__edge) {
  position: relative;
  z-index: 1;
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

/* Steps — quiet parchment + one soft edge orchid */
.steps {
  padding: var(--home-section-y-lg) 1.25rem;
  background: var(--color-parchment);
  border-block: var(--home-seam);
}

.steps__compact {
  list-style: none;
  width: var(--container);
  margin: 0 auto;
  padding: 0;
  display: grid;
  gap: 0.85rem;
}

.steps__compact li {
  display: grid;
  grid-template-columns: 2.5rem 1fr;
  gap: 0.85rem;
  align-items: start;
  height: 100%;
  padding: 1rem 1rem 1.05rem;
  background: var(--color-surface-raised);
  border: 1px solid rgba(176, 122, 113, 0.12);
  box-shadow: none;
}

.steps__compact-num {
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.04em;
}

.steps__compact strong {
  display: block;
  margin: 0.1rem 0 0.3rem;
  font-family: var(--font-display);
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-ink);
}

.steps__compact p {
  margin: 0;
  font: 400 0.88rem/1.5 var(--font-body);
  color: var(--color-muted);
}

@media (min-width: 768px) {
  .steps__compact {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.15rem;
  }

  .steps__compact li {
    grid-template-columns: 1fr;
    justify-items: start;
    gap: 0.75rem;
    padding: 1.35rem 1.25rem 1.4rem;
  }

  .steps__compact strong {
    font-size: 1.2rem;
  }

  .steps__compact p {
    font-size: 0.92rem;
  }
}

@media (min-width: 1024px) {
  .steps__compact {
    gap: 1.35rem;
  }

  .steps__compact li {
    padding: 1.5rem 1.4rem 1.55rem;
  }

  .steps__compact strong {
    font-size: 1.28rem;
  }
}
</style>
