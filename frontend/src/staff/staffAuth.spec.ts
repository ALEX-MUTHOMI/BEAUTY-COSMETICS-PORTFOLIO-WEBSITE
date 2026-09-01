import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import StaffLoginPanel from '../../components/staff/StaffLoginPanel.vue'
import {
  buildStaffAppleLoginUrl,
  buildStaffGoogleLoginUrl,
  buildStaffLoginUrl,
  confirmStaffPasswordReset,
  requestStaffPasswordReset,
  sanitizeNextPath,
  staffPasswordLogin,
  storageContainsStaffSecrets,
} from './staffAuth'
import { createClickGate } from './botGuard'

describe('staff auth client security contract', () => {
  it('builds bounded backend URLs without exposing tokens in browser storage', async () => {
    expect(buildStaffLoginUrl('https://api.example.com/')).toBe('https://api.example.com/api/staff/auth/login/')
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', '/staff/dashboard')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffAppleLoginUrl('https://api.example.com/', '/staff/settings/security')).toBe(
      'https://api.example.com/api/staff/auth/apple/start/?next=%2Fstaff%2Fsettings%2Fsecurity',
    )
    expect(buildStaffGoogleLoginUrl('https://api.example.com/', 'https://evil.example')).toBe(
      'https://api.example.com/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffGoogleLoginUrl('http://web:8000', '/staff/dashboard')).toBe(
      '/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard',
    )
    expect(buildStaffLoginUrl('http://web:8000')).toBe('/api/staff/auth/login/')
    expect(sanitizeNextPath('/staff/bookings/BK-1001')).toBe('/staff/bookings/BK-1001')
    expect(sanitizeNextPath('/customer/bookings')).toBe('/staff/dashboard')
    expect(sanitizeNextPath('//evil.example/staff/dashboard')).toBe('/staff/dashboard')
    expect(sanitizeNextPath('/staff/dashboard\r\nLocation:https://evil.example')).toBe('/staff/dashboard')

    localStorage.clear()
    sessionStorage.clear()
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })

  it('posts password login with cookie credentials and CSRF but returns generic failures', async () => {
    const fetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 400,
      json: vi.fn<() => Promise<unknown>>(),
    } as unknown as Response)

    const result = await staffPasswordLogin(
      'https://api.example.com',
      {
        email: ' BEAUTICIAN@EXAMPLE.COM ',
        password: 'correct horse battery staple',
        csrfToken: 'csrf-token',
      },
      fetcher,
    )

    expect(result).toEqual({
      ok: false,
      nextPath: '',
      message: 'Invalid credentials.',
      displayName: '',
      retryable: false,
    })
    expect(fetcher).toHaveBeenCalledWith(
      'https://api.example.com/api/staff/auth/login/',
      expect.objectContaining({
        credentials: 'include',
        method: 'POST',
        headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }),
      }),
    )
    const firstCall = fetcher.mock.calls.at(0)
    expect(firstCall).toBeDefined()
    const requestOptions = firstCall?.[1] as RequestInit
    expect(JSON.parse(String(requestOptions.body))).toEqual({
      email: 'beautician@example.com',
      password: 'correct horse battery staple',
      turnstile_token: '',
    })
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
  })

  it('maps rate-limit, availability, CSRF/session, and network failures separately from invalid credentials', async () => {
    const rateLimited = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 429,
      json: vi.fn<() => Promise<unknown>>(),
    } as unknown as Response)
    expect(
      (
        await staffPasswordLogin(
          'https://api.example.com',
          { email: 'a@b.com', password: 'x'.repeat(16), csrfToken: 't' },
          rateLimited,
        )
      ).message,
    ).toBe('Please try again later.')

    const unavailable = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 503,
      json: vi.fn<() => Promise<unknown>>(),
    } as unknown as Response)
    const unavailableResult = await staffPasswordLogin(
      'https://api.example.com',
      { email: 'a@b.com', password: 'x'.repeat(16), csrfToken: 't' },
      unavailable,
    )
    expect(unavailableResult.message).toBe('Desk temporarily unavailable. Try again in a moment.')
    expect(unavailableResult.retryable).toBe(true)
    expect(unavailableResult.message).not.toBe('Invalid credentials.')

    const offline = vi.fn<typeof fetch>().mockRejectedValue(new TypeError('Failed to fetch'))
    expect(
      (
        await staffPasswordLogin(
          'https://api.example.com',
          { email: 'a@b.com', password: 'x'.repeat(16), csrfToken: 't' },
          offline,
        )
      ).message,
    ).toBe('Could not reach the desk. Refresh and try again.')

    const csrfForbidden = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 403,
      json: vi.fn<() => Promise<unknown>>(),
    } as unknown as Response)
    const csrfResult = await staffPasswordLogin(
      'https://api.example.com',
      { email: 'a@b.com', password: 'x'.repeat(16), csrfToken: 't' },
      csrfForbidden,
    )
    expect(csrfResult.message).toBe('Sign-in session expired. Refresh the page and try again.')
    expect(csrfResult.retryable).toBe(true)
    expect(csrfResult.message).not.toContain('Could not reach the desk')
    expect(csrfResult.message).not.toBe('Invalid credentials.')

    vi.useFakeTimers()
    try {
      const hung = vi.fn<typeof fetch>().mockImplementation(
        (_url: string | URL | Request, init?: RequestInit) =>
          new Promise<Response>((_resolve, reject) => {
            init?.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')))
          }),
      )
      const hungPromise = staffPasswordLogin(
        'https://api.example.com',
        { email: 'a@b.com', password: 'x'.repeat(16), csrfToken: 't' },
        hung,
      )
      await vi.advanceTimersByTimeAsync(15_000)
      expect((await hungPromise).message).toBe('Could not reach the desk. Refresh and try again.')
      expect(hung).toHaveBeenCalledWith(
        'https://api.example.com/api/staff/auth/login/',
        expect.objectContaining({ signal: expect.any(AbortSignal) }),
      )
    } finally {
      vi.useRealTimers()
    }
  })

  it('client-side click gate blocks rapid duplicate actions without being the security boundary', () => {
    const gate = createClickGate(1200)

    expect(gate.canRun('staff-login', 10_000)).toBe(true)
    expect(gate.canRun('staff-login', 10_100)).toBe(false)
    expect(gate.isRunning('staff-login')).toBe(true)
    gate.finish('staff-login')
    expect(gate.canRun('staff-login', 10_100)).toBe(false)
    expect(gate.canRun('staff-login', 11_201)).toBe(true)
  })
})

