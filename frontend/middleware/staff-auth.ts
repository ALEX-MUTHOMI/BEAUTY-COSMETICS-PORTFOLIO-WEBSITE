import { getStaffMe } from '../src/staff/staffPortalApi'

/**
 * Universal staff gate (SSR + client). Client-only middleware previously allowed
 * no-JS / direct SSR HTML for /staff/* before the session check ran.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/staff/login' || to.path === '/staff/forgot-password' || to.path === '/staff/reset-password') {
    return
  }
  if (!to.path.startsWith('/staff')) {
    return
  }
  const runtimeConfig = useRuntimeConfig()
  const result = await getStaffMe(runtimeConfig.public.apiBaseUrl)
  if (!result.ok) {
    return navigateTo(`/staff/login?next=${encodeURIComponent(to.fullPath)}`)
  }
})
