<template>
  <StaffPortalShell title="Gallery" :api-base-url="apiBaseUrl">
    <div class="gallery-desk">
      <header class="gallery-desk__intro">
        <h2>Add photos for the website.</h2>
        <p>Pick a section, choose photos, then upload.</p>
      </header>

      <section class="gallery-desk__form" aria-label="Upload photos">
        <label>
          Section
          <select v-model="selectedCategoryId">
            <option value="">Choose section</option>
            <option v-for="category in categories" :key="category.publicId" :value="category.publicId">
              {{ category.name }}
            </option>
          </select>
        </label>
        <label v-if="(selectedCategory?.subcategories || []).length">
          Detail
          <select v-model="selectedSubcategoryId">
            <option value="">None</option>
            <option
              v-for="subcategory in selectedCategory?.subcategories || []"
              :key="subcategory.publicId"
              :value="subcategory.publicId"
            >
              {{ subcategory.name }}
            </option>
          </select>
        </label>
        <label class="gallery-desk__files">
          Photos
          <input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="onFilesSelected" />
        </label>
        <p v-if="selectionCopy" class="gallery-desk__note">{{ selectionCopy }}</p>
        <p v-if="selectedCategory?.isSensitiveDefault" class="gallery-desk__warn" role="status">
          Needs a visitor warning before it goes live.
        </p>
        <p v-if="statusCopy" class="gallery-desk__note" role="status">{{ statusCopy }}</p>
        <button type="button" class="gallery-desk__upload" :disabled="!canUpload || uploading" @click="submitSelected">
          {{ uploading ? 'Uploading…' : 'Upload' }}
        </button>
      </section>

      <section class="gallery-desk__sections" aria-label="Website sections">
        <button
          v-for="category in categories"
          :key="category.publicId"
          type="button"
          class="gallery-chip"
          :class="{ 'gallery-chip--active': selectedCategoryId === category.publicId }"
          @click="selectedCategoryId = category.publicId"
        >
          <strong>{{ category.name }}</strong>
          <span v-if="category.isSensitiveDefault">Needs warning</span>
        </button>
      </section>
    </div>
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
const statusCopy = ref('')
const uploading = ref(false)

const selectedCategory = computed(() => categories.value.find((category) => category.publicId === selectedCategoryId.value))
const selectionCopy = computed(() => {
  const count = selectedFiles.value.length
  if (!count) return 'JPG, PNG, or WebP from your phone.'
  return `${count} photo${count === 1 ? '' : 's'} ready.`
})
const canUpload = computed(() => Boolean(selectedCategoryId.value && selectedFiles.value.length))

function onFilesSelected(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFiles.value = Array.from(input.files || [])
  statusCopy.value = ''
}

async function submitSelected() {
  if (!canUpload.value || uploading.value) return
  uploading.value = true
  statusCopy.value = ''
  try {
    for (const file of selectedFiles.value) {
      const form = new FormData()
      form.set('category_public_id', selectedCategoryId.value)
      if (selectedSubcategoryId.value) form.set('subcategory_public_id', selectedSubcategoryId.value)
      form.set('image', file)
      const result = await postStaffGalleryImage(props.apiBaseUrl, form, props.csrfToken)
      if (!result.ok) {
        statusCopy.value = result.message || 'Could not upload this photo.'
        return
      }
    }
    statusCopy.value = 'Photos uploaded.'
    selectedFiles.value = []
  } finally {
    uploading.value = false
  }
}

if (!props.initialCategories.length) {
  getStaffGalleryCategories(props.apiBaseUrl).then((result) => {
    if (result.ok && result.data) categories.value = result.data.categories
  })
}
</script>

<style scoped>
.gallery-desk {
  display: grid;
  gap: 1rem;
}

.gallery-desk__intro h2 {
  margin: 0 0 0.35rem;
  font-family: var(--font-display, 'Libre Baskerville', Georgia, serif);
  font-size: clamp(1.35rem, 4vw, 1.75rem);
  font-weight: 400;
}

.gallery-desk__intro p {
  margin: 0;
  color: var(--color-muted, #8a8580);
}

.gallery-desk__form {
  display: grid;
  gap: 0.85rem;
  padding: 1.1rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  background: var(--color-paper, #fffcf8);
}

.gallery-desk__form label {
  display: grid;
  gap: 0.4rem;
  font: 600 0.78rem/1.2 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-muted, #8a8580);
}

.gallery-desk__form select,
.gallery-desk__form input[type='file'] {
  min-height: 2.75rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.14));
  border-radius: 0;
  padding: 0.55rem 0.75rem;
  background: var(--color-cream, #f7f3ee);
  color: var(--color-ink, #27272a);
  font: 500 0.95rem/1.2 var(--font-body, 'Manrope', sans-serif);
  text-transform: none;
  letter-spacing: normal;
}

.gallery-desk__note {
  margin: 0;
  color: var(--color-muted, #8a8580);
  font-size: 0.9rem;
}

.gallery-desk__warn {
  margin: 0;
  padding: 0.7rem 0.85rem;
  border-left: 3px solid var(--color-rose, #c98980);
  background: color-mix(in srgb, var(--color-rose-soft, #f0e8e4) 55%, transparent);
  color: var(--color-ink, #27272a);
  font: 600 0.9rem/1.35 var(--font-body, 'Manrope', sans-serif);
}

.gallery-desk__upload {
  min-height: 2.85rem;
  border: 0;
  color: #fff;
  background: var(--color-rose, #c98980);
  font: 600 0.78rem/1 var(--font-body, 'Manrope', sans-serif);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
}

.gallery-desk__upload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.gallery-desk__sections {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

.gallery-chip {
  display: grid;
  gap: 0.25rem;
  min-height: 4.25rem;
  padding: 0.9rem;
  border: 1px solid var(--color-line, rgba(39, 37, 42, 0.12));
  background: var(--color-paper, #fffcf8);
  color: var(--color-ink, #27272a);
  text-align: left;
  cursor: pointer;
}

.gallery-chip strong {
  font: 600 0.95rem/1.2 var(--font-body, 'Manrope', sans-serif);
}

.gallery-chip span {
  color: var(--color-rose-dark, #b5746c);
  font-size: 0.8rem;
}

.gallery-chip--active {
  border-color: var(--color-rose, #c98980);
  background: color-mix(in srgb, var(--color-rose-soft, #f0e8e4) 45%, transparent);
}

@media (min-width: 900px) {
  .gallery-desk {
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
    grid-template-areas:
      'intro intro'
      'form sections';
    align-items: start;
  }

  .gallery-desk__intro {
    grid-area: intro;
  }

  .gallery-desk__form {
    grid-area: form;
  }

  .gallery-desk__sections {
    grid-area: sections;
    grid-template-columns: 1fr;
  }
}
</style>
