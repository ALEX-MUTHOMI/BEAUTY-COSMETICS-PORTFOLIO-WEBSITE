<template>
  <StaffBookingDetail :api-base-url="apiBaseUrl" :public-booking-id="publicBookingId" />
</template>

<script setup lang="ts">
import StaffBookingDetail from '../../../src/staff/StaffBookingDetail.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const route = useRoute()
const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')
const publicBookingId = String(route.params.publicId || '')

useHead({
  title: 'Booking Detail | Shee Aesthetics',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})
</script>
