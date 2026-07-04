<template>
  <StaffReschedulesWorkspace />
</template>

<script setup lang="ts">
import StaffReschedulesWorkspace from '../../src/staff/StaffReschedulesWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })
useHead({ title: 'Staff Reschedules | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