describe('staff login panel', () => {
  it('renders Melis login with Shee mark, providers, reset, and accessibility surfaces', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
    })

    expect(wrapper.find('.staff-login__logo').exists()).toBe(true)
    expect(wrapper.find('.staff-login__logo-mark').exists()).toBe(true)
    expect(wrapper.text()).toMatch(/Welcome back/)
    expect(wrapper.text()).toContain('Continue with Google')
    expect(wrapper.text()).toContain('Continue with Apple')
    expect(wrapper.find('input[type="email"]').attributes('autocomplete')).toBe('username')
    expect(wrapper.find('input[type="password"]').attributes('autocomplete')).toBe('current-password')
    expect(wrapper.find('input[type="password"]').attributes('minlength')).toBe('15')
    expect(wrapper.text()).toContain('Forgot password?')
    expect(wrapper.find('.staff-login__reset').attributes('href')).toBe('/staff/forgot-password')
    expect(wrapper.text()).not.toMatch(/cookie-based|staff-only|shared device|dark mode/i)
  })

  it('always exposes provider start URLs with sanitized next', () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
        nextPath: '/staff/dashboard',
      },
    })

    const links = wrapper.findAll('a.staff-login__provider')
    expect(links).toHaveLength(2)
    const [googleLink, appleLink] = links
    expect(googleLink?.attributes('href')).toContain('/api/staff/auth/google/start/?next=%2Fstaff%2Fdashboard')
    expect(appleLink?.attributes('href')).toContain('/api/staff/auth/apple/start/?next=%2Fstaff%2Fdashboard')
  })

  it('personalizes welcome from typed email local-part', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
    })
    await wrapper.find('input[type="email"]').setValue('amina.k@example.com')
    expect(wrapper.find('#staff-login-title').text()).toBe('Welcome back, Amina')
  })

  it('shows and hides password input without persisting secrets', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
    })

    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('password')
    await wrapper.find('button.staff-login__eye').trigger('click')
    expect(wrapper.find('input[name="password"]').attributes('type')).toBe('text')
    expect(wrapper.find('button.staff-login__eye').attributes('aria-label')).toBe('Hide password')
    expect(storageContainsStaffSecrets(localStorage)).toBe(false)
    expect(storageContainsStaffSecrets(sessionStorage)).toBe(false)
  })

    it('ignores localStorage greet names and uses the typed email', async () => {
    localStorage.setItem('shee.desk.greet', 'Desk')
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: 'csrf-token',
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#staff-login-title').text()).toBe('Welcome back')
    await wrapper.find('input[type="email"]').setValue('amina.k@example.com')
    expect(wrapper.find('#staff-login-title').text()).toBe('Welcome back, Amina')
  })

  it('never maps missing CSRF to invalid credentials and offers retry', async () => {
    const wrapper = mount(StaffLoginPanel, {
      props: {
        apiBaseUrl: 'https://api.example.com',
        csrfToken: '',
      },
    })

    await wrapper.find('form').trigger('submit')
    expect(wrapper.find('.staff-login__status--error').text()).toBe(
      'Desk temporarily unavailable. Try again in a moment.',
    )
    expect(wrapper.find('button.staff-login__retry').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('Invalid credentials.')
  })
})

describe('staff password reset client', () => {
  it('posts reset request and confirm with CSRF and generic messages', async () => {
    const requestFetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: true,
      status: 200,
      json: vi.fn<() => Promise<{ detail: string }>>().mockResolvedValue({ detail: 'ok' }),
    } as unknown as Response)
    const requestResult = await requestStaffPasswordReset(
      'https://api.example.com',
      'beautician@example.com',
      'csrf-token',
      requestFetcher,
    )
    expect(requestResult.ok).toBe(true)
    expect(requestResult.message).toContain('reset instructions')
    expect(requestFetcher).toHaveBeenCalledWith(
      'https://api.example.com/api/staff/auth/password-reset/request/',
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }),
      }),
    )

    const confirmFetcher = vi.fn<typeof fetch>().mockResolvedValue({
      ok: false,
      status: 400,
      json: vi.fn<() => Promise<{ detail: string }>>().mockResolvedValue({ detail: 'raw' }),
    } as unknown as Response)
    const confirmResult = await confirmStaffPasswordReset(
      'https://api.example.com',
      'token-value',
      'Nairobi salon passphrase secure 2026!',
      'csrf-token',
      confirmFetcher,
    )
    expect(confirmResult.ok).toBe(false)
    expect(confirmResult.message).toContain('invalid or expired')
    expect(JSON.stringify(confirmResult)).not.toContain('raw')
  })
})
