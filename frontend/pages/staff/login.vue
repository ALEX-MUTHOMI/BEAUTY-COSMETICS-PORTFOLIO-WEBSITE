<template>
  <StaffLoginPanel
    :api-base-url="runtimeConfig.public.apiBaseUrl"
    :apple-enabled="runtimeConfig.public.staffAppleEnabled"
    :csrf-token="csrfToken"
    :google-enabled="runtimeConfig.public.staffGoogleEnabled"
    next-path="/staff/dashboard"
    @signed-in="handleSignedIn"
  />
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { ensureBookingCsrfToken } from '../../src/booking/bookingCsrf'
import StaffLoginPanel from '../../src/staff/StaffLoginPanel.vue'

definePageMeta({ layout: false })

const runtimeConfig = useRuntimeConfig()
const router = useRouter()
/** Always from API /api/csrf/ JSON — never Nuxt-origin cookie (cross-origin fail-closed). */
const csrfToken = ref('')

useHead({
  title: 'Staff Sign In | Shee Aesthetics',
  meta: [
    {
      name: 'robots',
      content: 'noindex,nofollow',
    },
  ],
})

onMounted(async () => {
  csrfToken.value =
    (await ensureBookingCsrfToken(String(runtimeConfig.public.apiBaseUrl || ''))) || ''
})

function handleSignedIn(nextPath: string) {
  router.replace(nextPath)
}
</script>
