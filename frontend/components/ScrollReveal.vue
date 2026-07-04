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
  }>(),
  { variant: 'up', delay: 0, threshold: 0.12 },
)

const root = ref<HTMLElement | null>(null)
const isVisible = ref(false)

let observer: IntersectionObserver | null = null

onMounted(() => {
  if (!root.value) return

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    isVisible.value = true
    return
  }

  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry?.isIntersecting) {
        isVisible.value = true
        observer?.disconnect()
      }
    },
    { threshold: props.threshold, rootMargin: '0px 0px -48px 0px' },
  )

  observer.observe(root.value)
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>
