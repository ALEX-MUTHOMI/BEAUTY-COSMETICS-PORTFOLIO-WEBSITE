<template>
  <StaffGalleryWorkspace />
</template>

<script setup lang="ts">
import StaffGalleryWorkspace from '../../src/staff/StaffGalleryWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Gallery | Beauty Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
