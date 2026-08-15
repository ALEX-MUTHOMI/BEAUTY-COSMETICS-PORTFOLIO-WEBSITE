<template>
  <StaffReschedulesWorkspace :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffReschedulesWorkspace from '~/components/staff/StaffReschedulesWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({ title: 'Staff Reschedules | Shee Aesthetics', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
