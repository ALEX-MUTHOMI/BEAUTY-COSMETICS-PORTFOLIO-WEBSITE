<template>
  <StaffBookingDetail :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffBookingDetail from '../../../src/staff/StaffBookingDetail.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({
  title: 'Booking Detail | AestheticOS Portal',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})
</script>
