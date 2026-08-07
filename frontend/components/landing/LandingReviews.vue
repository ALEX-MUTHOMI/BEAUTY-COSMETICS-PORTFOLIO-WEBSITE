<template>
  <!-- Client reviews — Mellis-style proof cards (no reviewer photos) -->
  <section class="reviews home-section home-floral" aria-labelledby="reviews-heading">
    <img
      src="/images/flower-edge.png"
      alt=""
      class="home-floral__edge home-floral__edge--tl"
      width="160"
      height="130"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
    <img
      src="/images/flower-edge.png"
      alt=""
      class="home-floral__edge home-floral__edge--br"
      width="180"
      height="145"
      loading="lazy"
      decoding="async"
      aria-hidden="true"
    />
    <div class="reviews__inner">
      <ScrollReveal variant="up">
        <header class="reviews__head">
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
            <h2 id="reviews-heading">What clients say</h2>
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

      <div class="reviews__grid">
        <ScrollReveal
          v-for="(review, index) in reviews"
          :key="review.name"
          variant="up"
          :delay="70 + index * 80"
        >
          <blockquote class="review-card">
            <div class="review-card__top">
              <div class="review-card__stars" aria-label="5 out of 5 stars">★★★★★</div>
              <span class="review-card__quote" aria-hidden="true">”</span>
            </div>
            <p class="review-card__text">{{ review.text }}</p>
            <footer class="review-card__footer">
              <cite class="review-card__name">{{ review.name }}</cite>
              <span class="review-card__service">{{ review.visitLabel }}</span>
            </footer>
          </blockquote>
        </ScrollReveal>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { landingClientReviews } from '@/landing/landingContent'

const reviews = landingClientReviews
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

.home-floral__edge--tl {
  top: 0.45rem;
  left: 0.85rem;
  width: min(11rem, 34vw);
  transform: rotate(-14deg);
}

.home-floral > :not(.home-floral__edge) {
  position: relative;
  z-index: 1;
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

/* Reviews — quiet parchment + one soft corner orchid */
.reviews {
  position: relative;
  padding: clamp(2.5rem, 5.5vh, 3.5rem) 1rem;
  overflow: hidden;
  border-block: var(--home-seam);
  background: var(--color-parchment);
}

.reviews__inner {
  width: var(--container);
  margin: 0 auto;
}

.reviews__head {
  margin-bottom: 1.75rem;
  text-align: center;
}

.reviews__head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4vw, 2.65rem);
  font-weight: 500;
  line-height: 1.15;
  letter-spacing: -0.025em;
  color: var(--color-ink);
}

.reviews__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.15rem;
}

.reviews__grid > * {
  height: 100%;
  min-width: 0;
}

.review-card {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  margin: 0;
  padding: 1.45rem 1.3rem 1.35rem;
  background: var(--color-surface-raised);
  border: 1px solid rgba(176, 122, 113, 0.12);
  box-shadow: none;
  transition: transform 0.35s var(--ease-story, ease);
}

.review-card:hover {
  transform: translateY(-3px);
}

.review-card__top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.review-card__stars {
  color: var(--color-rose);
  font-size: 0.78rem;
  letter-spacing: 0.18em;
  line-height: 1;
}

.review-card__quote {
  font-family: var(--font-display);
  font-size: 3.25rem;
  line-height: 0.55;
  color: rgba(176, 122, 113, 0.28);
  user-select: none;
}

.review-card__text {
  flex: 1;
  margin: 0 0 1.15rem;
  font-family: var(--font-display);
  font-style: italic;
  font-weight: 400;
  font-size: 0.95rem;
  line-height: 1.65;
  color: var(--color-muted);
}

.review-card__footer {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(44, 44, 48, 0.08);
}

.review-card__name {
  font: 700 1.05rem/1.25 var(--font-display);
  font-style: normal;
  color: var(--color-ink);
}

.review-card__service {
  font: 600 0.72rem/1.35 var(--font-body);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-rose);
}

@media (min-width: 768px) {
  .reviews {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .reviews__head {
    margin-bottom: 2rem;
  }

  .reviews__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1.25rem;
  }

  .review-card {
    padding: 1.5rem 1.35rem 1.4rem;
  }
}

@media (min-width: 1024px) {
  .reviews__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.15rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .review-card {
    animation: none !important;
    transition: none !important;
  }
}
</style>
