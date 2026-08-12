<template>
  <article
    class="service-treatment"
    :class="{ 'service-treatment--light': index % 2 === 1 }"
  >
    <span class="service-treatment__badge" aria-hidden="true">{{ indexLabel }}</span>

    <div class="service-treatment__body">
      <div class="service-treatment__row">
        <h3 class="service-treatment__name">{{ name }}</h3>
        <p class="service-treatment__duration">{{ duration }}</p>
        <p class="service-treatment__price">{{ price }}</p>
        <SiteButton
          :to="bookTo"
          variant="primary"
          class="service-treatment__book"
        >
          Book
        </SiteButton>
      </div>
      <p v-if="highlightLine" class="service-treatment__highlights">
        {{ highlightLine }}
      </p>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    name: string
    duration: string
    price: string
    highlights: string[]
    bookTo: string
    index?: number
  }>(),
  { index: 0 },
)

const indexLabel = computed(() => String(props.index + 1).padStart(2, '0'))

const highlightLine = computed(() =>
  props.highlights.filter(Boolean).slice(0, 3).join(' · '),
)
</script>

<style scoped>
.service-treatment {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.85rem 1rem;
  align-items: start;
  margin: 0;
  padding: 1.05rem 0;
  border-bottom: 1px solid rgba(248, 242, 238, 0.12);
  text-align: left;
  transition: background-color 0.18s ease;
}

.service-treatment:first-child {
  border-top: 1px solid rgba(248, 242, 238, 0.12);
}

.service-treatment:hover {
  background: rgba(222, 150, 141, 0.06);
}

.service-treatment:focus-within {
  background: rgba(222, 150, 141, 0.08);
  outline: none;
}

.service-treatment--light {
  background: rgba(252, 248, 245, 0.72);
  border: 1px solid rgba(176, 122, 113, 0.28);
  border-radius: 8px;
  padding: 0.85rem 1rem;
}

.service-treatment--light:hover {
  background: rgba(252, 248, 245, 0.92);
}

.service-treatment--light .service-treatment__name {
  color: #1e191b;
}

.service-treatment--light .service-treatment__duration {
  color: #6e6764;
}

.service-treatment--light .service-treatment__price {
  color: #b56b62;
}

.service-treatment--light .service-treatment__highlights {
  color: #59504c;
}

.service-treatment__badge {
  margin-top: 0.15rem;
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.14em;
  color: var(--color-rose);
}

.service-treatment__body {
  min-width: 0;
}

.service-treatment__row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.35rem 1rem;
  align-items: center;
}

.service-treatment__name {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.08rem, 2.4vw, 1.28rem);
  font-weight: 500;
  line-height: 1.3;
  color: #fff;
}

.service-treatment__duration {
  margin: 0;
  font: 600 0.72rem/1.4 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 248, 244, 0.62);
}

.service-treatment__price {
  margin: 0;
  font: 700 0.92rem/1.3 var(--font-body);
  color: #f0b8ac;
}

.service-treatment__book {
  justify-self: start;
  margin-top: 0.35rem;
}

.service-treatment__book :deep(.site-btn) {
  min-height: 2.5rem;
  padding-inline: 1.15rem;
  font-size: 0.72rem;
}

.service-treatment__highlights {
  margin: 0.55rem 0 0;
  font: 400 0.82rem/1.5 var(--font-body);
  color: rgba(255, 248, 244, 0.7);
}

@media (min-width: 768px) {
  .service-treatment {
    padding: 1.15rem 0.65rem;
  }

  .service-treatment__row {
    grid-template-columns: minmax(0, 1.4fr) auto auto auto;
    gap: 0.75rem 1.25rem;
  }

  .service-treatment__duration,
  .service-treatment__price {
    white-space: nowrap;
  }

  .service-treatment__book {
    margin-top: 0;
    justify-self: end;
  }
}

@media (prefers-reduced-motion: reduce) {
  .service-treatment {
    transition: none;
  }
}
</style>
