import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'

import { submitPrivacyRightsRequest } from './privacyRightsApi'

describe('privacyRightsApi', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('document', {
      cookie: 'csrftoken=test-csrf-token',
    } as Document)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('POSTs rights request with CSRF and returns ticket id only', async () => {
    fetchMock.mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: 'Your privacy request was accepted and will be reviewed.',
          ticket_id: 'abc123ticket',
          request_type: 'access',
          status: 'accepted',
          email: 'should-not-echo@example.com',
        }),
        { status: 202, headers: { 'Content-Type': 'application/json' } },
      ),
    )

    const result = await submitPrivacyRightsRequest('http://127.0.0.1:8000', {
      requestType: 'access',
      email: 'guest@example.com',
    })

    expect(result).toMatchObject({
      data: { ticketId: 'abc123ticket' },
    })
    expect(JSON.stringify(result)).not.toMatch(/should-not-echo/)

    const postCall = fetchMock.mock.calls.find((call) => String(call[0]).includes('rights-request'))
    expect(postCall).toBeTruthy()
    const init = postCall?.[1] as RequestInit
    expect(init.credentials).toBe('include')
    expect((init.headers as Record<string, string>)['X-CSRFToken']).toBe('test-csrf-token')
  })
})
