<template>
  <StaffPortalShell title="Gallery">
    <section class="gallery-panel">
      <div>
        <p class="eyebrow">Portfolio manager</p>
        <h2>Prepare images before publishing.</h2>
        <p>
          Uploads are disabled until the secure gallery backend is connected. Sensitive waxing
          images must be intentionally reviewed before homepage placement.
        </p>
      </div>
      <button type="button" disabled>Upload images unavailable</button>
    </section>

    <section class="gallery-grid" aria-label="Gallery categories">
      <article v-for="category in categories" :key="category.name">
        <div aria-hidden="true" />
        <h3>{{ category.name }}</h3>
        <p>{{ category.copy }}</p>
        <label><input type="checkbox" :disabled="category.sensitive" /> Featured on homepage</label>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import StaffPortalShell from './StaffPortalShell.vue'

const categories = [
  { name: 'Makeup', copy: 'Before and after looks for safe publication.', sensitive: false },
  { name: 'Waxing', copy: 'Sensitive category. Confirm placement before publishing.', sensitive: true },
  { name: 'Massage', copy: 'Calm portfolio imagery.', sensitive: false },
  { name: 'Facial / Skincare', copy: 'Treatment room and skincare results.', sensitive: false },
]
</script>

<style scoped>
.gallery-panel,
.gallery-grid article {
  border: 1px solid rgba(55, 32, 22, 0.12);
  border-radius: 28px;
  background: rgba(255, 253, 248, 0.84);
}

.gallery-panel {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.2rem;
  margin-bottom: 1rem;
}

.eyebrow {
  margin: 0 0 0.4rem;
  color: #8a4f34;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.gallery-panel h2,
.gallery-panel p,
.gallery-grid h3,
.gallery-grid p {
  margin: 0.25rem 0;
}

.gallery-panel button {
  min-height: 2.7rem;
  border: 0;
  border-radius: 999px;
  padding: 0 1rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.gallery-grid article {
  padding: 1rem;
}

.gallery-grid div {
  aspect-ratio: 4 / 3;
  border-radius: 20px;
  background: linear-gradient(135deg, #e9c6ab, #8a4f34);
}

@media (max-width: 960px) {
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .gallery-panel,
  .gallery-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
