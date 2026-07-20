<template>
  <article class="mellis-service">
    <div class="mellis-service__visual">
      <img :src="image" :alt="name" class="mellis-service__photo" loading="lazy" />
      <span class="mellis-service__icon-wrap" aria-hidden="true">
        <img :src="icon" alt="" class="mellis-service__icon" />
      </span>
    </div>
    <h3 class="mellis-service__title">{{ name }}</h3>
    <p class="mellis-service__text">{{ text }}</p>
    <SiteButton :to="ctaTo" variant="text">{{ ctaLabel }}</SiteButton>
  </article>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    name: string
    text: string
    image: string
    icon: string
    ctaTo?: string
    ctaLabel?: string
  }>(),
  {
    ctaTo: '/services',
    ctaLabel: 'View treatments',
  },
)
</script>

<style scoped>
.mellis-service {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  height: 100%;
  padding: 0 0.5rem 1rem;
}

.mellis-service__visual {
  position: relative;
  width: 128px;
  height: 128px;
  margin: 0 auto 1.15rem;
}

@media (min-width: 768px) {
  .mellis-service__visual {
    width: 148px;
    height: 148px;
    margin-bottom: 1.35rem;
  }
}

.mellis-service__photo {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #fff;
  box-shadow: 0 8px 32px rgba(39, 37, 42, 0.1);
  transition: transform 0.45s var(--ease-story);
}

.mellis-service:hover .mellis-service__photo {
  transform: scale(1.04);
}

.mellis-service__icon-wrap {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-rose);
  border: 3px solid #fff;
  box-shadow: 0 4px 14px rgba(222, 150, 141, 0.45);
}

.mellis-service__icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  filter: brightness(0) invert(1);
}

.mellis-service__title {
  margin: 0 0 0.45rem;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-ink);
}

.mellis-service__text {
  margin: 0 0 0.75rem;
  max-width: 26ch;
  font: 400 0.86rem/1.55 var(--font-body);
  color: var(--color-muted);
}
</style>
