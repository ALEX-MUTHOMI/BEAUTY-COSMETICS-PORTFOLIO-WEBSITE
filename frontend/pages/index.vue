<template>
  <main class="home">
    <!-- Hero slider -->
    <section class="hero">
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
            <SheeLogo to="/" variant="hero" size="lg" class="hero__brand" />
            <p class="hero__eyebrow">{{ slide.eyebrow }}</p>
            <h1 class="hero__title">{{ slide.title }}</h1>
            <p v-if="slide.subtitle" class="hero__subtitle">{{ slide.subtitle }}</p>
            <SiteButton to="/#packages" variant="primary">{{ slide.cta }}</SiteButton>
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
            <div class="welcome__accent" aria-hidden="true" />
            <img src="/images/welcome.jpg" alt="Client receiving a facial treatment" class="welcome__photo" loading="lazy" />
            <img src="/images/flower.png" alt="" class="welcome__flower" aria-hidden="true" loading="lazy" />
          </div>
        </ScrollReveal>
        <ScrollReveal variant="right" :delay="120" immediate>
          <div class="welcome__copy">
            <p class="label">Get to know us</p>
            <h2>Welcome to Shee Aesthetics</h2>
            <p class="welcome__text">
              Shee Aesthetics is a beauty therapy studio offering facials, waxing, massage, and makeup.
              Appointments are private, therapists are trained, and every service is done in a clean treatment room.
            </p>
            <div class="welcome__offers">
              <article class="welcome__offer welcome__offer--package">
                <span class="welcome__offer-badge">Must book</span>
                <img src="/images/icon-offer.png" alt="" width="46" height="46" />
                <div>
                  <h3>Tuesday &amp; Wednesday — Full Packages</h3>
                  <p>Our two package-only days. Facial, waxing, massage and makeup in one visit. Slots are limited — book early.</p>
                </div>
              </article>
              <article class="welcome__offer">
                <img src="/images/icon-gift.png" alt="" width="48" height="48" />
                <div>
                  <h3>Single Treatments</h3>
                  <p>One service at a time on Mon, Thu, Fri and Sat when you only need a facial, wax, massage or makeup session.</p>
                </div>
              </article>
            </div>
            <SiteButton to="/#packages" variant="primary">View Package Days</SiteButton>
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
          <article class="service-card">
            <div class="service-card__leaf" aria-hidden="true" />
            <div class="service-card__photo-wrap">
              <img :src="service.image" :alt="service.name" class="service-card__photo" loading="lazy" />
              <img :src="service.icon" alt="" class="service-card__icon" loading="lazy" />
            </div>
            <h3>{{ service.name }}</h3>
            <p>{{ service.text }}</p>
            <SiteButton to="/book" variant="text">Book Now</SiteButton>
          </article>
        </ScrollReveal>
      </div>
    </section>

    <!-- More we do -->
    <section class="more">
      <div class="more__inner">
        <ScrollReveal variant="left">
          <div class="more__copy">
            <p class="label">What else we do</p>
            <h2>Get an Incredible Spa Experience at Shee Aesthetics</h2>
            <ul class="more__list">
              <li v-for="item in serviceList" :key="item">{{ item }}</li>
            </ul>
            <SiteButton to="/book" variant="primary">Book Now</SiteButton>
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

    <!-- How it works -->
    <section class="steps">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">3 easy steps</p>
          <h2>How It Works?</h2>
        </header>
      </ScrollReveal>
      <div class="steps__grid">
        <ScrollReveal
          v-for="(step, index) in steps"
          :key="step.title"
          variant="up"
          :delay="index * 100"
        >
          <article class="step-card">
            <span class="step-card__num">{{ String(index + 1).padStart(2, '0') }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.text }}</p>
          </article>
        </ScrollReveal>
      </div>
    </section>

    <!-- Package days sell -->
    <section class="package-days" aria-labelledby="package-days-heading">
      <ScrollReveal variant="fade">
        <div class="package-days__inner">
          <p class="label">Limited — 2 days only</p>
          <h2 id="package-days-heading">{{ packageDayHeadline }}</h2>
          <p class="package-days__lead">{{ packageDaySubhead }}</p>
          <p class="package-days__urgency">{{ packageDayUrgency }}</p>
          <div class="package-days__chips" role="list">
            <span v-for="day in packageDays" :key="day" role="listitem">{{ day }}</span>
          </div>
          <SiteButton to="/book" variant="primary">Reserve Your Package Day</SiteButton>
        </div>
      </ScrollReveal>
    </section>

    <!-- Packages -->
    <section id="packages" class="packages">
      <ScrollReveal variant="fade">
        <header class="section-head">
          <p class="label">Pricing Plans</p>
          <h2>Choose Your Full Package — Tue &amp; Wed</h2>
          <p class="section-head__sub">Every plan below is available on package days only. Pick the visit that matches your occasion.</p>
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
          />
        </ScrollReveal>
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
              <img :src="review.photo" :alt="review.name" class="review-card__photo" loading="lazy" />
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
  PACKAGE_DAYS,
  packageDayHeadline,
  packageDaySubhead,
  packageDayUrgency,
  packages,
} from '@/landing/landingContent'

