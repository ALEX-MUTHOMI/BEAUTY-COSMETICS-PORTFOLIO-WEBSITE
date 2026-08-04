import { scrubSentryEvent } from '../src/security/sentryPiiScrubber'

/**
 * Empty-safe Sentry scaffold (no @sentry/* dependency required for CI builds).
 *
 * When NUXT_PUBLIC_SENTRY_DSN is set later, install `@sentry/vue` and wire init
 * in a follow-up — PII scrubbers are already exported for beforeSend.
 */
export default defineNuxtPlugin(() => {
  const config = useRuntimeConfig()
  const dsn = String(config.public.sentryDsn || '').trim()

  // Always expose scrubber for tests / future SDK wiring; never break booking boot.
  if (import.meta.client) {
    ;(window as Window & { __aestheticOsScrubSentryEvent?: typeof scrubSentryEvent }).__aestheticOsScrubSentryEvent =
      scrubSentryEvent
  }

  if (!dsn) {
    return
  }

  // DSN present but SDK not vendored yet — log once in dev only; fail closed.
  if (import.meta.dev) {
    console.info(
      '[sentry-scaffold] NUXT_PUBLIC_SENTRY_DSN is set; install @sentry/vue and wire init to enable reporting.',
    )
  }
})
