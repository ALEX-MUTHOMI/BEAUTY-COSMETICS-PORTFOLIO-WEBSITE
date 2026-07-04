<template>
  <StaffGalleryWorkspace />
</template>

<script setup lang="ts">
import StaffGalleryWorkspace from '../../src/staff/StaffGalleryWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })
useHead({ title: 'Staff Gallery | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
