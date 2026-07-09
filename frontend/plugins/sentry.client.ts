import { scrubSentryEvent } from '../src/security/sentryPiiScrubber'

/**
 * Empty-safe Sentry scaffold.
 * When NUXT_PUBLIC_SENTRY_DSN is unset, this is a no-op (CI / local).
 * When set, dynamically loads @sentry/vue if present — never blocks boot on missing SDK.
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const dsn = String(config.public.sentryDsn || '').trim()
  if (!dsn) {
    return
  }

  void (async () => {
    try {
      const Sentry = await import(/* @vite-ignore */ '@sentry/vue').catch(() => null)
      if (!Sentry?.init) return
      const nuxtApp = useNuxtApp()
      Sentry.init({
        app: nuxtApp.vueApp,
        dsn,
        environment: String(config.public.sentryEnvironment || 'development'),
        beforeSend(event: Record<string, unknown>) {
          return scrubSentryEvent(event)
        },
      })
    } catch {
      // Fail closed: observability must never break booking checkout.
    }
  })()
})
