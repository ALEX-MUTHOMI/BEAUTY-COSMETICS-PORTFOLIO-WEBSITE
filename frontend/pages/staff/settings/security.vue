<template>
  <StaffSettingsSecurity />
</template>

<script setup lang="ts">
import StaffSettingsSecurity from '../../../src/staff/StaffSettingsSecurity.vue'

definePageMeta({ middleware: ['staff-auth'], layout: false })
useHead({ title: 'Staff Security | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
