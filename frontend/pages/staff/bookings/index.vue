<template>
  <StaffBookingsWorkspace :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffBookingsWorkspace from '~/components/staff/StaffBookingsWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({
  title: 'Staff Bookings | Shee Aesthetics',
  meta: [{ name: 'robots', content: 'noindex,nofollow' }],
})
</script>
