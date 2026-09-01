import { describe, expect, it } from 'vitest'
import { bookingApiBase } from './bookingCsrf'
import { resolveTrustedApiBaseUrl, trustedApiOriginOrEmpty } from './bookingApiBaseTrust'

describe('resolveTrustedApiBaseUrl — host reroute red team', () => {
  it('accepts localhost:8000 and strips path drift', () => {
    expect(resolveTrustedApiBaseUrl('http://localhost:8000/api/evil')).toEqual({
      ok: true,
      origin: 'http://localhost:8000',
    })
  })

  it('rejects javascript and data schemes', () => {
    expect(resolveTrustedApiBaseUrl('javascript:alert(1)').ok).toBe(false)
    expect(resolveTrustedApiBaseUrl('data:text/html,hi').ok).toBe(false)
  })

  it('rejects credentials-in-URL and protocol-relative hosts', () => {
    expect(resolveTrustedApiBaseUrl('http://user:pass@localhost:8000').ok).toBe(false)
    expect(resolveTrustedApiBaseUrl('//evil.example').ok).toBe(false)
  })

  it('treats empty and same-origin as relative page origin', () => {
    expect(resolveTrustedApiBaseUrl('')).toEqual({ ok: true, origin: '' })
    expect(resolveTrustedApiBaseUrl('same-origin')).toEqual({ ok: true, origin: '' })
    expect(resolveTrustedApiBaseUrl('/')).toEqual({ ok: true, origin: '' })
  })

  it('rejects traversal on an absolute API origin', () => {
    expect(resolveTrustedApiBaseUrl('http://localhost:8000/../admin').ok).toBe(false)
  })

  it('trustedApiOriginOrEmpty fails closed on garbage and denylisted hosts', () => {
    expect(trustedApiOriginOrEmpty('https://evil.example')).toBe('')
    expect(trustedApiOriginOrEmpty('not a url')).toBe('')
    expect(trustedApiOriginOrEmpty('http://127.0.0.1:8000')).toBe('http://127.0.0.1:8000')
  })

  it('bookingApiBase stays relative for same-origin and strips docker service hosts', () => {
    expect(bookingApiBase('')).toBe('')
    expect(bookingApiBase('same-origin')).toBe('')
    expect(bookingApiBase('http://web:8000')).toBe('')
    expect(bookingApiBase('http://127.0.0.1:8000')).toBe('http://127.0.0.1:8000')
  })
})
