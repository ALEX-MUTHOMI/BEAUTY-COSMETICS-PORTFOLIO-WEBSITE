<template>
  <div class="landing-shell">
    <SiteLoader />
    <SiteHeader />
    <slot />
    <SiteFooter />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

useHead({
  htmlAttrs: {
    class: 'is-loading',
  },
})

onMounted(() => {
  document.documentElement.classList.add('site-motion')

  // If the loader never dismisses (blocked JS), still allow interaction after 5s.
  setTimeout(() => {
    document.documentElement.classList.add('site-ready')
    document.documentElement.classList.remove('is-loading')
  }, 5000)
})
</script>

<style scoped>
.landing-shell {
  min-height: 100vh;
  background: var(--color-paper);
}
</style>
