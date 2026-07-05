<template>
  <main class="home">
    <!-- Hero slider -->
    <section class="hero" @touchstart.passive="onHeroTouchStart" @touchend.passive="onHeroTouchEnd">
      <div class="hero__track">
        <article
          v-for="(slide, index) in heroSlides"
          :key="slide.image"
          class="hero__slide"
          :class="{ 'hero__slide--active': activeSlide === index }"
        >
          <img
            :src="slide.image"
            alt=""
            class="hero__bg"
            :class="{ 'hero__bg--zoom': activeSlide === index }"
            fetchpriority="high"
          />
          <div class="hero__overlay" />
          <div class="hero__content" :class="{ 'hero__content--in': activeSlide === index && heroReady }">
            <p class="hero__eyebrow">{{ slide.eyebrow }}</p>
            <h1 class="hero__title">{{ slide.title }}</h1>
            <p v-if="slide.subtitle" class="hero__subtitle">{{ slide.subtitle }}</p>
            <SiteButton :to="slide.ctaTo" variant="primary">{{ slide.cta }}</SiteButton>
          </div>
        </article>
      </div>
      <ol class="hero__pager">
        <li v-for="(_, index) in heroSlides" :key="index">
          <button
            type="button"
            :class="{ 'hero__pager-dot--active': activeSlide === index }"
            :aria-label="`Go to slide ${index + 1}`"
            @click="goToSlide(index)"
          >
            {{ index + 1 }}
          </button>
        </li>
      </ol>
    </section>

    <!-- Welcome -->
    <section id="welcome" class="welcome">
      <div class="welcome__inner">
        <ScrollReveal variant="left" class="welcome__media-wrap" immediate>
          <div class="welcome__media">
            <div class="welcome__mirror" aria-hidden="true">
              <img src="/images/welcome.jpg" alt="Spa treatment room with candles and warm lighting" class="welcome__photo" loading="lazy" />
            </div>
            <img src="/images/flower.png" alt="" class="welcome__flower" aria-hidden="true" loading="lazy" />
          </div>
        </ScrollReveal>
        <ScrollReveal variant="right" :delay="120" immediate>
          <div class="welcome__copy">
            <p class="label">Get to know us</p>
            <h2>Welcome to Shee Aesthetics</h2>
            <p class="welcome__text">
              Shee Aesthetics is a beauty therapy studio offering facials, waxing, massage, and makeup.
              Book online and pay by M-Pesa to confirm. We do not take appointments by phone.
            </p>
            <div class="welcome__offers">
              <NuxtLink to="/#packages" class="welcome__offer-btn">
                <img src="/images/icon-offer.png" alt="" width="46" height="46" />
                <div>
                  <h3>Special Offer</h3>
                  <p>Full packages on Tuesday and Wednesday. Facial, waxing, massage and makeup in one visit.</p>
                  <span class="welcome__offer-action">View packages</span>
                </div>
              </NuxtLink>
              <NuxtLink to="/#singles" class="welcome__offer-btn">
                <img src="/images/icon-gift.png" alt="" width="48" height="48" />
                <div>
                  <h3>Single Treatments</h3>
                  <p>Book one service on Mon, Thu, Fri and Sat when you only need a single session.</p>
                  <span class="welcome__offer-action">View singles</span>
                </div>
              </NuxtLink>
            </div>
            <SiteButton to="/#services" variant="primary">Discover More</SiteButton>
          </div>
        </ScrollReveal>
      </div>
    </section>

    <!-- Services -->
    <section id="services" class="services">
      <ScrollReveal variant="fade" immediate>
        <header class="section-head">
          <p class="label">Our Treatments</p>
          <h2>What We're Offering</h2>
        </header>
      </ScrollReveal>
      <div class="services__grid">
        <ScrollReveal
          v-for="(service, index) in services"
          :key="service.name"
          variant="up"
          :delay="index * 90"
        >
          <MellisServiceCard
            :name="service.name"
            :text="service.text"
            :image="service.image"
            :icon="service.icon"
          />
        </ScrollReveal>
      </div>
    </section>

    <!-- Full packages — after services for mobile booking flow -->
    <section id="packages" class="packages">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">Pricing Plans</p>
          <h2>Full Packages, Tuesday &amp; Wednesday</h2>
          <p class="section-head__sub">Package days only. Facial, waxing, massage and makeup in one private visit.</p>
        </header>
      </ScrollReveal>
      <div class="packages__grid">
        <ScrollReveal
          v-for="(pkg, index) in packages"
          :key="pkg.name"
          variant="up"
          :delay="index * 90"
        >
          <MellisPackageCard
            :name="pkg.name"
            :text="pkg.text"
            :price="pkg.price"
            :includes="pkg.includes"
            :featured="pkg.featured"
            :badge="pkg.badge"
            :days-label="pkg.daysLabel"
            :cta-label="pkg.ctaLabel"
          />
        </ScrollReveal>
      </div>
    </section>

    <!-- Single treatments -->
    <section id="singles" class="packages packages--singles">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">Single Treatments</p>
          <h2>Book One Service at a Time</h2>
          <p class="section-head__sub">Mon, Thu–Sat. Pick a facial, wax, massage or makeup when you only need one.</p>
        </header>
      </ScrollReveal>
      <div class="packages__grid packages__grid--singles">
        <ScrollReveal
          v-for="(treatment, index) in singleTreatments"
          :key="treatment.name"
          variant="up"
          :delay="index * 80"
        >
          <MellisPackageCard
            :name="treatment.name"
            :text="treatment.text"
            :price="treatment.price"
            :includes="treatment.includes"
            :days-label="treatment.daysLabel"
            :cta-label="treatment.ctaLabel"
          />
        </ScrollReveal>
      </div>
    </section>

    <!-- How it works — Mellis flow -->
    <section class="steps">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">3 easy steps</p>
          <h2>How It Works?</h2>
        </header>
      </ScrollReveal>
      <div class="steps__flow">
        <ScrollReveal
          v-for="(step, index) in flowSteps"
          :key="step.title"
          variant="up"
          :delay="index * 100"
        >
          <MellisFlowStep
            :num="step.num"
            :title="step.title"
            :text="step.text"
            :image="step.image"
          />
        </ScrollReveal>
      </div>
    </section>

    <!-- More we do -->
    <section class="more">
      <div class="more__bg" aria-hidden="true">
        <img src="/images/more-bg.jpg" alt="" loading="lazy" />
        <div class="more__bg-overlay" />
      </div>
      <div class="more__inner">
        <ScrollReveal variant="left">
          <div class="more__panel">
            <p class="label">What else we do</p>
            <h2>Get an Incredible Spa Experience at Shee Aesthetics</h2>
            <ul class="more__list">
              <li v-for="item in serviceList" :key="item">{{ item }}</li>
            </ul>
            <SiteButton to="/book" variant="primary" class="more__cta">Just Book</SiteButton>
            <p class="more__hint">Prices are listed above. You pay at checkout to confirm.</p>
          </div>
        </ScrollReveal>
        <div class="more__stats">
          <ScrollReveal
            v-for="(stat, index) in stats"
            :key="stat.label"
            variant="scale"
            :delay="index * 80"
          >
            <article class="stat-card">
              <img :src="stat.icon" alt="" width="48" height="48" loading="lazy" />
              <span class="stat-card__num">{{ stat.value }}</span>
              <span class="stat-card__label">{{ stat.label }}</span>
            </article>
          </ScrollReveal>
        </div>
      </div>
    </section>

    <!-- Testimonials -->
    <section class="reviews">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">Customer Reviews</p>
          <h2>What They're Talking About Shee Aesthetics</h2>
          <p class="section-head__sub">Feedback from clients who book facials, waxing, massage and makeup with us.</p>
        </header>
      </ScrollReveal>
      <div class="reviews__grid">
        <ScrollReveal
          v-for="(review, index) in reviews"
          :key="review.name"
          variant="up"
          :delay="index * 100"
        >
          <blockquote class="review-card">
            <img src="/images/quote.png" alt="" class="review-card__quote" aria-hidden="true" />
            <div class="review-card__stars" aria-label="5 out of 5 stars">★★★★★</div>
            <p>{{ review.text }}</p>
            <footer>
              <span class="review-card__avatar" aria-hidden="true">{{ review.initials }}</span>
              <div>
                <cite>{{ review.name }}</cite>
                <span>Customer</span>
              </div>
            </footer>
          </blockquote>
        </ScrollReveal>
      </div>
    </section>

    <!-- Gallery -->
    <section id="gallery" class="gallery">
      <ScrollReveal variant="fade">
        <header class="section-head section-head--light">
          <p class="label">Follow us on Instagram</p>
          <h2>@shee_aesthetics</h2>
        </header>
      </ScrollReveal>
      <div class="gallery__grid">
        <ScrollReveal
          v-for="(img, index) in galleryImages"
          :key="index"
          variant="scale"
          :delay="index * 60"
        >
          <a href="#" class="gallery__item">
            <img :src="img" alt="Shee Aesthetics studio photo" loading="lazy" />
          </a>
        </ScrollReveal>
      </div>
    </section>

    <!-- Hours CTA -->
    <section class="cta">
      <div class="cta__photo">
        <img src="/images/cta-bg.jpg" alt="" loading="lazy" />
        <div class="cta__overlay" />
      </div>
      <div class="cta__inner">
        <ScrollReveal variant="left">
          <div class="cta__book">
            <h2>Our Spa Center is the True Splendor</h2>
            <SiteButton to="/book" variant="primary">Book Now</SiteButton>
          </div>
        </ScrollReveal>
        <ScrollReveal variant="right" :delay="120">
          <div class="cta__hours">
            <img src="/images/icon-clock.png" alt="" width="40" height="40" />
            <p class="label">Opening Hours</p>
            <div class="cta__hours-grid">
              <div>
                <h3>Monday</h3>
                <p>9:00 am – 6:00 pm</p>
              </div>
              <div>
                <h3>Tue &amp; Wed</h3>
                <p>Full packages only</p>
              </div>
              <div>
                <h3>Thu – Sat</h3>
                <p>8:00 am – 7:00 pm</p>
              </div>
              <div>
                <h3>Sunday</h3>
                <p>Closed</p>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>

    <!-- Blog -->
    <section class="blog">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">Blog Posts</p>
          <h2>Latest News &amp; Articles</h2>
        </header>
      </ScrollReveal>
      <div class="blog__grid">
        <ScrollReveal
          v-for="(post, index) in blogPosts"
          :key="post.title"
          variant="up"
          :delay="index * 90"
        >
          <article class="blog-card">
            <a href="#" class="blog-card__image">
              <img :src="post.image" :alt="post.title" loading="lazy" />
            </a>
            <div class="blog-card__body">
              <h3><a href="#">{{ post.title }}</a></h3>
              <p>{{ post.excerpt }}</p>
              <a href="#" class="blog-card__link">Read More</a>
            </div>
          </article>
        </ScrollReveal>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import {
  flowSteps,
  heroSlides,
  packages,
  singleTreatments,
} from '@/landing/landingContent'

