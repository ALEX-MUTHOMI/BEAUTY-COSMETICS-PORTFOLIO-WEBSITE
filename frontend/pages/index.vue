<template>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Premium Beauty Booking Platform</p>
      <h1>Secure cosmetics portfolio with verified SSR delivery.</h1>
      <p class="lede">
        Nuxt renders this page on the server while Django provides the protected API boundary
        for passwordless authentication and M-Pesa workflows.
      </p>
      <a class="cta" :href="runtimeConfig.public.apiBaseUrl + '/health/'">Check API Health</a>
    </section>
  </main>
</template>

<script setup lang="ts">
const runtimeConfig = useRuntimeConfig()
</script>

<style scoped>
.shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
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
</style>
