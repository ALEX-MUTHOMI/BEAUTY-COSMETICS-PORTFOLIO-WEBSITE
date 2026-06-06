import { getStaffMe } from '../src/staff/staffPortalApi'

export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/staff/login' || to.path === '/staff/forgot-password' || to.path === '/staff/reset-password') {
    return
  }
  const runtimeConfig = useRuntimeConfig()
  const result = await getStaffMe(runtimeConfig.public.apiBaseUrl)
  if (!result.ok) {
    return navigateTo(`/staff/login?next=${encodeURIComponent(to.fullPath)}`)
  }
})
