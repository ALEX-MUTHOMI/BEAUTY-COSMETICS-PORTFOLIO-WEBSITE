// ==============================================================================
// Enterprise Nuxt 3 SSR and Security Configuration
// ==============================================================================
export default defineNuxtConfig({
  // Enforce Server-Side Rendering (SSR) for optimal SEO crawlability and index ranking
  ssr: true,

  // Runtime environment configuration parameters
  runtimeConfig: {
    // Keys exposed only on the server-side context
    turnstileSecretKey: process.env.NUXT_TURNSTILE_SECRET_KEY || '1x0000000000000000000000000000000AA',

    // Keys exposed on both client and server contexts
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
      staffAppleEnabled: process.env.NUXT_PUBLIC_STAFF_APPLE_ENABLED === 'true',
      staffGoogleEnabled: process.env.NUXT_PUBLIC_STAFF_GOOGLE_ENABLED === 'true',
      turnstileSiteKey: process.env.NUXT_PUBLIC_TURNSTILE_SITE_KEY || '1x0000000000000000000000000000000AA',
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
  security: {
    headers: {
      contentSecurityPolicy: {
        'script-src': [
          "'self'",
          "https://challenges.cloudflare.com/turnstile/", // Cloudflare Challenge Script
          "https://static.cloudflareinsights.com"
        ],
        'frame-src': [
          "'self'",
          "https://challenges.cloudflare.com/turnstile/" // Cloudflare Challenge Frame
        ]
      },
      crossOriginEmbedderPolicy: 'unsafe-none',
      crossOriginOpenerPolicy: 'same-origin',
      xFrameOptions: 'DENY',
      xContentTypeOptions: 'nosniff',
      referrerPolicy: 'no-referrer-when-downgrade'
    },
    rateLimiter: {
      tokensPerInterval: 150,
      interval: 'hour'
    }
  },

  // Global application header and metadata registrations
  app: {
    head: {
      title: 'Premium Beauty & Cosmetics Portfolio | Booking Platform',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Discover premium cosmetics and secure instant aesthetic bookings with Safaricom M-Pesa express integration.' }
      ],
      script: [
        // Injection fallback for Cloudflare Turnstile bot verification challenge API
        {
          src: 'https://challenges.cloudflare.com/turnstile/v0/api.js',
          async: true,
          defer: true
        }
      ]
    }
  },

  devtools: { enabled: true }
})
