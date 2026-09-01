<template>
  <StaffLoginPanel
    :api-base-url="runtimeConfig.public.apiBaseUrl"
    :apple-enabled="runtimeConfig.public.staffAppleEnabled"
    :csrf-token="csrfToken"
    :csrf-bootstrap-failed="csrfBootstrapFailed"
    :google-enabled="runtimeConfig.public.staffGoogleEnabled"
    :sign-in-hint="signInHint"
    next-path="/staff/dashboard"
    @signed-in="handleSignedIn"
    @retry-desk="bootstrapCsrf"
  />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { ensureBookingCsrfToken } from '~/src/booking/bookingCsrf'
import StaffLoginPanel from '~/components/staff/StaffLoginPanel.vue'

definePageMeta({ layout: false })

const runtimeConfig = useRuntimeConfig()
const router = useRouter()
const route = useRoute()
/** Always from API /api/csrf/ JSON — never Nuxt-origin cookie (cross-origin fail-closed). */
const csrfToken = ref('')
const csrfBootstrapFailed = ref(false)

const signInHint = computed(() => {
  const flag = String(route.query.signin || '')
  if (flag === 'unavailable') {
    return 'That sign-in could not be completed. Try email, or ask ops to finish Google/Apple setup.'
  }
  return ''
})

useHead({
  title: 'Staff Sign In | Shee Aesthetics',
  meta: [
    {
      name: 'robots',
      content: 'noindex,nofollow',
    },
  ],
})

async function bootstrapCsrf() {
  csrfBootstrapFailed.value = false
  csrfToken.value =
    (await ensureBookingCsrfToken(String(runtimeConfig.public.apiBaseUrl || ''), {
      forceRefresh: true,
    })) || ''
  csrfBootstrapFailed.value = !csrfToken.value
}

onMounted(() => {
  void bootstrapCsrf()
})

function handleSignedIn(nextPath: string) {
  // Full document navigation after password login so the API session cookie is
  // visible to the next load and a stalled client-route transition cannot leave
  // the desk on “Signing in…”.
  const target = nextPath && nextPath.startsWith('/staff/') ? nextPath : '/staff/dashboard'
  if (typeof window !== 'undefined') {
    window.location.assign(target)
    return
  }
  void router.replace(target)
}
</script>
