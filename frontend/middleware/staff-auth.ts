/**
 * Middleware: staff-auth
 * Ensures that the user has staff privileges before accessing routes.
 */
import { getStaffMe } from '../src/staff/staffPortalApi'

/**
 * Staff desk gate. Session cookies live on the API origin (cross-port on local,
 * cross-origin in compose). Nuxt SSR inside the frontend container cannot reach
 * `localhost:8000` or forward those cookies, so enforcement is client-only.
 * Anonymous full-page loads still resolve to the login screen after hydration.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/staff/login' || to.path === '/staff/forgot-password' || to.path === '/staff/reset-password') {
    return
  }
  if (!to.path.startsWith('/staff')) {
    return
  }
  if (import.meta.server) {
    return
  }

  const runtimeConfig = useRuntimeConfig()
  try {
    const result = await getStaffMe(runtimeConfig.public.apiBaseUrl)
    if (!result.ok) {
      return navigateTo(`/staff/login?next=${encodeURIComponent(to.fullPath)}`)
    }
  } catch {
    return navigateTo(`/staff/login?next=${encodeURIComponent(to.fullPath)}`)
  }
})