const packageDays = PACKAGE_DAYS

const heroSlides = [
  {
    image: '/images/hero-1.jpg',
    eyebrow: 'Tue & Wed — full packages only',
    title: 'Your Full Glow Day',
    subtitle: 'Facial, waxing, massage and makeup in one private visit.',
    cta: 'Book Package Day',
  },
  {
    image: '/images/hero-2.jpg',
    eyebrow: 'Shee Aesthetics',
    title: 'Spa Beauty',
    subtitle: 'Reserved treatment rooms. Trained therapists. No rush.',
    cta: 'See Packages',
  },
  {
    image: '/images/hero-3.jpg',
    eyebrow: 'Limited weekly slots',
    title: 'Treat Yourself',
    subtitle: 'Package days fill fast — secure Tuesday or Wednesday early.',
    cta: 'Reserve Now',
  },
]

const activeSlide = ref(0)
const heroReady = ref(true)
let timer: ReturnType<typeof setInterval> | null = null

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
    text: 'Face and body waxing with hot wax — brows, underarms, legs and bikini.',
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

const steps = [
  { title: 'Book', text: 'Choose Tuesday or Wednesday and pick your full package online or by phone.' },
  { title: 'Treatment', text: 'Arrive a few minutes early. Your therapist walks you through each step in your private room.' },
  { title: 'Done', text: 'Leave with facials, waxing, massage and makeup complete — ready for your week or event.' },
]

const reviews = [
  {
    name: 'Wanjiku M.',
    text: 'I come every month for a facial. My skin has improved and the room is always clean and quiet.',
    photo: '/images/testimonial-1.jpg',
  },
  {
    name: 'Sharon O.',
    text: 'Had my makeup done for a wedding. It stayed on all day and looked good in every photo.',
    photo: '/images/testimonial-2.jpg',
  },
  {
    name: 'Diana K.',
    text: 'The Saturday massage is something I look forward to each week. Easy to book and always on time.',
    photo: '/images/testimonial-3.jpg',
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
      content: 'Shee Aesthetics — facials, waxing, massage and makeup. Full packages Tue & Wed. Single treatments Mon, Thu–Sat.',
    },
  ],
})
</script>

