<template>
  <StaffPaymentsWorkspace :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffPaymentsWorkspace from '~/components/staff/StaffPaymentsWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({ title: 'Staff Payments | Shee Aesthetics', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
