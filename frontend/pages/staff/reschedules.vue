<template>
  <StaffReschedulesWorkspace />
</template>

<script setup lang="ts">
import StaffReschedulesWorkspace from '../../src/staff/StaffReschedulesWorkspace.vue'

definePageMeta({ middleware: ['staff-auth'] })
useHead({ title: 'Staff Reschedules | Beauty Portal', meta: [{ name: 'robots', content: 'noindex,nofollow' }] })
</script>