<style scoped>
.home {
  background: var(--color-paper);
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
  margin: 0 auto 3rem;
  text-align: center;
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

/* Hero */
.hero {
  position: relative;
  height: min(726px, 88vh);
  min-height: 500px;
  overflow: hidden;
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
  padding: 2rem 1.5rem 4rem;
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

.hero__brand {
  margin-bottom: 1rem;
  animation: hero-float 4s ease-in-out infinite;
}

.hero__eyebrow {
  margin: 0 0 0.5rem;
  font: 600 0.85rem var(--font-body);
  letter-spacing: 0.32em;
  text-transform: uppercase;
}

.hero__title {
  margin: 0 0 0.75rem;
  font-family: var(--font-script);
  font-size: clamp(3.5rem, 10vw, 8rem);
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
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: transparent;
  color: #fff;
  font: 600 0.8rem var(--font-body);
  cursor: pointer;
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

@keyframes hero-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

/* Welcome */
.welcome {
  padding: clamp(4.5rem, 9vh, 6.5rem) 1.5rem;
}

.welcome__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(2rem, 5vw, 4.5rem);
  align-items: center;
}

.welcome__media-wrap,
.welcome__copy {
  height: 100%;
}

.welcome__media {
  position: relative;
}

.welcome__accent {
  position: absolute;
  left: -2rem;
  bottom: -2rem;
  width: 50%;
  height: 45%;
  background: var(--color-cream);
  z-index: 0;
  transition: transform 0.6s var(--ease-story);
}

.welcome__media:hover .welcome__accent {
  transform: translate(4px, 4px);
}

.welcome__photo {
  position: relative;
  z-index: 1;
  width: 100%;
  display: block;
  aspect-ratio: 4 / 5;
  object-fit: cover;
  transition: transform 0.6s var(--ease-story);
}

.welcome__media:hover .welcome__photo {
  transform: scale(1.02);
}

.welcome__flower {
  position: absolute;
  right: -1.5rem;
  bottom: 2rem;
  z-index: 2;
  width: min(160px, 35%);
  pointer-events: none;
}

.welcome__copy h2 {
  margin: 0 0 1.25rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.5vw, 2.5rem);
  font-weight: 400;
  line-height: 1.25;
}

.welcome__text {
  margin: 0 0 2rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.welcome__offers {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.75rem;
  margin-bottom: 2.25rem;
}

.welcome__offers article {
  display: flex;
  gap: 1rem;
  transition: transform 0.35s var(--ease-story);
}

.welcome__offer {
  position: relative;
}

.welcome__offer--package {
  padding: 1.15rem;
  background: var(--color-cream);
  border: 1px solid rgba(222, 150, 141, 0.35);
  border-left: 3px solid var(--color-rose);
}

.welcome__offer-badge {
  position: absolute;
  top: 0.65rem;
  right: 0.75rem;
  padding: 0.2rem 0.55rem;
  background: var(--color-rose);
  color: #fff;
  font: 600 0.62rem var(--font-body);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.welcome__offers article:hover {
  transform: translateX(4px);
}

.welcome__offers h3 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 700;
}

.welcome__offers p {
  margin: 0;
  font: 400 0.88rem/1.55 var(--font-body);
  color: var(--color-muted);
}

/* Services */
.services {
  padding: clamp(3rem, 7vh, 5rem) 1.5rem clamp(5rem, 9vh, 6.5rem);
  background: var(--color-paper);
}

.services__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.service-card {
  position: relative;
  background: #fff;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  padding: 2.75rem 1.5rem 2rem;
  text-align: center;
  height: 100%;
  transition:
    transform 0.4s var(--ease-story),
    box-shadow 0.4s var(--ease-story),
    border-top-color 0.35s;
}

.service-card:hover {
  transform: translateY(-8px);
  border-top-color: var(--color-rose-dark);
  box-shadow: 0 20px 50px rgba(39, 37, 42, 0.12);
}

.service-card__leaf {
  position: absolute;
  inset: 0;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M40 8c-6 14-18 16-18 28a18 18 0 0 0 36 0c0-12-12-14-18-28z' fill='%2327272a'/%3E%3C/svg%3E");
  background-size: 90px;
  pointer-events: none;
}

.service-card__photo-wrap {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 1.75rem;
}

.service-card__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  transition: transform 0.5s var(--ease-story);
}

.service-card:hover .service-card__photo {
  transform: scale(1.05);
}

.service-card__icon {
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 46px;
  height: 46px;
  padding: 10px;
  border-radius: 50%;
  background: var(--color-rose);
  box-sizing: border-box;
  object-fit: contain;
  transition: transform 0.35s var(--ease-story);
}

.service-card:hover .service-card__icon {
  transform: translateX(-50%) scale(1.08);
}

.service-card h3 {
  margin: 0 0 0.85rem;
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
}

.service-card p {
  margin: 0 0 1.25rem;
  font: 400 0.88rem/1.65 var(--font-body);
  color: var(--color-muted);
}

/* More */
.more {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
  background: var(--color-cream);
}

.more__inner {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 3rem;
  align-items: center;
}

.more__copy h2 {
  margin: 0 0 1.75rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 3.5vw, 2.45rem);
  font-weight: 400;
  line-height: 1.25;
}

.more__list {
  columns: 2;
  column-gap: 2rem;
  list-style: none;
  margin: 0 0 2rem;
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
  padding: 2rem 1.25rem;
  text-align: center;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  height: 100%;
  transition:
    transform 0.4s var(--ease-story),
    box-shadow 0.4s,
    border-top-color 0.35s;
}

.stat-card:hover {
  transform: translateY(-8px);
  border-top-color: var(--color-rose-dark);
  box-shadow: 0 20px 48px rgba(39, 37, 42, 0.12);
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

/* Steps */
.steps {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
}

.steps__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  border: 1px solid var(--color-line);
}