const activeSlide = ref(0)
const heroReady = ref(true)
let timer: ReturnType<typeof setInterval> | null = null
let heroTouchStartX = 0

function onHeroTouchStart(e: TouchEvent) {
  heroTouchStartX = e.changedTouches[0]?.clientX ?? 0
}

function onHeroTouchEnd(e: TouchEvent) {
  const endX = e.changedTouches[0]?.clientX ?? 0
  const delta = heroTouchStartX - endX
  if (Math.abs(delta) < 48) return
  if (delta > 0) {
    activeSlide.value = (activeSlide.value + 1) % heroSlides.length
  } else {
    activeSlide.value = (activeSlide.value - 1 + heroSlides.length) % heroSlides.length
  }
  resetTimer()
}

function goToSlide(index: number) {
  activeSlide.value = index
  resetTimer()
}

function resetTimer() {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    activeSlide.value = (activeSlide.value + 1) % heroSlides.length
  }, 5000)
}

watch(activeSlide, () => {
  heroReady.value = false
  requestAnimationFrame(() => {
    heroReady.value = true
  })
})

onMounted(() => {
  heroReady.value = true
  resetTimer()
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

const services = [
  {
    name: 'Facial Care',
    text: 'Deep cleanse, exfoliation and hydration tailored to your skin type.',
    image: '/images/service-facial.jpg',
    icon: '/images/icon-facial.png',
  },
  {
    name: 'Massages',
    text: 'Swedish and deep tissue massage to release tension in back, neck and shoulders.',
    image: '/images/service-massage.jpg',
    icon: '/images/icon-massage.png',
  },
  {
    name: 'Waxing',
    text: 'Face and body waxing with hot wax. Brows, underarms, legs and bikini.',
    image: '/images/service-waxing.jpg',
    icon: '/images/icon-waxing.png',
  },
  {
    name: 'Makeup',
    text: 'Everyday makeup and full glam for weddings, events and photo shoots.',
    image: '/images/service-makeup.jpg',
    icon: '/images/icon-makeup.png',
  },
]

const serviceList = [
  'Deep Cleansing Facials',
  'Hot Stone Massage',
  'Full Body Waxing',
  'Bridal Makeup',
  'Back & Shoulder Massage',
  'Brow Shaping',
  'Skin Brightening',
  'Event Glam',
]

const stats = [
  { value: '5+', label: 'Years Experience', icon: '/images/icon-counter-1.png' },
  { value: '4', label: 'Core Services', icon: '/images/icon-counter-2.png' },
  { value: '500+', label: 'Happy Clients', icon: '/images/icon-counter-3.png' },
  { value: '6', label: 'Days Open Weekly', icon: '/images/icon-counter-4.png' },
]

const reviews = [
  {
    name: 'Wanjiku M.',
    initials: 'WM',
    text: 'I come every month for a facial. My skin has improved and the room is always clean and quiet.',
  },
  {
    name: 'Sharon O.',
    initials: 'SO',
    text: 'Had my makeup done for a wedding. It stayed on all day and looked good in every photo.',
  },
  {
    name: 'Diana K.',
    initials: 'DK',
    text: 'The Saturday massage is something I look forward to each week. Easy to book and always on time.',
  },
]

const galleryImages = [
  '/images/gallery-1.jpg',
  '/images/gallery-2.jpg',
  '/images/gallery-3.jpg',
  '/images/gallery-4.jpg',
  '/images/gallery-5.jpg',
  '/images/gallery-6.jpg',
]

const blogPosts = [
  {
    title: 'How to prepare for your first facial',
    excerpt: 'What to do before your appointment and what to expect during a 60-minute facial.',
    image: '/images/blog-1.jpg',
  },
  {
    title: '5 tips for long-lasting event makeup',
    excerpt: 'Simple steps to keep your makeup fresh from morning through to the end of the night.',
    image: '/images/blog-2.jpg',
  },
  {
    title: 'Why we only do full packages on Tue & Wed',
    excerpt: 'How blocking two days for packages gives every client enough time and attention.',
    image: '/images/blog-3.jpg',
  },
]

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Shee Aesthetics | Facials, Waxing, Massage & Makeup',
  meta: [
    {
      name: 'description',
      content: 'Shee Aesthetics. Facials, waxing, massage and makeup. Full packages Tue and Wed. Single treatments Mon, Thu to Sat.',
    },
  ],
})
</script>

