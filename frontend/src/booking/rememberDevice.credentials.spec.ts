import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'

import { fetchRememberedDevice } from './rememberDevice'

describe('remember-device credentials', () => {
  const fetchMock = vi.fn<typeof fetch>()

  beforeEach(() => {
    fetchMock.mockReset()
    vi.stubGlobal('fetch', fetchMock)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('sends credentials include so HttpOnly device cookie can travel cross-origin', async () => {
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ remembered: false }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    )

    await fetchRememberedDevice('http://127.0.0.1:8000')

    expect(fetchMock).toHaveBeenCalled()
    const init = fetchMock.mock.calls[0]?.[1] as RequestInit
    expect(init.credentials).toBe('include')
  })
})
