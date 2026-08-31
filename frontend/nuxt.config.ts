// ==============================================================================
// Enterprise Nuxt 3 SSR and Security Configuration
// ==============================================================================
import { fileURLToPath } from 'node:url'

/** Additive report-only CSP (keeps enforcing CSP). Operator collector URL via env. */
function buildCspReportOnlyHeader(): string | undefined {
  if (process.env.NUXT_PUBLIC_CSP_REPORT_ONLY !== 'true') return undefined
  const reportUri =
    process.env.NUXT_PUBLIC_CSP_REPORT_URI?.trim() || 'https://sheeaesthetics.co.ke/csp-report'
  const directives = [
    "default-src 'self'",
    "script-src 'self' 'strict-dynamic' https://challenges.cloudflare.com/turnstile/ https://static.cloudflareinsights.com",
    "object-src 'none'",
    "base-uri 'none'",
    "connect-src 'self' https://challenges.cloudflare.com",
    `report-uri ${reportUri}`,
  ]
  if (process.env.NUXT_PUBLIC_TRUSTED_TYPES_PREP === 'true') {
    directives.push("require-trusted-types-for 'script'")
  }
  return directives.join('; ')
}

const cspReportOnlyHeader = buildCspReportOnlyHeader()

export default defineNuxtConfig({
  // Enforce Server-Side Rendering (SSR) for optimal SEO crawlability and index ranking
  ssr: true,
  experimental: {
    appManifest: false,
  },

  // Staff desk uses credentialed calls to the API origin; SPA mode avoids SSR
  // session checks that cannot see cross-origin API cookies inside Docker.
  routeRules: {
    '/staff/**': { ssr: false },
    '/images/**': {
      headers: {
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    },
    ...(cspReportOnlyHeader
      ? {
          '/**': {
            headers: {
              'Content-Security-Policy-Report-Only': cspReportOnlyHeader,
            },
          },
        }
      : {}),
  },

  // Mellis theme design tokens shared across the public site
  css: ['~/assets/css/tokens.css', '~/assets/css/motion.css', '~/assets/css/loader.css'],

  // Match tsconfig `@/*` → `src/*` for shared landing modules and tests
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url)),
  },

  // Runtime environment configuration parameters
  runtimeConfig: {
    // Keys exposed only on the server-side context
    turnstileSecretKey: process.env.NUXT_TURNSTILE_SECRET_KEY || '1x0000000000000000000000000000000AA',

    // Keys exposed on both client and server contexts
    public: {
      // Single source of truth for Nuxt (:3000) → Django (:8000). Never wildcard.
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'https://sheeaesthetics.co.ke',
      // Empty-safe Sentry scaffold — live DSN via secrets later (PII scrubbers always on).
      sentryDsn: process.env.NUXT_PUBLIC_SENTRY_DSN || '',
      sentryEnvironment: process.env.NUXT_PUBLIC_SENTRY_ENVIRONMENT || process.env.NODE_ENV || 'development',
      staffAppleEnabled: process.env.NUXT_PUBLIC_STAFF_APPLE_ENABLED === 'true',
      staffGoogleEnabled: process.env.NUXT_PUBLIC_STAFF_GOOGLE_ENABLED === 'true',
      turnstileSiteKey: process.env.NUXT_PUBLIC_TURNSTILE_SITE_KEY || '1x0000000000000000000000000000000AA',
      /** Live Meru WhatsApp E.164 digits only (no +). Empty/placeholder = CTAs fail closed. */
      whatsappE164: process.env.NUXT_PUBLIC_WHATSAPP_E164 || '',
    },
  },

  // Modules registration for perimeter protection (BOT Mitigation, CSRF, and HTTP Headers)
  modules: [
    '@nuxtjs/turnstile',
    'nuxt-csurf',
    'nuxt-security'
  ],

  // 1. Cloudflare Turnstile Configuration
  turnstile: {
    siteKey: process.env.NUXT_PUBLIC_TURNSTILE_SITE_KEY || '1x0000000000000000000000000000000AA',
    addScript: true // Automatically inject Turnstile scripts to route templates
  },

  // 2. Strict Cross-Site Request Forgery (CSRF) protection boundary
  csurf: {
    https: process.env.NODE_ENV === 'production',
    cookie: {
      path: '/',
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict'
    }
  },

  // 3. Strict Security Headers auditing (mitigating XSS, Clickjacking, and injection vectors)
  // CSP report-only soak + Trusted Types prep are env-gated and additive — enforcing CSP stays on.
  // NUXT_PUBLIC_CSP_REPORT_ONLY=true → also emit Content-Security-Policy-Report-Only (see routeRules).
  // NUXT_PUBLIC_TRUSTED_TYPES_PREP=true → include require-trusted-types-for 'script' in that report-only policy.
  // Reporting endpoint is operator-owned (Cloudflare / collector); origin does not accept CSP reports in-app.
  security: {
    nonce: true,
    headers: {
      contentSecurityPolicy: {
        'script-src': [
          "'self'",
          "'strict-dynamic'",
          "'nonce-{{nonce}}'",
          'https://challenges.cloudflare.com/turnstile/',
          'https://static.cloudflareinsights.com',
        ],
        'frame-src': [
          "'self'",
          'https://challenges.cloudflare.com/turnstile/',
          'https://www.google.com/',
          'https://maps.google.com/',
        ],
        // Close plugin / base-tag injection vectors (CSP Level 2+).
        'object-src': ["'none'"],
        'base-uri': ["'none'"],
        // Browser fetches: same origin + Django API + Turnstile + optional Sentry.
        'connect-src': [
          "'self'",
          'https://challenges.cloudflare.com',
          ...(process.env.NUXT_PUBLIC_API_BASE_URL
            ? [process.env.NUXT_PUBLIC_API_BASE_URL.replace(/\/$/, '')]
            : ['http://127.0.0.1:8000', 'http://localhost:8000']),
          ...(process.env.NUXT_PUBLIC_SENTRY_DSN ? ['https://*.ingest.sentry.io'] : []),
        ],
        // Enforcing Trusted Types only when explicitly enabled (can break Vue sinks — prefer report-only soak first).
        ...(process.env.NUXT_PUBLIC_TRUSTED_TYPES_ENFORCE === 'true'
          ? { 'require-trusted-types-for': ["'script'"] }
          : {}),
      },
      permissionsPolicy: {
        camera: [],
        microphone: [],
        geolocation: [],
      },
      crossOriginEmbedderPolicy: 'unsafe-none',
      crossOriginOpenerPolicy: 'same-origin',
      xFrameOptions: 'DENY',
      xContentTypeOptions: 'nosniff',
      referrerPolicy: 'no-referrer-when-downgrade',
    },
    rateLimiter: {
      tokensPerInterval: 150,
      interval: 'hour',
    },
  },

  // Global application header and metadata registrations
  app: {
    head: {
      title: 'Shee Aesthetics | Facials, Waxing, Massage & Makeup',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Shee Aesthetics — facials, waxing, massage and makeup. Full packages Tue & Wed. Single treatments Mon, Thu–Sat.',
        },
      ],
      // Turnstile's challenge script is injected once by the `turnstile.addScript`
      // option above. A second manual <script> tag here previously duplicated
      // that load on every page.
    }
  },

  devtools: { enabled: process.env.NODE_ENV !== 'production' }
})
