import { test, expect, type Page, type Route } from '@playwright/test'

/**
 * Deterministic money-path: hold → checkout → guest STK → status/confirmation.
 * Stubbed Django booking APIs (fake provider). Does not require a live API.
 * Existing readiness smoke remains for when the real stack is up.
 */
const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:3000'
const API_URL = process.env.NUXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'

const BOOKING_ID = '11111111-1111-4111-8111-111111111111'
const CHECKOUT_ID = '22222222-2222-4222-8222-222222222222'
const ATTEMPT_ID = '33333333-3333-4333-8333-333333333333'
const SERVICE_ID = '44444444-4444-4444-8444-444444444444'
const RESOURCE_ID = '55555555-5555-4555-8555-555555555555'
const SLOT_DAY = '2026-08-12' // Wednesday — package day
const SLOT_START = '2026-08-12T04:00:00+00:00'
const SLOT_END = '2026-08-12T05:00:00+00:00'

async function apiHealthy(request: import('@playwright/test').APIRequestContext): Promise<boolean> {
  try {
    const res = await request.get(`${API_URL}/health/`, { timeout: 5000 })
    return res.ok()
  } catch {
    return false
  }
}

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

async function installMoneyPathFixtures(page: Page) {
  const apiHost = new URL(API_URL).origin

  await page.route(`${apiHost}/api/csrf/**`, (route) =>
    json(route, { csrf_token: 'e2e-csrf-token-fixture' }),
  )

  await page.route(`${apiHost}/api/bookings/catalog/resolve-handoff/**`, (route) =>
    json(route, {
      selection: {
        selection_type: 'full_package',
        public_id: SERVICE_ID,
        slug: 'classic-full-package',
        name: 'Classic Full Package',
        duration_minutes: 180,
      },
    }),
  )

  await page.route(`${apiHost}/api/bookings/calendar/**`, (route) =>
    json(route, {
      calendar: {
        timezone: 'Africa/Nairobi',
        layout: 'package_pairs',
        range: { start: SLOT_DAY, end: SLOT_DAY },
        selection: {
          type: 'full_package',
          public_id: SERVICE_ID,
          slug: 'classic-full-package',
          name: 'Classic Full Package',
        },
        days: [
          {
            date: SLOT_DAY,
            weekday: 3,
            day_type: 'full_package',
            status: 'available',
            reason_code: null,
            slot_count: 2,
            capacity: { max: 3, booked: 0, remaining: 3 },
          },
        ],
        weeks: [
          {
            week_start: SLOT_DAY,
            days: [
              {
                date: SLOT_DAY,
                weekday: 3,
                day_type: 'full_package',
                status: 'available',
                reason_code: null,
                slot_count: 2,
                capacity: { max: 3, booked: 0, remaining: 3 },
              },
            ],
          },
        ],
      },
    }),
  )

  await page.route(`${apiHost}/api/bookings/availability/**`, (route) =>
    json(route, {
      availability: [
        {
          date: SLOT_DAY,
          slots: [
            {
              starts_at: SLOT_START,
              ends_at: SLOT_END,
              duration_minutes: 60,
              buffer_minutes: 0,
              resource_public_id: RESOURCE_ID,
              service_public_id: SERVICE_ID,
            },
          ],
        },
      ],
    }),
  )

  await page.route(`${apiHost}/api/bookings/policy-acceptance-text/**`, (route) =>
    json(route, {
      checkbox_text: 'I agree to the Shee Aesthetics booking policy for this visit.',
    }),
  )

  await page.route(`${apiHost}/api/customers/remembered-device/**`, (route) =>
    json(route, { remembered: false }),
  )

  await page.route(`${apiHost}/api/bookings/holds/**`, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return json(route, {
      booking: {
        booking_public_id: BOOKING_ID,
        status: 'held',
        hold_expires_at: '2026-08-12T05:30:00+00:00',
        hold_ttl_minutes: 15,
        next_action: 'checkout_required',
      },
    })
  })

  await page.route(`${apiHost}/api/bookings/checkout/mpesa/stk/**`, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return json(route, {
      stk: {
        booking_public_id: BOOKING_ID,
        checkout_public_id: CHECKOUT_ID,
        attempt_id: ATTEMPT_ID,
        payment_status: 'stk_sent',
        next_action: 'await_stk_confirmation',
      },
    })
  })

  await page.route(`${apiHost}/api/bookings/checkout/**`, async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    const path = new URL(route.request().url()).pathname
    if (path.includes('/mpesa/stk')) return route.fallback()
    return json(route, {
      checkout: {
        booking_public_id: BOOKING_ID,
        checkout_public_id: CHECKOUT_ID,
        status_url: `/booking/status/${BOOKING_ID}/`,
        amount: '8500',
        currency: 'KES',
        next_action: 'initiate_payment',
      },
    })
  })

  await page.route(`${apiHost}/api/bookings/status/${BOOKING_ID}/**`, (route) =>
    json(route, {
      booking_reference: BOOKING_ID,
      booking_status: 'confirmed',
      payment_status: 'paid',
      next_action: 'none',
      service: { name: 'Classic Full Package' },
      schedule: { date: SLOT_DAY, start_time_eat: '07:00' },
    }),
  )

  // Fake Turnstile so guest STK can submit without Cloudflare widget flakiness.
  await page.addInitScript(() => {
    const install = () => {
      const api = {
        render(_el: unknown, opts?: { callback?: (token: string) => void }) {
          queueMicrotask(() => opts?.callback?.('XXXX.DUMMY.TOKEN.XXXX'))
          return 'e2e-widget'
        },
        ready(cb: () => void) {
          queueMicrotask(cb)
        },
        reset() {},
        remove() {},
        getResponse() {
          return 'XXXX.DUMMY.TOKEN.XXXX'
        },
      }
      Object.defineProperty(window, 'turnstile', {
        configurable: true,
        writable: true,
        value: api,
      })
    }
    install()
  })

  await page.route('https://challenges.cloudflare.com/**', async (route) => {
    if (route.request().resourceType() === 'script') {
      return route.fulfill({
        status: 200,
        contentType: 'application/javascript',
        body: 'window.turnstile=window.turnstile||{render:function(e,o){setTimeout(function(){o&&o.callback&&o.callback("XXXX.DUMMY.TOKEN.XXXX")},0);return"e2e"},ready:function(c){c&&c()},reset:function(){},remove:function(){},getResponse:function(){return"XXXX.DUMMY.TOKEN.XXXX"}};',
      })
    }
    return route.fulfill({ status: 204, body: '' })
  })
}

