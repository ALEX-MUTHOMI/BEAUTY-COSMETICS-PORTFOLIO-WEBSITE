<template>
  <BookingClosedNotice v-if="!bookingEnabled" />
  <BookCheckoutPage v-else :handoff="handoff" />
</template>

<script setup lang="ts">
import BookCheckoutPage from '~/components/booking/BookCheckoutPage.vue'
import BookingClosedNotice from '~/components/booking/BookingClosedNotice.vue'
import { isPublicBookingEnabled } from '~/src/booking/publicBookingGate'
import {
  parseBookPathParams,
  SERVICES_BOOK_ENTRY,
  type ResolvedBookHandoff,
} from '@/landing/bookingHandoff'

definePageMeta({ layout: 'landing' })

const route = useRoute()
const config = useRuntimeConfig()
const siteUrl = (config.public.siteUrl as string) || 'https://sheeaesthetics.co.ke'
const bookingEnabled = isPublicBookingEnabled(config.public.bookingEnabled)

const parsed = parseBookPathParams({
  plan: route.params.plan,
  date: route.query.date,
})

if (!parsed) {
  await navigateTo(SERVICES_BOOK_ENTRY, { redirectCode: 302, replace: true })
}

const handoff = parsed as ResolvedBookHandoff
const planName = handoff.planName || 'Full package'
const path = `/book/package/${handoff.plan}`

useSeoMeta({
  title: `Book ${planName} | Shee Aesthetics Meru`,
  description: `See live availability and book ${planName} at Shee Aesthetics Meru. Package days Tuesday and Wednesday. Pay online to confirm.`,
  robots: 'noindex,follow',
})
useHead({ link: [{ rel: 'canonical', href: `${siteUrl}${path}` }] })
</script>
