<template>
  <div class="landing-shell">
    <SiteLoader />
    <SiteHeader />
    <slot />
    <SiteFooter />
  </div>
</template>

<style scoped>
.landing-shell {
  min-height: 100vh;
  background: var(--color-paper);
}
</style>