<style scoped>
.home {
  background: var(--color-paper);
  margin: 0;
  padding: 0;
}

.label {
  margin: 0 0 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font: 600 0.72rem var(--font-body);
  color: var(--color-rose);
}

.section-head {
  width: var(--container);
  margin: 0 auto 2rem;
  text-align: center;
  padding: 0 0.25rem;
}

.section-head h2 {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 4vw, 2.65rem);
  font-weight: 400;
  line-height: 1.25;
}

.section-head__sub {
  max-width: 52ch;
  margin: 1rem auto 0;
  font: 400 1rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.section-head--light .label,
.section-head--light h2 {
  color: #fff;
}

/* Hero — mobile-first */
.hero {
  position: relative;
  height: min(72svh, 520px);
  min-height: 420px;
  overflow: hidden;
  touch-action: pan-y;
}

.hero__track {
  height: 100%;
  position: relative;
}

.hero__slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 1.1s var(--ease-story), visibility 1.1s;
}

.hero__slide--active {
  opacity: 1;
  visibility: visible;
  z-index: 1;
}

.hero__bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.08);
  transition: transform 7s linear;
}

.hero__bg--zoom {
  transform: scale(1);
}

.hero__overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(39, 37, 42, 0.35), rgba(39, 37, 42, 0.55));
}

