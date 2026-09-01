<template>
  <BookingStatusCard :booking-public-id="publicId" mode="confirmation" />
</template>

<script setup lang="ts">
import { computed } from 'vue'

const route = useRoute()

definePageMeta({ layout: 'landing' })

useSeoMeta({
  title: 'Booking Confirmation | Shee Aesthetics Meru',
  robots: 'noindex,nofollow',
})

const publicId = computed(() => String(route.params.publicId ?? ''))
</script>
