<template>
  <StaffSettingsSecurity />
</template>

<script setup lang="ts">
import StaffSettingsSecurity from '../../../src/staff/StaffSettingsSecurity.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Settings | Beauty Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
