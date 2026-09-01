/**
 * Fail-closed public /book routes until NUXT_PUBLIC_BOOKING_ENABLED=true.
 */
import { isPublicBookingEnabled } from '~/src/booking/publicBookingGate'

export default defineNuxtRouteMiddleware((to) => {
  const config = useRuntimeConfig()
  if (isPublicBookingEnabled(config.public.bookingEnabled)) return
  if (to.path === '/book' || to.path.startsWith('/book/')) {
    if (import.meta.server) {
      setResponseStatus(503)
    }
  }
})
