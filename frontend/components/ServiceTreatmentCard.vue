<template>
  <button
    type="button"
    class="service-treatment"
    :class="[
      `service-treatment--${variant}`,
      { 'service-treatment--selected': selected },
    ]"
    :aria-pressed="selected"
    @click="emit('select')"
  >
    <span class="service-treatment__badge" aria-hidden="true">{{ indexLabel }}</span>

    <div class="service-treatment__head">
      <h3 class="service-treatment__name">{{ name }}</h3>
      <p class="service-treatment__price">{{ price }}</p>
    </div>

    <p class="service-treatment__duration">
      <span class="service-treatment__duration-icon" aria-hidden="true">◷</span>
      {{ duration }}
    </p>

    <p class="service-treatment__text">{{ description }}</p>

    <ul class="service-treatment__list">
      <li v-for="item in highlights" :key="item">{{ item }}</li>
    </ul>

    <span class="service-treatment__action">
      {{ selected ? 'Selected — book this' : 'Select this treatment' }}
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    name: string
    description: string
    duration: string
    price: string
    highlights: string[]
    selected?: boolean
    index?: number
    variant?: 'facials' | 'massage' | 'waxing' | 'makeup'
  }>(),
  { selected: false, index: 0, variant: 'facials' },
)

const emit = defineEmits<{ select: [] }>()

const indexLabel = computed(() => String(props.index + 1).padStart(2, '0'))
</script>

<style scoped>
.service-treatment {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 1.35rem 1.25rem 1.2rem;
  border: 2px solid transparent;
  border-radius: 2px;
  background: #fff;
  box-shadow: 0 4px 20px rgba(39, 37, 42, 0.06);
  text-align: left;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.2s ease,
    box-shadow 0.25s ease,
    transform 0.2s ease,
    background-color 0.2s ease;
}

.service-treatment:hover {
  box-shadow: 0 10px 28px rgba(39, 37, 42, 0.1);
  transform: translateY(-2px);
}

.service-treatment:focus-visible {
  outline: 2px solid var(--color-rose);
  outline-offset: 2px;
}

.service-treatment--selected {
  border-color: var(--color-rose);
  background: linear-gradient(165deg, #fff 0%, var(--color-rose-soft) 100%);
  box-shadow:
    0 12px 32px rgba(222, 150, 141, 0.22),
    inset 0 0 0 1px rgba(222, 150, 141, 0.15);
  transform: translateY(-3px);
}

.service-treatment--facials.service-treatment--selected {
  border-color: #de968d;
}

.service-treatment--massage.service-treatment--selected {
  border-color: #c97f76;
  background: linear-gradient(165deg, #fff 0%, #f8ece9 100%);
}

.service-treatment--waxing.service-treatment--selected {
  border-color: #b86f66;
  background: linear-gradient(165deg, #fff 0%, #f5e6e3 100%);
}

.service-treatment--makeup.service-treatment--selected {
  border-color: #d4a59e;
  background: linear-gradient(165deg, #fff 0%, #faf0ee 100%);
}

.service-treatment__badge {
  align-self: flex-start;
  margin-bottom: 0.85rem;
  padding: 0.2rem 0.55rem;
  font: 700 0.68rem var(--font-body);
  letter-spacing: 0.14em;
  color: var(--color-rose-dark);
  background: var(--color-rose-soft);
  border-radius: 2px;
}

.service-treatment--selected .service-treatment__badge {
  color: #fff;
  background: var(--color-rose);
}

.service-treatment__head {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.65rem;
}

.service-treatment__name {
  margin: 0;
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  line-height: 1.3;
  color: var(--color-ink);
}

.service-treatment__price {
  margin: 0;
  font: 700 0.95rem var(--font-body);
  color: var(--color-rose-dark);
}

.service-treatment__duration {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.75rem;
  font: 600 0.78rem var(--font-body);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.service-treatment__duration-icon {
  font-size: 0.9rem;
  line-height: 1;
}

.service-treatment__text {
  margin: 0 0 1rem;
  font: 400 0.92rem/1.65 var(--font-body);
  color: var(--color-deep);
}

.service-treatment__list {
  margin: 0 0 1.15rem;
  padding: 0;
  list-style: none;
  flex: 1;
}

.service-treatment__list li {
  position: relative;
  padding-left: 1.1rem;
  font: 500 0.86rem/1.55 var(--font-body);
  color: var(--color-ink);
}

.service-treatment__list li + li {
  margin-top: 0.4rem;
}

.service-treatment__list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  top: 0;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--color-rose);
}

.service-treatment__action {
  display: block;
  margin-top: auto;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(39, 37, 42, 0.08);
  font: 700 0.72rem var(--font-body);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--color-rose);
}

.service-treatment--selected .service-treatment__action {
  color: var(--color-rose-dark);
  border-top-color: rgba(222, 150, 141, 0.35);
}

@media (prefers-reduced-motion: reduce) {
  .service-treatment {
    transition: none;
  }

  .service-treatment:hover,
  .service-treatment--selected {
    transform: none;
  }
}
</style>
