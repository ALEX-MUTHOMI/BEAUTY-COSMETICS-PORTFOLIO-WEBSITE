<template>
  <StaffDashboard />
</template>

<script setup lang="ts">
import StaffDashboard from '../../src/staff/StaffDashboard.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })
useHead({ title: 'Staff Dashboard | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
