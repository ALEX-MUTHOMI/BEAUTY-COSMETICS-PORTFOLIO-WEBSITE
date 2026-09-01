<template>
  <div
    ref="root"
    class="reveal"
    :class="[
      { 'reveal--visible': isVisible },
      variant ? `reveal--${variant}` : '',
    ]"
    :style="{ '--reveal-delay': `${delay}ms` }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'up' | 'left' | 'right' | 'scale' | 'fade'
    delay?: number
    threshold?: number
    /** Reveal immediately (e.g. hero-adjacent content after loader). */
    immediate?: boolean
  }>(),
  { variant: 'up', delay: 0, threshold: 0.12, immediate: false },
)

const root = ref<HTMLElement | null>(null)
const isVisible = ref(false)

let observer: IntersectionObserver | null = null

function reveal() {
  isVisible.value = true
  observer?.disconnect()
  observer = null
}

function isInViewport(el: HTMLElement): boolean {
  const rect = el.getBoundingClientRect()
  const viewHeight = window.innerHeight || document.documentElement.clientHeight
  return rect.top <= viewHeight * 0.92 && rect.bottom >= 0
}

onMounted(() => {
  if (!root.value) return

  // Respects prefers-reduced-motion: reduce for accessibility.
  // Animations are disabled for users who prefer reduced motion.
  if (props.immediate || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    reveal()
    return
  }

  if (isInViewport(root.value)) {
    reveal()
    return
  }

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) reveal()
    },
    { threshold: props.threshold, rootMargin: '0px 0px -12% 0px' },
  )

  observer.observe(root.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>
