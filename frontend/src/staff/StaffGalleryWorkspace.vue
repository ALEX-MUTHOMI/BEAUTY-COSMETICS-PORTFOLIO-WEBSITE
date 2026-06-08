<template>
  <StaffPortalShell title="Gallery">
    <section class="gallery-panel">
      <div>
        <p class="eyebrow">Portfolio manager</p>
        <h2>Prepare images for the website.</h2>
        <p>
          Select a section, choose photos, then publish only after each image is ready. Sensitive
          waxing images stay off the homepage and need a warning.
        </p>
      </div>
      <button type="button" :disabled="!canUpload" @click="submitSelected">Upload selected images</button>
    </section>

    <section class="upload-flow" aria-label="Upload image to portfolio">
      <label>
        Website section
        <select v-model="selectedCategoryId">
          <option value="">Choose section</option>
          <option v-for="category in categories" :key="category.publicId" :value="category.publicId">
            {{ category.name }}
          </option>
        </select>
      </label>
      <label>
        Detail section
        <select v-model="selectedSubcategoryId">
          <option value="">No detail section</option>
          <option v-for="subcategory in selectedCategory?.subcategories || []" :key="subcategory.publicId" :value="subcategory.publicId">
            {{ subcategory.name }}
          </option>
        </select>
      </label>
      <label>
        Select images
        <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onFilesSelected" />
      </label>
      <p class="upload-note">{{ selectionCopy }}</p>
      <p class="upload-note">{{ currentStateCopy }}</p>
      <p v-if="selectedCategory?.isSensitiveDefault" class="sensitive-warning">
        Sensitive waxing image: warning required before publishing.
      </p>
    </section>

    <section class="gallery-grid" aria-label="Gallery categories">
      <article v-for="category in categories" :key="category.publicId">
        <div aria-hidden="true" />
        <h3>{{ category.name }}</h3>
        <p>
          {{
            category.isSensitiveDefault
              ? 'Warning required before visitors see these images.'
              : 'Safe for normal portfolio placement after review.'
          }}
        </p>
        <label><input type="checkbox" :disabled="category.isSensitiveDefault" /> Featured on homepage</label>
      </article>
    </section>
  </StaffPortalShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import StaffPortalShell from './StaffPortalShell.vue'
import type { StaffGalleryCategory } from './staffPortalApi'
import { getStaffGalleryCategories, postStaffGalleryImage } from './staffPortalApi'

const props = withDefaults(
  defineProps<{
    apiBaseUrl?: string
    csrfToken?: string
    initialCategories?: StaffGalleryCategory[]
  }>(),
  {
    apiBaseUrl: '',
    csrfToken: '',
    initialCategories: () => [
      { publicId: 'makeup', name: 'Makeup', slug: 'makeup', isSensitiveDefault: false, subcategories: [] },
      { publicId: 'waxing', name: 'Waxing', slug: 'waxing', isSensitiveDefault: true, subcategories: [] },
      { publicId: 'massage', name: 'Massage', slug: 'massage', isSensitiveDefault: false, subcategories: [] },
      { publicId: 'facial', name: 'Facial / Skincare', slug: 'facial', isSensitiveDefault: false, subcategories: [] },
    ],
  },
)

const categories = ref<StaffGalleryCategory[]>(props.initialCategories)
const selectedCategoryId = ref('')
const selectedSubcategoryId = ref('')
const selectedFiles = ref<File[]>([])
const currentStateCopy = ref('Checking image')

const selectedCategory = computed(() => categories.value.find((category) => category.publicId === selectedCategoryId.value))
const selectionCopy = computed(() => {
  const count = selectedFiles.value.length
  if (!count) return 'Choose JPG, PNG, or WebP images from your phone.'
  return `${count} image${count === 1 ? '' : 's'} selected. Cap warnings appear before upload.`
})
const canUpload = computed(() => Boolean(selectedCategoryId.value && selectedFiles.value.length))

function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFiles.value = Array.from(input.files || [])
  currentStateCopy.value = selectedFiles.value.length ? 'Preparing for website' : 'Checking image'
}

async function submitSelected() {
  if (!canUpload.value) return
  currentStateCopy.value = 'Preparing for website'
  for (const file of selectedFiles.value) {
    const form = new FormData()
    form.set('category_public_id', selectedCategoryId.value)
    if (selectedSubcategoryId.value) form.set('subcategory_public_id', selectedSubcategoryId.value)
    form.set('image', file)
    const result = await postStaffGalleryImage(props.apiBaseUrl, form, props.csrfToken)
    currentStateCopy.value = result.ok ? 'Ready to publish' : result.message || 'Could not use this image'
  }
}

if (!props.initialCategories.length) {
  getStaffGalleryCategories(props.apiBaseUrl).then((result) => {
    if (result.ok && result.data) categories.value = result.data.categories
  })
}
</script>

<style scoped>
.gallery-panel,
.gallery-grid article,
.upload-flow {
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

.upload-flow {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.upload-flow label {
  display: grid;
  gap: 0.45rem;
  color: #4b2d20;
  font-weight: 800;
}

.upload-flow select,
.upload-flow input {
  min-height: 2.7rem;
  border: 1px solid rgba(55, 32, 22, 0.18);
  border-radius: 16px;
  padding: 0.6rem;
  background: #fffaf4;
}

.upload-note,
.sensitive-warning {
  margin: 0;
  align-self: end;
  color: #68402d;
}

.sensitive-warning {
  color: #8a2f1d;
  font-weight: 900;
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
  .gallery-grid,
  .upload-flow {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