.hero__content {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 1.5rem 1.25rem 3.5rem;
  color: #fff;
  opacity: 0;
  transform: translateY(24px);
  transition:
    opacity 0.9s var(--ease-story) 0.15s,
    transform 0.9s var(--ease-story) 0.15s;
}

.hero__content--in {
  opacity: 1;
  transform: translateY(0);
}

.hero__eyebrow {
  margin: 0 0 0.5rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

.hero__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-script);
  font-size: clamp(2.65rem, 13vw, 8rem);
  font-weight: 400;
  line-height: 1;
  color: #fff;
}

.hero__subtitle {
  max-width: 36ch;
  margin: 0 0 1.75rem;
  font: 400 1rem/1.65 var(--font-body);
  color: rgba(255, 255, 255, 0.88);
}

.hero__pager {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
  z-index: 3;
}

.hero__pager button {
  width: 44px;
  height: 44px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: transparent;
  color: #fff;
  font: 600 0.8rem var(--font-body);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: background 0.3s, border-color 0.3s, transform 0.3s;
}

.hero__pager button:hover {
  transform: translateY(-2px);
  border-color: #fff;
}

.hero__pager-dot--active {
  background: var(--color-rose) !important;
  border-color: var(--color-rose) !important;
}

/* Welcome — mobile-first single column */
.welcome {
  padding: clamp(3rem, 8vh, 6.5rem) 1rem;
}

