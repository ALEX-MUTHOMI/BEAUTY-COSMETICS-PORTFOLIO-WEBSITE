<template>
  <SupportPage />
</template>

<script setup lang="ts">
/**
 * Contact Page
 * Renders the primary support and contact interface for users to reach out.
 */
import SupportPage from './support.vue'

definePageMeta({ layout: 'landing' })

useHead({
  title: 'Contact Us | Shee Aesthetics Meru',
  meta: [
    {
      name: 'description',
      content: 'Contact Shee Aesthetics beauty salon and wellness studio in Meru Town, Kenya. Direct WhatsApp, phone, and booking support.',
    },
  ],
})
</script>
