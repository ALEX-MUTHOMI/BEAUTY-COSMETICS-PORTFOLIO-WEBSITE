<template>
  <StaffBookingDetail />
</template>

<script setup lang="ts">
import StaffBookingDetail from '../../../src/staff/StaffBookingDetail.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })
useHead({ title: 'Booking Detail | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
