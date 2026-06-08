<template>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Premium Beauty Portfolio</p>
      <h1>Polished looks, safely published.</h1>
      <p class="lede">
        Browse featured beauty work prepared through a secure image pipeline. Originals stay private;
        visitors only see optimized website-ready images.
      </p>
      <a class="cta" :href="runtimeConfig.public.apiBaseUrl + '/health/'">Check API Health</a>
    </section>

    <section class="portfolio" aria-label="Featured portfolio">
      <div class="section-heading">
        <p class="eyebrow">Featured work</p>
        <h2>Website-ready gallery</h2>
      </div>
      <p v-if="galleryError" class="gallery-state">Portfolio images could not load. Please try again shortly.</p>
      <p v-else-if="!featuredImages.length" class="gallery-state">Portfolio images are being prepared.</p>
      <div v-else class="carousel" aria-label="Homepage carousel">
        <article v-for="image in featuredImages" :key="image.public_id">
          <img
            :src="bestVariant(image).url"
            :srcset="srcset(image)"
            :width="bestVariant(image).width"
            :height="bestVariant(image).height"
            :alt="image.title || image.category.name"
            loading="lazy"
            decoding="async"
          />
          <div>
            <p>{{ image.category.name }}</p>
            <h3>{{ image.title || 'Featured look' }}</h3>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup lang="ts">
interface GalleryVariant {
  url: string
  width: number
  height: number
  format: string
  size_bytes: number
}

interface GalleryImage {
  public_id: string
  title: string
  category: { slug: string; name: string }
  requires_warning: boolean
  variants: Record<string, GalleryVariant>
}

const runtimeConfig = useRuntimeConfig()
const { data, error } = await useFetch<{ images: GalleryImage[] }>(
  `${runtimeConfig.public.apiBaseUrl}/api/gallery/public/homepage/`,
  {
    default: () => ({ images: [] }),
  },
)

const galleryError = computed(() => Boolean(error.value))
const featuredImages = computed(() => (data.value?.images || []).filter((image) => !image.requires_warning))

function bestVariant(image: GalleryImage): GalleryVariant {
  return image.variants.hero || image.variants.desktop || image.variants.tablet || image.variants.mobile || image.variants.thumbnail
}

function srcset(image: GalleryImage): string {
  return Object.values(image.variants)
    .filter((variant) => variant.url.endsWith('.webp'))
    .sort((a, b) => a.width - b.width)
    .map((variant) => `${variant.url} ${variant.width}w`)
    .join(', ')
}
</script>

<style scoped>
.shell {
  min-height: 100vh;
  padding: 2rem;
  background:
    radial-gradient(circle at 20% 20%, rgba(176, 88, 54, 0.24), transparent 32rem),
    linear-gradient(135deg, #fff7ed 0%, #ead0bb 48%, #b86245 100%);
}

.hero {
  max-width: 760px;
  padding: clamp(2rem, 6vw, 5rem);
  border: 1px solid rgba(36, 23, 15, 0.18);
  border-radius: 32px;
  background: rgba(255, 250, 244, 0.72);
  box-shadow: 0 30px 80px rgba(72, 40, 22, 0.22);
}

.eyebrow {
  margin: 0 0 1rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font: 700 0.78rem ui-sans-serif, sans-serif;
}

h1 {
  margin: 0;
  font-size: clamp(2.6rem, 7vw, 5.8rem);
  line-height: 0.94;
}

.lede {
  max-width: 58ch;
  margin: 1.5rem 0 2rem;
  color: #573728;
  font: 1.12rem/1.65 ui-sans-serif, sans-serif;
}

.cta {
  display: inline-flex;
  color: #fff9f1;
  background: #24170f;
  border-radius: 999px;
  padding: 0.9rem 1.3rem;
  text-decoration: none;
  font: 800 0.9rem ui-sans-serif, sans-serif;
}

.portfolio {
  margin-top: 2rem;
  border-radius: 34px;
  background: rgba(36, 23, 15, 0.78);
  color: #fffaf3;
  padding: clamp(1rem, 4vw, 2rem);
}

.section-heading {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 4rem);
}

.gallery-state {
  color: #f8d8be;
}

.carousel {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.carousel article {
  overflow: hidden;
  border-radius: 28px;
  background: #fff7ed;
  color: #24170f;
}

.carousel img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.carousel div {
  padding: 1rem;
}

.carousel p,
.carousel h3 {
  margin: 0.2rem 0;
}

@media (max-width: 820px) {
  .carousel {
    grid-template-columns: 1fr;
  }
}
</style>