.welcome__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}

.welcome__media-wrap,
.welcome__copy {
  height: 100%;
}

.welcome__media {
  position: relative;
  display: flex;
  justify-content: center;
}

.welcome__mirror {
  position: relative;
  width: min(260px, 68vw);
  aspect-ratio: 1;
  margin: 0 auto;
  padding: 6px;
  border-radius: 50%;
  background: linear-gradient(145deg, var(--color-rose-soft), #fff 45%, var(--color-rose-soft));
  box-shadow:
    0 0 0 1px rgba(222, 150, 141, 0.35),
    0 16px 48px rgba(39, 37, 42, 0.12);
}

.welcome__photo {
  width: 100%;
  height: 100%;
  display: block;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
}

.welcome__flower {
  position: absolute;
  right: max(-0.25rem, calc(50% - 150px));
  bottom: 0.5rem;
  z-index: 2;
  width: min(100px, 28%);
  pointer-events: none;
}

.welcome__offers {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
}

.welcome__copy h2 {
  margin: 0 0 1.25rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.5vw, 2.5rem);
  font-weight: 400;
  line-height: 1.25;
}

.welcome__text {
  margin: 0 0 1.5rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.welcome__offer-btn {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  width: 100%;
  padding: 1.15rem 1.25rem;
  border: 1px solid var(--color-line);
  border-left: 3px solid var(--color-rose);
  background: #fff;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  transition:
    transform 0.35s var(--ease-story),
    border-color 0.35s,
    box-shadow 0.35s;
  -webkit-tap-highlight-color: transparent;
}

.welcome__offer-btn:hover {
  transform: translateY(-2px);
  border-color: var(--color-rose);
  box-shadow: 0 10px 28px rgba(39, 37, 42, 0.08);
}

.welcome__offer-btn:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.welcome__offer-btn h3 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-ink);
}

.welcome__offer-btn p {
  margin: 0;
  font: 400 0.88rem/1.55 var(--font-body);
  color: var(--color-muted);
}

.welcome__offer-action {
  display: inline-block;
  margin-top: 0.65rem;
  font: 600 0.72rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
}

/* Services — Mellis open grid, no boxed cards */
.services {
  padding: clamp(2.5rem, 7vh, 5rem) 1rem clamp(3.5rem, 9vh, 6.5rem);
  background: var(--color-paper);
}

.services__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}

/* More — standout band with visible spa photo */
.more {
  position: relative;
  padding: clamp(3.5rem, 9vh, 6.5rem) 1rem;
  overflow: hidden;
  border-top: 4px solid var(--color-rose);
  border-bottom: 4px solid var(--color-rose);
}

.more__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.more__bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
}

.more__bg-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    rgba(252, 245, 245, 0.97) 0%,
    rgba(255, 255, 255, 0.9) 42%,
    rgba(39, 37, 42, 0.45) 100%
  );
}

.more__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
}

.more__panel {
  background: #fff;
  border-left: 4px solid var(--color-rose);
  padding: clamp(1.75rem, 4vw, 2.5rem);
  box-shadow: 0 24px 64px rgba(39, 37, 42, 0.14);
  max-width: 34rem;
}

