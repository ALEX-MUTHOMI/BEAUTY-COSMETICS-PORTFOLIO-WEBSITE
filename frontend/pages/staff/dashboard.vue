<template>
  <StaffDashboard :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffDashboard from '~/components/staff/StaffDashboard.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({ title: 'Staff Dashboard | Shee Aesthetics', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
