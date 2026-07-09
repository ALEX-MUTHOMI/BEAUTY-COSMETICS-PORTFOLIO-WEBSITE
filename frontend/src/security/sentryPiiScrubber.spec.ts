import { describe, expect, it } from 'vitest'
import { scrubPiiText, scrubSentryEvent } from './sentryPiiScrubber'

describe('sentryPiiScrubber — GDPR / DPA redaction', () => {
  it('redacts Kenyan MSISDN and email from free text', () => {
    const text = scrubPiiText('Customer grace@example.com phone +254712345678 paid')
    expect(text).not.toContain('grace@example.com')
    expect(text).not.toContain('+254712345678')
    expect(text).toContain('[REDACTED]')
  })

  it('redacts token-like assignments', () => {
    const text = scrubPiiText('csrftoken=abc123 turnstile=tok-xyz idempotency=hold:1')
    expect(text).not.toContain('abc123')
    expect(text).not.toContain('tok-xyz')
  })

  it('scrubs nested Sentry event payloads', () => {
    const event = scrubSentryEvent({
      message: 'hold failed for grace@example.com',
      extra: { phone: '+254712345678', booking_id: '11111111-1111-4111-8111-111111111111' },
      request: { headers: { Authorization: 'Bearer secret-token' } },
    })
    expect(event).not.toBeNull()
    expect(JSON.stringify(event)).not.toContain('grace@example.com')
    expect(JSON.stringify(event)).not.toContain('+254712345678')
    expect(JSON.stringify(event)).not.toContain('secret-token')
    expect(event?.extra).toMatchObject({ phone: '[REDACTED]' })
  })
})