.more__panel h2 {
  margin: 0 0 1.5rem;
  font-family: var(--font-display);
  font-size: clamp(1.9rem, 4.5vw, 2.55rem);
  font-weight: 400;
  line-height: 1.2;
  color: var(--color-ink);
}

.more__cta {
  width: 100%;
  max-width: 16rem;
}

.more__hint {
  margin: 1rem 0 0;
  font: 500 0.8rem/1.5 var(--font-body);
  color: var(--color-muted);
  letter-spacing: 0.02em;
}

.more__list {
  columns: 1;
  column-gap: 2rem;
  list-style: none;
  margin: 0 0 1.5rem;
  padding: 0;
}

.more__list li {
  position: relative;
  padding-left: 1.1rem;
  margin-bottom: 0.85rem;
  font: 500 0.92rem var(--font-body);
  break-inside: avoid;
}

.more__list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-rose);
}

.more__stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.stat-card {
  background: #fff;
  padding: 1.5rem 1.25rem;
  text-align: center;
  border: 1px solid rgba(222, 150, 141, 0.25);
  box-shadow: 0 12px 36px rgba(39, 37, 42, 0.1);
  height: 100%;
  transition: transform 0.4s var(--ease-story), box-shadow 0.4s;
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(39, 37, 42, 0.1);
}

.stat-card img {
  margin: 0 auto 1rem;
  display: block;
}

.stat-card__num {
  display: block;
  font: 700 2.5rem/1 var(--font-display);
  color: var(--color-ink);
}

.stat-card__label {
  display: block;
  margin-top: 0.5rem;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-muted);
}

/* Steps — Mellis circle flow */
.steps {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
  background: var(--color-paper);
}

.steps__flow {
  position: relative;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
  padding-top: 0.5rem;
}

.steps__flow::before {
  display: none;
}

/* Packages */
.packages {
  padding: clamp(2.5rem, 8vh, 6rem) 1rem;
  background: var(--color-paper);
}

.packages__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
  align-items: stretch;
  padding-top: 0.5rem;
}

.packages--singles {
  background: var(--color-cream);
}

.packages__grid--singles {
  grid-template-columns: 1fr;
}

/* Reviews */
.reviews {
  padding: clamp(2.5rem, 8vh, 6rem) 1rem;
}

.reviews__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.review-card {
  margin: 0;
  padding: 1.75rem 1.5rem;
  background: var(--color-cream);
  position: relative;
  height: 100%;
  transition: transform 0.4s var(--ease-story), box-shadow 0.4s;
}

.review-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(39, 37, 42, 0.08);
}

.review-card__quote {
  width: 36px;
  margin-bottom: 1rem;
  opacity: 0.35;
}

.review-card__stars {
  color: var(--color-rose);
  font-size: 0.85rem;
  letter-spacing: 0.15em;
  margin-bottom: 1rem;
}

.review-card p {
  margin: 0 0 1.75rem;
  font: 400 0.92rem/1.7 var(--font-body);
  color: var(--color-muted);
}

.review-card footer {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.review-card__avatar {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.8rem var(--font-body);
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.review-card cite {
  display: block;
  font: 700 0.95rem var(--font-display);
  font-style: normal;
  color: var(--color-ink);
}

.review-card footer span {
  font: 400 0.82rem var(--font-body);
  color: var(--color-muted);
}

/* Gallery */
.gallery {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
  background: var(--color-footer);
}

.gallery__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.35rem;
}

.gallery__item {
  display: block;
  aspect-ratio: 1;
  overflow: hidden;
}

.gallery__item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-story), filter 0.5s;
}

.gallery__item:hover img {
  transform: scale(1.08);
  filter: brightness(1.05);
}

/* CTA */
.cta {
  position: relative;
  padding: clamp(4rem, 9vh, 6.5rem) 1.5rem;
  overflow: hidden;
}

.cta__photo {
  position: absolute;
  inset: 0;
}

.cta__photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.05);
  animation: cta-kenburns 18s ease-in-out infinite alternate;
}

.cta__overlay {
  position: absolute;
  inset: 0;
  background: rgba(39, 37, 42, 0.82);
}

.cta__inner {
  position: relative;
  z-index: 1;
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  align-items: center;
  color: #fff;
}

