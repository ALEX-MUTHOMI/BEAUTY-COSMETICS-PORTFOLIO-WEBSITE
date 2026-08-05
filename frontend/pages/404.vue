<template>
  <main class="not-found">
    <SectionHeading
      eyebrow="Oops"
      title="Page not found"
      description="Check the URL and try again. If you’re trying to book, we can take you to the booking page."
    />

    <div class="not-found__actions">
      <SiteButton to="/" variant="outline">Home</SiteButton>
      <SiteButton to="/services" variant="primary">Services</SiteButton>
      <SiteButton to="/book" variant="primary">Book now</SiteButton>
    </div>
  </main>
</template>

<script setup lang="ts">
// Nuxt will automatically set the correct 404 status code for this special page.
</script>

<style scoped>
.not-found {
  padding: 3rem 1rem;
  max-width: 68rem;
  margin: 0 auto;
}

.not-found__actions {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
</style>