async function seedTurnstileToken(page: Page) {
  await page.evaluate(() => {
    const selectors = [
      'input[name="cf-turnstile-response"]',
      'textarea[name="cf-turnstile-response"]',
      '[name="cf-turnstile-response"]',
    ]
    for (const sel of selectors) {
      const el = document.querySelector(sel) as HTMLInputElement | null
      if (el) {
        el.value = 'XXXX.DUMMY.TOKEN.XXXX'
        el.dispatchEvent(new Event('input', { bubbles: true }))
        el.dispatchEvent(new Event('change', { bubbles: true }))
      }
    }

    const walk = (root: Element | null) => {
      if (!root) return
      const anyEl = root as unknown as {
        __vueParentComponent?: { setupState?: Record<string, { value?: unknown }> }
      }
      const setup = anyEl.__vueParentComponent?.setupState
      if (setup?.turnstileToken && typeof setup.turnstileToken === 'object') {
        setup.turnstileToken.value = 'XXXX.DUMMY.TOKEN.XXXX'
      }
      if (setup?.turnstileRequired && typeof setup.turnstileRequired === 'object') {
        // Keep required true but token set — prefer token over disabling the gate.
      }
      for (const child of Array.from(root.children)) walk(child)
    }
    walk(document.body)
  })
  await page.waitForTimeout(300)
}

test.describe('Book money-path smoke (thin client readiness)', () => {
  test('book package path loads against a healthy Django API', async ({ page, request }) => {
    test.skip(!(await apiHealthy(request)), 'Django API not reachable for money-path smoke')

    const response = await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })
    expect(response?.ok()).toBeTruthy()
    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible({
      timeout: 20000,
    })
    await expect(page.getByRole('heading', { name: /Date & time/i })).toBeVisible()
    await expect(page.locator('body')).not.toContainText(/traceback|Internal Server Error/i)

    const continueBtn = page.locator('button.book-continue').first()
    await expect(continueBtn).toBeVisible()
    await expect(continueBtn).toBeDisabled()
  })
})

test.describe('Book money-path fixtures (hold → STK → status)', () => {
  test('completes guest hold, checkout, STK, and confirmation with stubbed APIs', async ({
    page,
  }) => {
    test.setTimeout(90_000)
    await installMoneyPathFixtures(page)

    await page.goto(`${BASE_URL}/book/package/classic-full-package`, {
      waitUntil: 'domcontentloaded',
    })

    await expect(page.getByRole('heading', { name: 'Classic Full Package' })).toBeVisible({
      timeout: 20000,
    })
    await expect(page.getByRole('heading', { name: /Date & time/i })).toBeVisible()

    const dayChip = page.locator('button.flo-chip').filter({ hasNot: page.locator('[disabled]') }).first()
    await expect(dayChip).toBeVisible({ timeout: 15000 })
    await dayChip.click()

    const slotBtn = page.locator('button.flo-slots__btn').first()
    await expect(slotBtn).toBeVisible({ timeout: 15000 })
    await slotBtn.click()

    const continueBtn = page.locator('button.book-continue').first()
    await expect(continueBtn).toBeEnabled({ timeout: 10000 })
    await continueBtn.click()

    await expect(page.getByRole('heading', { name: /Your details/i })).toBeVisible({
      timeout: 15000,
    })

    await page.locator('input[name="full_name"]').fill('Grace Meru')
    await page.locator('input[name="email"]').fill('grace.e2e@example.com')
    await page.locator('input[name="email_confirm"]').fill('grace.e2e@example.com')
    await page.locator('input[name="phone"]').fill('0712345678')
    await page.locator('.book-customer__policy input[type="checkbox"]').check()

    await seedTurnstileToken(page)

    const submit = page.locator('button.book-customer__submit')
    await expect(submit).toBeEnabled({ timeout: 20000 })
    await submit.click()

    await expect(page).toHaveURL(new RegExp(`/booking/(confirmation|status)/${BOOKING_ID}`), {
      timeout: 20000,
    })
    await expect(page.getByText(/You are booked|Booking confirmed/i)).toBeVisible({
      timeout: 20000,
    })
    await expect(page.locator('body')).not.toContainText(/traceback|Internal Server Error/i)
  })
})