.cta__book h2 {
  margin: 0 0 2rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.5vw, 2.65rem);
  font-weight: 400;
  line-height: 1.25;
  color: #fff;
  max-width: 16ch;
}

.cta__hours .label {
  color: var(--color-rose);
}

.cta__hours-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.cta__hours-grid h3 {
  margin: 0 0 0.25rem;
  font: 700 0.95rem var(--font-body);
  color: #fff;
}

.cta__hours-grid p {
  margin: 0;
  font: 400 0.88rem var(--font-body);
  color: rgba(255, 255, 255, 0.75);
}

@keyframes cta-kenburns {
  from {
    transform: scale(1.05);
  }
  to {
    transform: scale(1.12);
  }
}

/* Blog */
.blog {
  padding: clamp(2.5rem, 7vh, 5rem) 1rem clamp(2rem, 4vh, 3rem);
}

.blog__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.25rem;
}

.blog-card {
  height: 100%;
  transition: transform 0.4s var(--ease-story);
}

.blog-card:hover {
  transform: translateY(-6px);
}

.blog-card__image {
  display: block;
  overflow: hidden;
}

.blog-card__image img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
  transition: transform 0.55s var(--ease-story);
}

.blog-card:hover .blog-card__image img {
  transform: scale(1.06);
}

.blog-card__body {
  padding: 1.5rem 0 0;
}

.blog-card h3 {
  margin: 0 0 0.75rem;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
}

.blog-card h3 a {
  text-decoration: none;
  color: var(--color-ink);
  transition: color 0.25s;
}

.blog-card h3 a:hover {
  color: var(--color-rose);
}

.blog-card p {
  margin: 0 0 1rem;
  font: 400 0.9rem/1.65 var(--font-body);
  color: var(--color-muted);
}

.blog-card__link {
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  text-decoration: none;
  color: var(--color-rose);
  transition: letter-spacing 0.25s;
}

.blog-card__link:hover {
  letter-spacing: 0.16em;
}

/* Tablet and up — progressive enhancement */
@media (min-width: 640px) {
  .welcome__offers {
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .cta__hours-grid {
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }

  .gallery__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 768px) {
  .hero {
    height: min(78svh, 640px);
    min-height: 480px;
  }

  .hero__content {
    padding: 2rem 1.5rem 4rem;
  }

  .hero__eyebrow {
    font-size: 0.85rem;
    letter-spacing: 0.32em;
  }

  .section-head {
    margin-bottom: 3rem;
  }

  .welcome {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .welcome__inner {
    gap: clamp(2rem, 5vw, 4.5rem);
  }

  .welcome__mirror {
    width: min(320px, 42vw);
  }

  .welcome__flower {
    right: -1rem;
    width: min(130px, 30%);
  }

  .services,
  .reviews,
  .packages {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .services__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  .packages__grid,
  .packages__grid--singles {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .reviews__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
  }

  .review-card {
    padding: 2rem 1.75rem;
  }

  .blog__grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .more__inner {
    grid-template-columns: 1.15fr 1fr;
    gap: 3rem;
  }

  .more__cta {
    width: auto;
  }

  .more__list {
    columns: 2;
    margin-bottom: 2rem;
  }

  .cta__inner {
    grid-template-columns: 1fr 1fr;
    gap: 3rem;
  }
}

@media (min-width: 1024px) {
  .hero {
    height: min(726px, 88vh);
    min-height: 500px;
  }

  .welcome__inner {
    grid-template-columns: 1fr 1fr;
  }

  .services__grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .steps__flow {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  .steps__flow::before {
    content: '';
    display: block;
    position: absolute;
    top: 100px;
    left: 18%;
    right: 18%;
    height: 2px;
    background: var(--color-rose-soft);
    z-index: 0;
  }

  .packages__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.75rem;
  }

  .packages__grid--singles {
    grid-template-columns: repeat(4, 1fr);
  }

  .reviews__grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }

  .gallery__grid {
    grid-template-columns: repeat(6, 1fr);
  }

  .blog__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .hero__slide,
  .hero__bg,
  .hero__content,
  .cta__photo img,
  .stat-card,
  .package-card,
  .review-card,
  .blog-card {
    animation: none !important;
    transition: none !important;
  }

  .hero__bg,
  .hero__bg--zoom {
    transform: none;
  }
}
</style>
