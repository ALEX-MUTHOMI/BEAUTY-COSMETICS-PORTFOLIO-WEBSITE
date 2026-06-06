<template>
  <StaffLoginPanel
    :api-base-url="runtimeConfig.public.apiBaseUrl"
    :csrf-token="csrfToken"
    next-path="/staff/portal"
    @signed-in="handleSignedIn"
  />
</template>

<script setup lang="ts">
import StaffLoginPanel from '../../src/staff/StaffLoginPanel.vue'

const runtimeConfig = useRuntimeConfig()
const router = useRouter()
const csrfToken = useCookie<string>('csrftoken', {
  sameSite: 'strict',
  secure: process.env.NODE_ENV === 'production',
})

useHead({
  title: 'Staff Sign In | Beauty Portal',
  meta: [
    {
      name: 'robots',
      content: 'noindex,nofollow',
    },
  ],
})

function handleSignedIn(nextPath: string) {
  router.replace(nextPath)
}
</script>
