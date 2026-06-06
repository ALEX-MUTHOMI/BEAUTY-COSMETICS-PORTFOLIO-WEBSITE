<template>
  <StaffDashboard />
</template>

<script setup lang="ts">
import StaffDashboard from '../../src/staff/StaffDashboard.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Dashboard | Beauty Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
