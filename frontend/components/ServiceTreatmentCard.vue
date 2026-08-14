<template>
  <article class="service-treatment">
    <span class="service-treatment__badge" aria-hidden="true">{{ indexLabel }}</span>

    <div class="service-treatment__body">
      <div class="service-treatment__row">
        <div class="service-treatment__info">
          <h3 class="service-treatment__name">{{ name }}</h3>
          <p class="service-treatment__duration">{{ duration }}</p>
        </div>

        <div class="service-treatment__action">
          <p class="service-treatment__price">{{ price }}</p>
          <SiteButton
            :to="bookTo"
            variant="primary"
            class="service-treatment__book"
          >
            Book
          </SiteButton>
        </div>
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
  gap: 0.75rem 0.95rem;
  align-items: center;
  margin: 0 0 0.65rem;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  background: rgba(38, 30, 32, 0.85);
  border: 1px solid rgba(222, 150, 141, 0.2);
  text-align: left;
  box-shadow: 0 4px 14px rgba(20, 15, 17, 0.16);
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    background-color 0.18s ease,
    box-shadow 0.18s ease;
}

.service-treatment:last-child {
  margin-bottom: 0;
}

.service-treatment:hover {
  transform: translateY(-1px);
  background: rgba(46, 36, 38, 0.95);
  border-color: var(--color-rose, #b07a71);
  box-shadow: 0 6px 18px rgba(20, 15, 17, 0.26);
}

.service-treatment:focus-within {
  border-color: var(--color-rose);
  outline: none;
}

.service-treatment__badge {
  font: 700 0.72rem/1 var(--font-body);
  letter-spacing: 0.12em;
  color: var(--color-rose, #b07a71);
}

.service-treatment__body {
  min-width: 0;
}

.service-treatment__row {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.service-treatment__info {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.45rem 0.75rem;
}

.service-treatment__name {
  margin: 0;
  font-family: var(--font-display);
  font-size: clamp(1.02rem, 2.2vw, 1.18rem);
  font-weight: 500;
  line-height: 1.25;
  color: #fcf8f5;
}

.service-treatment__duration {
  margin: 0;
  font: 600 0.68rem/1.3 var(--font-body);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 248, 244, 0.58);
}

.service-treatment__action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
}

.service-treatment__price {
  margin: 0;
  font: 700 0.9rem/1.2 var(--font-body);
  color: #f0b8ac;
}

.service-treatment__book :deep(.site-btn) {
  min-height: 2.15rem;
  padding-inline: 0.95rem;
  font-size: 0.68rem;
  letter-spacing: 0.08em;
  border-radius: 6px;
}

.service-treatment__highlights {
  margin: 0.35rem 0 0;
  font: 400 0.78rem/1.45 var(--font-body);
  color: rgba(255, 248, 244, 0.65);
}

@media (min-width: 640px) {
  .service-treatment {
    padding: 0.85rem 1.15rem;
  }

  .service-treatment__row {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .service-treatment__info {
    flex: 1 1 auto;
    min-width: 0;
  }

  .service-treatment__action {
    flex: 0 0 auto;
    justify-content: flex-end;
    gap: 1.25rem;
  }

  .service-treatment__price {
    white-space: nowrap;
  }
}

@media (prefers-reduced-motion: reduce) {
  .service-treatment {
    transition: none;
  }
}
</style>
