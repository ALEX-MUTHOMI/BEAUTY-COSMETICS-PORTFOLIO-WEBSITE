<template>
  <StaffSettingsSecurity :api-base-url="apiBaseUrl" />
</template>

<script setup lang="ts">
import StaffSettingsSecurity from '~/components/staff/StaffSettingsSecurity.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })

const runtimeConfig = useRuntimeConfig()
const apiBaseUrl = String(runtimeConfig.public.apiBaseUrl || '')

useHead({ title: 'Staff Settings | Shee Aesthetics', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
