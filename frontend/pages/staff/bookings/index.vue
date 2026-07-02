<template>
  <StaffBookingsWorkspace />
</template>

<script setup lang="ts">
import StaffBookingsWorkspace from '../../../src/staff/StaffBookingsWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Bookings | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