.step-card {
  padding: 2.5rem 2rem;
  text-align: center;
  border-right: 1px solid var(--color-line);
  height: 100%;
  transition: background 0.35s;
}

.step-card:hover {
  background: var(--color-cream);
}

.step-card:last-child {
  border-right: none;
}

.step-card__num {
  display: inline-block;
  margin-bottom: 1.25rem;
  font: 700 2rem var(--font-display);
  color: var(--color-rose);
}

.step-card h3 {
  margin: 0 0 0.85rem;
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
}

.step-card p {
  margin: 0;
  font: 400 0.92rem/1.65 var(--font-body);
  color: var(--color-muted);
}

/* Package days sell band */
.package-days {
  padding: clamp(3.5rem, 7vh, 5rem) 1.5rem;
  background: linear-gradient(135deg, var(--color-rose-soft) 0%, var(--color-cream) 55%, #fff 100%);
  border-top: 1px solid rgba(222, 150, 141, 0.2);
  border-bottom: 1px solid rgba(222, 150, 141, 0.2);
}

.package-days__inner {
  width: min(720px, 100%);
  margin: 0 auto;
  text-align: center;
}

.package-days__inner h2 {
  margin: 0 0 1rem;
  font-family: var(--font-display);
  font-size: clamp(1.85rem, 4vw, 2.5rem);
  font-weight: 400;
  line-height: 1.25;
}

.package-days__lead {
  margin: 0 0 1rem;
  font: 400 1rem/1.75 var(--font-body);
  color: var(--color-muted);
}

.package-days__urgency {
  margin: 0 0 1.5rem;
  font: 600 0.92rem/1.6 var(--font-body);
  color: var(--color-ink);
}

.package-days__chips {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.75rem;
}

.package-days__chips span {
  padding: 0.5rem 1.25rem;
  border: 1px solid var(--color-rose);
  background: #fff;
  font: 600 0.75rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose-dark);
}

/* Packages */
.packages {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
  background: var(--color-paper);
}

.packages__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.75rem;
  align-items: stretch;
  padding-top: 0.5rem;
}

/* Reviews */
.reviews {
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
}

.reviews__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.review-card {
  margin: 0;
  padding: 2.25rem 2rem;
  background: #fff;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  position: relative;
  height: 100%;
  transition:
    transform 0.4s var(--ease-story),
    box-shadow 0.4s,
    border-top-color 0.35s;
}

.review-card:hover {
  transform: translateY(-8px);
  border-top-color: var(--color-rose-dark);
  box-shadow: 0 20px 48px rgba(39, 37, 42, 0.12);
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

.review-card__photo {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
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
  grid-template-columns: repeat(6, 1fr);
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
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
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
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
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
  padding: clamp(4rem, 8vh, 6rem) 1.5rem;
}

.blog__grid {
  width: var(--container);
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.blog-card {
  height: 100%;
  background: #fff;
  border: 1px solid var(--color-line);
  border-top: 3px solid var(--color-rose);
  box-shadow: var(--shadow-card);
  transition:
    transform 0.4s var(--ease-story),
    box-shadow 0.4s,
    border-top-color 0.35s;
}

.blog-card:hover {
  transform: translateY(-8px);
  border-top-color: var(--color-rose-dark);
  box-shadow: 0 20px 48px rgba(39, 37, 42, 0.12);
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
  padding: 1.5rem 1.25rem 1.75rem;
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

/* Responsive */
@media (max-width: 1024px) {
  .services__grid { grid-template-columns: repeat(2, 1fr); }
  .gallery__grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .welcome__inner,
  .more__inner,
  .cta__inner { grid-template-columns: 1fr; }

  .welcome__offers { grid-template-columns: 1fr; }
  .welcome__accent { left: 0; bottom: -1rem; }

  .services__grid,
  .packages__grid,
  .reviews__grid,
  .blog__grid,
  .steps__grid { grid-template-columns: 1fr; }

  .step-card { border-right: none; border-bottom: 1px solid var(--color-line); }
  .more__list { columns: 1; }
  .gallery__grid { grid-template-columns: repeat(2, 1fr); }
}

@media (prefers-reduced-motion: reduce) {
  .hero__slide,
  .hero__bg,
  .hero__content,
  .hero__brand,
  .cta__photo img,
  .service-card,
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
