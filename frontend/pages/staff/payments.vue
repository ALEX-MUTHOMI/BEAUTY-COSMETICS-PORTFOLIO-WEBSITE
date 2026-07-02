<template>
  <StaffPaymentsWorkspace />
</template>

<script setup lang="ts">
import StaffPaymentsWorkspace from '../../src/staff/StaffPaymentsWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Payments | AestheticOS Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
