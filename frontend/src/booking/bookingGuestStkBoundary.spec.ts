import { readFileSync, readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'

import { initiateBookingGuestStk } from './bookingWriteApi'

const OWNER_STK_PATTERN = /\/api\/checkout\/sessions\/[^"'`\s]+\/mpesa\/stk\//
const GUEST_STK_PATH = '/api/bookings/checkout/mpesa/stk/'

function listSourceFiles(dir: string): string[] {
  const entries = readdirSync(dir)
  const files: string[] = []
  for (const entry of entries) {
    const absolute = join(dir, entry)
    const stats = statSync(absolute)
    if (stats.isDirectory()) {
      if (entry === 'node_modules' || entry === '.nuxt' || entry === 'dist') continue
      files.push(...listSourceFiles(absolute))
      continue
    }
    if (/\.(ts|vue|js|mjs)$/.test(entry) && !entry.endsWith('.spec.ts')) {
      files.push(absolute)
    }
  }
  return files
}

describe('guest money-path STK boundary', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('posts guest STK only to the public bookings route with CSRF', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      status: 202,
      json: async () => ({
        stk: {
          booking_public_id: '33333333-3333-4333-8333-333333333333',
          checkout_public_id: '44444444-4444-4444-8444-444444444444',
          attempt_id: '55555555-5555-4555-8555-555555555555',
          payment_status: 'awaiting_payment',
          next_action: 'await_stk_confirmation',
        },
      }),
    } as Response)

    const result = await initiateBookingGuestStk(
      'https://api.example.com',
      {
        bookingPublicId: '33333333-3333-4333-8333-333333333333',
        checkoutPublicId: '44444444-4444-4444-8444-444444444444',
        phoneNumber: '+254712345678',
        idempotencyKey: 'stk-key-1',
      },
      'csrf-token',
    )

    expect('data' in result).toBe(true)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(url).toContain(GUEST_STK_PATH)
    expect(url).not.toMatch(OWNER_STK_PATTERN)
    expect(init.method).toBe('POST')
    expect(init.headers).toEqual(
      expect.objectContaining({
        'X-CSRFToken': 'csrf-token',
      }),
    )
  })

  it('keeps frontend sources off the owner IsAuthenticated STK route', () => {
    const roots = [join(process.cwd(), 'src'), join(process.cwd(), 'pages'), join(process.cwd(), 'components')]
    const violations: string[] = []
    for (const root of roots) {
      for (const file of listSourceFiles(root)) {
        const source = readFileSync(file, 'utf8')
        if (OWNER_STK_PATTERN.test(source)) {
          violations.push(file.replace(/\\/g, '/'))
        }
      }
    }
    expect(violations).toEqual([])
  })
})
